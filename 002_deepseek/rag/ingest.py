from pathlib import Path

from .chunking import chunk_text
from .embeddings import embed_texts


def texts_to_chunks(texts: list[str], chunk_size: int, chunk_overlap: int) -> list[str]:
    out: list[str] = []
    for t in texts:
        out.extend(chunk_text(t, chunk_size, chunk_overlap))
    return out


def ingest_to_local(prefix_path: Path, texts: list[str], chunk_size: int, chunk_overlap: int) -> int:
    from .store_local import save_index

    chunks = texts_to_chunks(texts, chunk_size, chunk_overlap)
    if not chunks:
        return 0
    embs = embed_texts(chunks)
    save_index(prefix_path, embs, chunks)
    return len(chunks)


def ingest_to_supabase(
    table: str,
    texts: list[str],
    chunk_size: int,
    chunk_overlap: int,
    replace: bool,
    user_id: str,
) -> int:
    from . import store_supabase

    chunks = texts_to_chunks(texts, chunk_size, chunk_overlap)
    if not chunks:
        return 0
    embs = embed_texts(chunks)
    client = store_supabase.get_client()
    if replace:
        store_supabase.clear_user_chunks(client, table, user_id)
    store_supabase.insert_chunks(client, table, user_id, chunks, embs)
    return len(chunks)
