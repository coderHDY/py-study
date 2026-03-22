"""
嵌入：本地 sentence-transformers，或任意 OpenAI 兼容 Embeddings API（含阿里云百炼 compatible-mode）。

百炼示例（北京地域）：
  EMBEDDING_API_KEY 或 DASHSCOPE_API_KEY=<DashScope API Key>
  EMBEDDING_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
  EMBEDDING_MODEL=text-embedding-v4
  EMBEDDING_DIM=384   # 与库表 vector(384) 一致；v3/v4 支持 dimensions 参数

国际域可将 BASE_URL 换为 https://dashscope-intl.aliyuncs.com/compatible-mode/v1
可选 DASHSCOPE_REGION=intl（或 sg）使用国际域；勿把百炼 Key 只写在 OPENAI_API_KEY 却不设 BASE_URL，否则会误请求 OpenAI 官方而 401。
"""
import os
from functools import lru_cache
from typing import Literal

import numpy as np

EmbeddingBackend = Literal["local", "openai"]

_DASHSCOPE_CN = "https://dashscope.aliyuncs.com/compatible-mode/v1"
_DASHSCOPE_INTL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"


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


def embedding_dim() -> int:
    backend = _backend_name()
    if backend == "openai":
        raw = os.environ.get("EMBEDDING_DIM")
        if raw is not None and str(raw).strip() != "":
            return int(str(raw).strip())
        # 与 supabase_multiuser.sql 中 vector(384) 对齐；本地显式 openai 未设时仍用 1536
        if os.environ.get("VERCEL"):
            return 384
        return 1536
    return 384


def _backend_name() -> str:
    raw = os.environ.get("EMBEDDING_BACKEND")
    if raw is not None and str(raw).strip() != "":
        return "openai" if str(raw).strip().lower() == "openai" else "local"
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

    emb = os.environ.get("EMBEDDING_API_KEY", "").strip()
    ds = os.environ.get("DASHSCOPE_API_KEY", "").strip()
    oa = os.environ.get("OPENAI_API_KEY", "").strip()
    if emb:
        key = emb
    elif ds:
        key = ds
    else:
        key = oa
    base = _resolve_embedding_api_base()
    return OpenAI(api_key=key, base_url=base)


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
    if backend == "openai":
        client = _openai_client()
        model = os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small")
        vecs = []
        batch = 32
        dim = embedding_dim()
        for i in range(0, len(texts), batch):
            part = texts[i : i + batch]
            kwargs: dict = {"model": model, "input": part}
            if _embeddings_api_supports_dimensions(model) and dim > 0:
                kwargs["dimensions"] = dim
            r = client.embeddings.create(**kwargs)
            order = {item.index: np.array(item.embedding, dtype=np.float32) for item in r.data}
            vecs.extend(order[j] for j in range(len(part)))
        return np.stack(vecs, axis=0)

    model = _local_model()
    arr = model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=False,
        normalize_embeddings=True,
    )
    return np.asarray(arr, dtype=np.float32)
