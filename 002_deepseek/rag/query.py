from pathlib import Path

from .embeddings import embed_texts


def retrieve_chunks(
    backend: str,
    query: str,
    top_k: int,
    index_path: Path,
    supabase_user_id: str,
) -> list[str]:
    q = (query or "").strip()
    if not q:
        return []
    vecs = embed_texts([q])
    if vecs.size == 0:
        return []
    vec = vecs[0]
    k = max(1, int(top_k))

    if backend == "supabase":
        from .store_supabase import get_client, match_chunks

        return match_chunks(get_client(), vec, k, supabase_user_id)

    from .store_local import search

    return search(index_path, vec, k)
