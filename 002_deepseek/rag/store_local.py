import json
from pathlib import Path

import numpy as np

META_EXT = ".meta.json"


def _faiss():
    import faiss

    return faiss


def _paths(prefix: Path) -> tuple[Path, Path]:
    p = Path(prefix)
    s = str(p)
    if s.endswith(".faiss"):
        faiss_path = p
        base = s[: -len(".faiss")]
        meta_path = Path(base + META_EXT)
    else:
        faiss_path = Path(s + ".faiss")
        meta_path = Path(s + META_EXT)
    return faiss_path, meta_path


def save_index(base_path: Path, vectors: np.ndarray, chunks: list[str]) -> None:
    faiss = _faiss()
    if vectors.size == 0:
        raise ValueError("无向量可写入")
    faiss_path, meta_path = _paths(base_path)
    faiss_path.parent.mkdir(parents=True, exist_ok=True)
    dim = int(vectors.shape[1])
    index = faiss.IndexFlatIP(dim)
    v = vectors.astype(np.float32).copy()
    faiss.normalize_L2(v)
    index.add(v)
    faiss.write_index(index, str(faiss_path))
    meta = {"chunks": chunks, "dim": dim}
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


def load_index(base_path: Path):
    faiss = _faiss()
    faiss_path, meta_path = _paths(base_path)
    if not faiss_path.exists() or not meta_path.exists():
        return None, None
    index = faiss.read_index(str(faiss_path))
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    chunks = meta.get("chunks") or []
    return index, chunks


def search(base_path: Path, query_vec: np.ndarray, top_k: int) -> list[str]:
    faiss = _faiss()
    index, chunks = load_index(base_path)
    if index is None or not chunks:
        return []
    q = query_vec.astype(np.float32).reshape(1, -1).copy()
    faiss.normalize_L2(q)
    k = min(top_k, len(chunks))
    _, indices = index.search(q, k)
    out: list[str] = []
    for idx in indices[0]:
        if 0 <= idx < len(chunks):
            out.append(chunks[idx])
    return out


def count_chunks(base_path: Path) -> int:
    _, chunks = load_index(base_path)
    return len(chunks) if chunks else 0


def index_mtime(base_path: Path) -> float | None:
    faiss_path, meta_path = _paths(base_path)
    if not faiss_path.exists():
        return None
    t = faiss_path.stat().st_mtime
    if meta_path.exists():
        t = max(t, meta_path.stat().st_mtime)
    return t
