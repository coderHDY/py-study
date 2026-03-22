from typing import Any

import numpy as np
from supabase import Client


def _vector_param(vec: np.ndarray) -> str:
    """PostgREST 对 pgvector 列通常需要字符串字面量 '[f,f,...]'，纯 JSON 数组可能被拒。"""
    return "[" + ",".join(f"{float(x):.8g}" for x in vec) + "]"


def get_client() -> Client:
    import os

    from supabase import create_client

    url = os.environ.get("SUPABASE_URL", "").strip()
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    if not url or not key:
        raise RuntimeError("缺少 SUPABASE_URL 或 SUPABASE_SERVICE_ROLE_KEY")
    return create_client(url, key)


def truncate_table(client: Client, table: str) -> None:
    client.rpc("truncate_rag_chunks").execute()


def clear_user_chunks(client: Client, table: str, user_id: str) -> None:
    """删除该用户在表中的全部向量（用于 replace 建库）。"""
    while True:
        r = (
            client.table(table)
            .select("id")
            .eq("user_id", user_id)
            .limit(500)
            .execute()
        )
        rows = r.data or []
        if not rows:
            break
        ids = [row["id"] for row in rows]
        client.table(table).delete().in_("id", ids).execute()


def insert_chunks(
    client: Client,
    table: str,
    user_id: str,
    contents: list[str],
    embeddings: np.ndarray,
    metadatas: list[dict[str, Any]] | None = None,
) -> None:
    from postgrest.exceptions import APIError

    def build_rows(embedding_fmt: str) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for i, text in enumerate(contents):
            vec = embeddings[i]
            if embedding_fmt == "str":
                emb_val: Any = _vector_param(vec)
            else:
                emb_val = [float(x) for x in vec]
            md: dict[str, Any] = metadatas[i] if metadatas and i < len(metadatas) else {}
            out.append(
                {
                    "user_id": user_id,
                    "content": text,
                    "embedding": emb_val,
                    "metadata": md,
                }
            )
        return out

    batch = 100
    for fmt in ("str", "list"):
        try:
            rows = build_rows(fmt)
            for i in range(0, len(rows), batch):
                client.table(table).insert(rows[i : i + batch]).execute()
            return
        except APIError as e:
            if fmt == "list":
                raise


def match_chunks(
    client: Client,
    query_embedding: np.ndarray,
    match_count: int,
    filter_user_id: str,
) -> list[str]:
    q = query_embedding.astype(float)
    r = client.rpc(
        "match_rag_chunks",
        {
            "query_embedding": q.tolist(),
            "match_count": match_count,
            "filter_user_id": filter_user_id,
        },
    ).execute()
    data = r.data or []
    return [row.get("content", "") for row in data if row.get("content")]


def count_rows(client: Client, table: str, user_id: str) -> int:
    r = (
        client.table(table)
        .select("id", count="exact")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    c = getattr(r, "count", None)
    return int(c) if c is not None else 0
