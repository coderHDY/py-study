import os
from functools import lru_cache
from typing import Literal

import numpy as np

EmbeddingBackend = Literal["local", "openai"]


def embedding_dim() -> int:
    backend = _backend_name()
    if backend == "openai":
        return int(os.environ.get("EMBEDDING_DIM", "1536"))
    return 384


def _backend_name() -> str:
    b = (os.environ.get("EMBEDDING_BACKEND") or "local").strip().lower()
    return "openai" if b == "openai" else "local"


@lru_cache(maxsize=1)
def _local_model():
    from sentence_transformers import SentenceTransformer

    name = os.environ.get("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    return SentenceTransformer(name)


def _openai_client():
    from openai import OpenAI

    key = os.environ.get("EMBEDDING_API_KEY") or os.environ.get("OPENAI_API_KEY")
    base = os.environ.get("EMBEDDING_BASE_URL", "https://api.openai.com/v1")
    return OpenAI(api_key=key, base_url=base)


def embed_texts(texts: list[str]) -> np.ndarray:
    if not texts:
        return np.array([], dtype=np.float32).reshape(0, embedding_dim())

    backend = _backend_name()
    if backend == "openai":
        client = _openai_client()
        model = os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small")
        vecs = []
        batch = 32
        for i in range(0, len(texts), batch):
            part = texts[i : i + batch]
            r = client.embeddings.create(model=model, input=part)
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
