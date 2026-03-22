"""
嵌入方式：
- local：sentence-transformers（默认 all-MiniLM-L6-v2 为 384 维，会零填充到 EMBEDDING_DIM，默认 512，与 Supabase 一致）
- openai：OpenAI 兼容 HTTP（含百炼 compatible-mode / OpenAI 官方）
- dashscope_multimodal：百炼原生 SDK（MultiModalEmbedding）

默认逻辑维数 EMBEDDING_DIM=512（与 supabase_*.sql 中 vector(512) 一致）；未设置环境变量时本地与 Vercel 均按 512。

百炼 text-embedding-v3/v4 的 dimensions 仅允许离散取值；与意图维不一致时会先按合法维请求，再截断/填充到 EMBEDDING_DIM。

百炼兼容示例：
  DASHSCOPE_API_KEY=...
  EMBEDDING_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
  EMBEDDING_MODEL=text-embedding-v4

国际域：compatible-mode 使用 dashscope-intl 域名；可设 DASHSCOPE_REGION=intl。
"""
import os
from functools import lru_cache
from typing import Literal

import numpy as np

EmbeddingBackend = Literal["local", "openai", "dashscope_mm"]

_DASHSCOPE_CN = "https://dashscope.aliyuncs.com/compatible-mode/v1"
_DASHSCOPE_INTL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"

# 百炼 OpenAI 兼容嵌入 v3/v4：parameters.dimension 仅允许下列取值（官方报错枚举）
_DASHSCOPE_COMPATIBLE_VALID_DIMS = (64, 128, 256, 512, 768, 1024, 1536, 2048, 3072)


def _using_dashscope_compatible_embedding_api() -> bool:
    return "dashscope" in _resolve_embedding_api_base().lower()


def _snap_dashscope_compatible_dimension(d: int) -> int:
    if d in _DASHSCOPE_COMPATIBLE_VALID_DIMS:
        return d
    ge = [x for x in _DASHSCOPE_COMPATIBLE_VALID_DIMS if x >= d]
    if ge:
        return min(ge)
    return max(_DASHSCOPE_COMPATIBLE_VALID_DIMS)


def _dashscope_compatible_base() -> str:
    r = os.environ.get("DASHSCOPE_REGION", "cn").strip().lower()
    if r in ("intl", "international", "sg", "singapore", "sea"):
        return _DASHSCOPE_INTL
    return _DASHSCOPE_CN


def _resolve_embedding_api_base() -> str:
    explicit = os.environ.get("EMBEDDING_BASE_URL", "").strip()
    if explicit:
        return explicit
    prov = os.environ.get("EMBEDDING_PROVIDER", "").strip().lower()
    if prov in ("dashscope", "bailian", "aliyun"):
        return _dashscope_compatible_base()
    model = os.environ.get("EMBEDDING_MODEL", "").strip().lower()
    if model.startswith("text-embedding-v"):
        return _dashscope_compatible_base()
    emb = os.environ.get("EMBEDDING_API_KEY", "").strip()
    ds = os.environ.get("DASHSCOPE_API_KEY", "").strip()
    if ds and not emb:
        return _dashscope_compatible_base()
    return "https://api.openai.com/v1"


def _default_embedding_model_for_api() -> str:
    """未设置 EMBEDDING_MODEL 时：百炼无 OpenAI 模型名，默认 text-embedding-v4。"""
    if "dashscope" in _resolve_embedding_api_base().lower():
        return "text-embedding-v4"
    return "text-embedding-3-small"


def _openai_embedding_desired_dim() -> int:
    """写入库表/逻辑维度的意图值（未做百炼合法维 snap）。"""
    raw = os.environ.get("EMBEDDING_DIM")
    if raw is not None and str(raw).strip() != "":
        return int(str(raw).strip())
    return 512


def _openai_compatible_api_dimensions_param() -> int:
    """发给 embeddings.create 的 dimensions（百炼须为合法枚举之一）。"""
    desired = _openai_embedding_desired_dim()
    if _using_dashscope_compatible_embedding_api():
        return _snap_dashscope_compatible_dimension(desired)
    return desired


def _resize_embedding_rows(arr: np.ndarray, target_cols: int) -> np.ndarray:
    """将每行变为 target_cols：不足则右侧零填充，超出则截断前段，再整行 L2 归一。"""
    n, d = arr.shape
    base = np.asarray(arr, dtype=np.float32)
    if d < target_cols:
        out = np.hstack([base, np.zeros((n, target_cols - d), dtype=np.float32)])
    elif d > target_cols:
        out = np.asarray(base[:, :target_cols], dtype=np.float32)
    else:
        out = base
    norms = np.linalg.norm(out, axis=1, keepdims=True)
    return out / np.maximum(norms, 1e-12)


def embedding_dim() -> int:
    backend = _backend_name()
    if backend == "dashscope_mm":
        raw = os.environ.get("EMBEDDING_DIM")
        if raw is not None and str(raw).strip() != "":
            return int(str(raw).strip())
        return 512
    if backend == "openai":
        desired = _openai_embedding_desired_dim()
        if _using_dashscope_compatible_embedding_api():
            out = os.environ.get("EMBEDDING_OUTPUT_DIM", "").strip()
            if out:
                return int(out)
            snapped = _snap_dashscope_compatible_dimension(desired)
            if snapped > desired:
                return desired
            return snapped
        return desired
    raw = os.environ.get("EMBEDDING_DIM")
    if raw is not None and str(raw).strip() != "":
        return int(str(raw).strip())
    return 512


