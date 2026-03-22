"""
全局配置 + 按 user_id 隔离的会话（Supabase）。
需设置 SESSIONS_BACKEND=supabase 且配置 SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY。
"""
from __future__ import annotations

import json
from typing import Any

TABLE_CONFIG = "pumpkin_app_config"
TABLE_SESSIONS = "pumpkin_sessions"


def _client():
    from rag.store_supabase import get_client

    return get_client()


def fetch_global_config() -> dict[str, Any]:
    c = _client()
    r = c.table(TABLE_CONFIG).select("config").eq("id", "default").limit(1).execute()
    rows = r.data or []
    if not rows:
        default_cfg = {
            "name": "南瓜小助手",
            "personality": "You are a helpful assistant. 你是一个友好的AI南瓜智能伴侣。",
        }
        c.table(TABLE_CONFIG).upsert(
            {"id": "default", "config": default_cfg},
            on_conflict="id",
        ).execute()
        return dict(default_cfg)
    cfg = rows[0].get("config") or {}
    if isinstance(cfg, str):
        cfg = json.loads(cfg)
    return dict(cfg)


def save_global_config(config: dict[str, Any]) -> None:
    c = _client()
    c.table(TABLE_CONFIG).upsert({"id": "default", "config": config}, on_conflict="id").execute()


def list_user_sessions(user_id: str) -> dict[str, dict[str, Any]]:
    c = _client()
    r = (
        c.table(TABLE_SESSIONS)
        .select("id, title, messages")
        .eq("user_id", user_id)
        .order("updated_at", desc=True)
        .execute()
    )
    out: dict[str, dict[str, Any]] = {}
    for row in r.data or []:
        sid = row["id"]
        msgs = row.get("messages")
        if not isinstance(msgs, list):
            msgs = []
        out[sid] = {"title": row.get("title", "新会话"), "messages": msgs}
    return out


def get_user_session(user_id: str, sid: str) -> dict[str, Any] | None:
    c = _client()
    r = (
        c.table(TABLE_SESSIONS)
        .select("id, title, messages")
        .eq("user_id", user_id)
        .eq("id", sid)
        .limit(1)
        .execute()
    )
    rows = r.data or []
    if not rows:
        return None
    row = rows[0]
    msgs = row.get("messages")
    if not isinstance(msgs, list):
        msgs = []
    return {"title": row.get("title", "新会话"), "messages": msgs}


def create_user_session(user_id: str, sid: str) -> None:
    c = _client()
    c.table(TABLE_SESSIONS).insert(
        {"user_id": user_id, "id": sid, "title": "新会话", "messages": []}
    ).execute()


def delete_user_session(user_id: str, sid: str) -> None:
    c = _client()
    c.table(TABLE_SESSIONS).delete().eq("user_id", user_id).eq("id", sid).execute()


def save_user_session(user_id: str, sid: str, title: str, messages: list[dict[str, Any]]) -> None:
    c = _client()
    c.table(TABLE_SESSIONS).upsert(
        {"user_id": user_id, "id": sid, "title": title, "messages": messages},
        on_conflict="user_id,id",
    ).execute()