def _backend_name() -> str:
    raw = os.environ.get("EMBEDDING_BACKEND")
    if raw is not None and str(raw).strip() != "":
        r = str(raw).strip().lower()
        if r in ("dashscope_multimodal", "dashscope_mm", "multimodal"):
            return "dashscope_mm"
        return "openai" if r == "openai" else "local"
    model = os.environ.get("EMBEDDING_MODEL", "").strip().lower()
    if "tongyi-embedding-vision" in model or "embedding-vision-flash" in model:
        return "dashscope_mm"
    # 云端镜像不含 sentence-transformers / torch，未配置时默认走 API 嵌入
    if os.environ.get("VERCEL"):
        return "openai"
    return "local"


@lru_cache(maxsize=1)
def _local_model():
    from sentence_transformers import SentenceTransformer

    name = os.environ.get("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    return SentenceTransformer(name)


def _openai_client():
    from openai import OpenAI

    key = _dashscope_api_key()
    base = _resolve_embedding_api_base()
    return OpenAI(api_key=key, base_url=base)


def _dashscope_api_key() -> str:
    return (
        os.environ.get("EMBEDDING_API_KEY", "").strip()
        or os.environ.get("DASHSCOPE_API_KEY", "").strip()
        or os.environ.get("OPENAI_API_KEY", "").strip()
    )


def _parse_multimodal_embedding_output(output) -> list[list[float]]:
    """解析 MultiModalEmbedding 返回的 output（兼容 output / result.embeddings）。"""
    if output is None:
        raise ValueError("DashScope MultiModalEmbedding 返回空 output")
    data = output if isinstance(output, dict) else {}
    embs = data.get("embeddings")
    if embs is None:
        res = data.get("result")
        if isinstance(res, dict):
            embs = res.get("embeddings")
    if not embs:
        raise ValueError(
            "无法在 MultiModalEmbedding 响应中解析 embeddings，"
            f"keys={list(data.keys()) if isinstance(data, dict) else type(output)}"
        )
    rows: list[tuple[int, list[float]]] = []
    for i, item in enumerate(embs):
        if isinstance(item, dict):
            idx = int(item.get("index", i))
            vec = item.get("embedding")
            if vec is None:
                continue
            rows.append((idx, [float(x) for x in vec]))
        elif isinstance(item, (list, tuple)):
            rows.append((i, [float(x) for x in item]))
    if not rows:
        raise ValueError("embeddings 列表为空或格式无法识别")
    rows.sort(key=lambda x: x[0])
    return [r[1] for r in rows]


def _embed_texts_dashscope_multimodal(texts: list[str]) -> np.ndarray:
    from http import HTTPStatus

    import dashscope
    from dashscope import MultiModalEmbedding

    key = _dashscope_api_key()
    if not key:
        raise ValueError("使用多模态嵌入需要配置 DASHSCOPE_API_KEY 或 EMBEDDING_API_KEY")

    model = os.environ.get("EMBEDDING_MODEL", "").strip()
    if not model:
        model = "tongyi-embedding-vision-flash-2026-03-06"

    dashscope.api_key = key
    batch = max(1, int(os.environ.get("MULTIMODAL_EMBED_BATCH", "8")))

    all_vecs: list[np.ndarray] = []
    for i in range(0, len(texts), batch):
        part = texts[i : i + batch]
        contents: list[dict] = []
        for t in part:
            elem: dict = {"text": t}
            elem.setdefault("factor", 1.0)
            contents.append(elem)
        resp = MultiModalEmbedding.call(model=model, input=contents, api_key=key)
        if resp.status_code != HTTPStatus.OK:
            raise RuntimeError(
                "DashScope MultiModalEmbedding 失败: "
                f"{resp.code} {resp.message} request_id={getattr(resp, 'request_id', '')}"
            )
        out = getattr(resp, "output", None)
        parsed = _parse_multimodal_embedding_output(out)
        if len(parsed) != len(part):
            raise RuntimeError(
                f"嵌入条数不一致：请求 {len(part)} 条，返回 {len(parsed)} 条"
            )
        for row in parsed:
            all_vecs.append(np.asarray(row, dtype=np.float32))
    arr = np.stack(all_vecs, axis=0)
    return _resize_embedding_rows(arr, embedding_dim())


def _embeddings_api_supports_dimensions(model: str) -> bool:
    """OpenAI text-embedding-3* 与百炼 text-embedding-v3/v4 等支持 dimensions。"""
    m = str(model).lower()
    if m.startswith("text-embedding-3"):
        return True
    if m.startswith("text-embedding-v3") or m.startswith("text-embedding-v4"):
        return True
    return False


def embed_texts(texts: list[str]) -> np.ndarray:
    if not texts:
        return np.array([], dtype=np.float32).reshape(0, embedding_dim())

    backend = _backend_name()
    if backend == "dashscope_mm":
        return _embed_texts_dashscope_multimodal(texts)
    if backend == "openai":
        client = _openai_client()
        model = os.environ.get("EMBEDDING_MODEL", "").strip() or _default_embedding_model_for_api()
        vecs = []
        batch = 32
        api_dim = _openai_compatible_api_dimensions_param()
        logical_dim = embedding_dim()
        for i in range(0, len(texts), batch):
            part = texts[i : i + batch]
            kwargs: dict = {"model": model, "input": part}
            if _embeddings_api_supports_dimensions(model) and api_dim > 0:
                kwargs["dimensions"] = api_dim
            r = client.embeddings.create(**kwargs)
            order = {item.index: np.array(item.embedding, dtype=np.float32) for item in r.data}
            vecs.extend(order[j] for j in range(len(part)))
        arr = np.stack(vecs, axis=0)
        return _resize_embedding_rows(arr, logical_dim)

    model = _local_model()
    arr = model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=False,
        normalize_embeddings=True,
    )
    return _resize_embedding_rows(np.asarray(arr, dtype=np.float32), embedding_dim())
