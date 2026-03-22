"""
AI 南瓜智能伴侣 - 后端 API
"""
import os
import re
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:
    pass

from flask import (
    Flask,
    abort,
    jsonify,
    make_response,
    request,
    send_from_directory,
    Response,
    stream_with_context,
    current_app,
)
from flask_cors import CORS
from openai import OpenAI
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder="static")
CORS(app, allow_headers=["Content-Type", "Authorization", "X-Client-User-Id"])

CLIENT_USER_ID_HEADER = "X-Client-User-Id"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

# Vercel 文件系统只有 /tmp 可写；本地使用 data/ 目录
DATA_DIR = Path("/tmp") if os.environ.get("VERCEL") else Path(__file__).parent / "data"
SESSIONS_FILE = DATA_DIR / "sessions.json"

# RAG 切块/检索/表名/本地索引目录名仅在后端维护（前端与持久化 config 均不暴露）
DEFAULT_RAG_INDEX = "pumpkin_index"
RAG_CHUNK_SIZE = 500
RAG_CHUNK_OVERLAP = 80
RAG_TOP_K = 4
RAG_SUPABASE_TABLE = "rag_chunks"


def sanitize_index_path(name: str) -> str:
    name = (name or "").strip()
    if not name:
        return DEFAULT_RAG_INDEX
    if ".." in name or "/" in name or "\\" in name:
        return DEFAULT_RAG_INDEX
    if not re.match(r"^[a-zA-Z0-9_.-]+$", name):
        return DEFAULT_RAG_INDEX
    return name[:120]


def merge_rag_config(config: dict) -> dict:
    """运行时注入固定 RAG 路径；持久化层不保存 rag（见 persistable_config）。"""
    cfg = dict(config)
    cfg["rag"] = {"index_path": DEFAULT_RAG_INDEX}
    return cfg


def persistable_config(config: dict) -> dict:
    """写入文件/数据库的配置：不含 rag，避免多余字段。"""
    return {k: v for k, v in config.items() if k != "rag"}


def rag_backend_for_api(internal: str | None) -> str:
    if internal == "supabase":
        return "cloud"
    if internal == "local":
        return "local"
    return "invalid"


def sessions_storage_for_api() -> str:
    return "cloud" if use_supabase_sessions() else "file"


def rag_index_prefix_path(index_path: str, client_user_id: str | None = None) -> Path:
    base = sanitize_index_path(index_path)
    if client_user_id and re.match(r"^[a-zA-Z0-9_-]{8,128}$", client_user_id):
        safe_u = re.sub(r"[^a-zA-Z0-9_-]", "", client_user_id)[:128]
        return (DATA_DIR / "rag" / safe_u / base).resolve()
    return (DATA_DIR / "rag" / base).resolve()


def rag_sources_dir() -> Path:
    p = (DATA_DIR / "rag" / "sources").resolve()
    p.mkdir(parents=True, exist_ok=True)
    return p


def _rag_dependency_error_message(exc: BaseException) -> str:
    if isinstance(exc, ModuleNotFoundError) and getattr(exc, "name", None):
        name = exc.name
        if name in ("faiss", "sentence_transformers", "torch"):
            return (
                f"缺少 Python 依赖「{name}」。本地 FAISS/嵌入模型请执行：pip install -r requirements-local.txt。"
                "若在 Vercel 部署，请使用云端知识库并设置 EMBEDDING_BACKEND=openai（勿安装 torch 系大包）。"
            )
        return (
            f"缺少 Python 依赖「{name}」。请执行：pip install -r requirements.txt，"
            "或使用：.venv/bin/pip install -r requirements.txt"
        )
    return str(exc)


def _supabase_error_message(exc: BaseException) -> str:
    try:
        from postgrest.exceptions import APIError

        if isinstance(exc, APIError):
            parts = [p for p in (exc.message, exc.details, exc.hint) if p]
            base = "云端存储: " + (" | ".join(parts) if parts else repr(exc))
            msg = (exc.message or "").lower()
            if "row-level security" in msg or exc.code == "42501":
                base += (
                    " — 说明：服务端应使用具有完整数据权限的密钥（勿使用公开/匿名密钥）；"
                    "密钥仅放在服务器环境变量中，勿暴露到前端。"
                )
            return base
    except ImportError:
        pass
    return str(exc) or repr(exc)


def resolve_rag_backend():
    explicit = os.environ.get("RAG_BACKEND", "").strip().lower()
    has_sb = bool(
        os.environ.get("SUPABASE_URL", "").strip()
        and os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    )
    if explicit == "supabase":
        if has_sb:
            return "supabase", None
        return None, "已启用云端知识库但未配置云服务地址或服务端密钥"
    if explicit == "local":
        return "local", None
    if os.environ.get("VERCEL") and has_sb:
        return "supabase", None
    return "local", None


def _supabase_credentials_ok() -> bool:
    return bool(
        os.environ.get("SUPABASE_URL", "").strip()
        and os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    )


def use_supabase_sessions() -> bool:
    """需环境变量 SESSIONS_BACKEND=supabase 且已配置 Supabase 密钥。"""
    return os.environ.get("SESSIONS_BACKEND", "").strip().lower() == "supabase" and _supabase_credentials_ok()


def get_valid_client_user_id() -> str | None:
    uid = request.headers.get(CLIENT_USER_ID_HEADER, "").strip()
    if uid and re.match(r"^[a-zA-Z0-9_-]{8,128}$", uid):
        return uid
    return None


def require_client_user_id() -> str:
    uid = get_valid_client_user_id()
    if not uid:
        abort(
            make_response(
                jsonify({"error": f"缺少或非法请求头 {CLIENT_USER_ID_HEADER}（浏览器应写入 localStorage 并随请求发送）"}),
                400,
            )
        )
    return uid


def load_data():
    """加载 sessions.json"""
    if not SESSIONS_FILE.exists():
        return {
            "sessions": {},
            "config": {
                "name": "南瓜小助手",
                "personality": "You are a helpful assistant. 你是一个友好的AI南瓜智能伴侣。",
            },
        }
    with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    """保存 sessions.json"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_client():
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")


# ============ API 路由 ============


@app.route("/api/sessions", methods=["GET"])
def list_sessions():
    """获取所有会话列表"""
    if use_supabase_sessions():
        import session_store_supabase as ssb

        uid = require_client_user_id()
        sessions = ssb.list_user_sessions(uid)
        return jsonify({
            "sessions": [
                {"id": sid, "title": s.get("title", "新会话"), "messages": s.get("messages", [])}
                for sid, s in sessions.items()
            ]
        })
    data = load_data()
    sessions = data.get("sessions", {})
    return jsonify({
        "sessions": [
            {"id": sid, "title": s.get("title", "新会话"), "messages": s.get("messages", [])}
            for sid, s in sessions.items()
        ]
    })


@app.route("/api/sessions", methods=["POST"])
def create_session():
    """新建会话"""
    if use_supabase_sessions():
        import session_store_supabase as ssb

        uid = require_client_user_id()
        sid = str(uuid.uuid4())[:8]
        ssb.create_user_session(uid, sid)
        return jsonify({"id": sid, "title": "新会话", "messages": []})
    data = load_data()
    sid = str(uuid.uuid4())[:8]
    data["sessions"][sid] = {"messages": [], "title": "新会话"}
    save_data(data)
    return jsonify({"id": sid, "title": "新会话", "messages": []})


@app.route("/api/sessions/<sid>", methods=["GET"])
def get_session(sid):
    """获取单个会话"""
    if use_supabase_sessions():
        import session_store_supabase as ssb

        uid = require_client_user_id()
        s = ssb.get_user_session(uid, sid)
        if s is None:
            return jsonify({"error": "会话不存在"}), 404
        return jsonify({"id": sid, "title": s.get("title", "新会话"), "messages": s.get("messages", [])})
    data = load_data()
    if sid not in data.get("sessions", {}):
        return jsonify({"error": "会话不存在"}), 404
    s = data["sessions"][sid]
    return jsonify({"id": sid, "title": s.get("title", "新会话"), "messages": s.get("messages", [])})


@app.route("/api/sessions/<sid>", methods=["DELETE"])
def delete_session(sid):
    """删除会话"""
    if use_supabase_sessions():
        import session_store_supabase as ssb

        uid = require_client_user_id()
        if ssb.get_user_session(uid, sid) is None:
            return jsonify({"error": "会话不存在"}), 404
        ssb.delete_user_session(uid, sid)
        return jsonify({"ok": True})
    data = load_data()
    if sid not in data.get("sessions", {}):
        return jsonify({"error": "会话不存在"}), 404
    del data["sessions"][sid]
    save_data(data)
    return jsonify({"ok": True})


@app.route("/api/config", methods=["GET"])
def get_config():
    """获取配置"""
    if use_supabase_sessions():
        import session_store_supabase as ssb

        require_client_user_id()
        cfg = merge_rag_config(ssb.fetch_global_config())
    else:
        data = load_data()
        cfg = merge_rag_config(data.get("config", {}))
    backend, err = resolve_rag_backend()
    out = dict(cfg)
    out.pop("rag", None)
    out["rag_runtime"] = {"backend": rag_backend_for_api(backend), "error": err}
    out["sessions_storage"] = sessions_storage_for_api()
    return jsonify(out)


@app.route("/api/config", methods=["PUT"])
def update_config():
    """更新配置（名字/性格/RAG）"""
    body = request.get_json() or {}
    if use_supabase_sessions():
        import session_store_supabase as ssb

        require_client_user_id()
        config = merge_rag_config(ssb.fetch_global_config())
        if "name" in body:
            config["name"] = body["name"]
        if "personality" in body:
            config["personality"] = body["personality"]
        ssb.save_global_config(persistable_config(config))
    else:
        data = load_data()
        config = merge_rag_config(data.get("config", {}))
        if "name" in body:
            config["name"] = body["name"]
        if "personality" in body:
            config["personality"] = body["personality"]
        data["config"] = persistable_config(config)
        save_data(data)
    out = dict(merge_rag_config(config))
    out.pop("rag", None)
    backend, err = resolve_rag_backend()
    out["rag_runtime"] = {"backend": rag_backend_for_api(backend), "error": err}
    out["sessions_storage"] = sessions_storage_for_api()
    return jsonify(out)


@app.route("/api/rag/status", methods=["GET"])
def rag_status():
    backend, err = resolve_rag_backend()
    if use_supabase_sessions():
        import session_store_supabase as ssb

        require_client_user_id()
        cfg_src = ssb.fetch_global_config()
    else:
        cfg_src = load_data().get("config", {})
    cfg = merge_rag_config(cfg_src)
    rag = cfg["rag"]
    out = {
        "backend": rag_backend_for_api(backend),
        "error": err,
        "chunk_count": 0,
        "updated_at": None,
    }
    if err or not backend:
        return jsonify(out)
    try:
        cuid = get_valid_client_user_id()
        if backend == "local":
            from rag.store_local import count_chunks, index_mtime

            path = rag_index_prefix_path(rag["index_path"], cuid)
            out["chunk_count"] = count_chunks(path)
            t = index_mtime(path)
            if t:
                out["updated_at"] = datetime.fromtimestamp(t, tz=timezone.utc).isoformat()
        else:
            if not cuid:
                out["error"] = f"云端知识库需要请求头 {CLIENT_USER_ID_HEADER}"
                return jsonify(out)
            from rag.store_supabase import get_client, count_rows

            client = get_client()
            out["chunk_count"] = count_rows(client, RAG_SUPABASE_TABLE, cuid)
    except Exception as e:
        out["error"] = str(e)
    return jsonify(out)


@app.route("/api/rag/ingest", methods=["POST"])
def rag_ingest():
    backend, err = resolve_rag_backend()
    if err or not backend:
        return jsonify({"error": err or "知识库暂不可用"}), 400

    texts: list[str] = []
    replace = True
    if request.content_type and "multipart/form-data" in request.content_type:
        replace = request.form.get("replace", "true").lower() in ("1", "true", "yes")
        for f in request.files.getlist("files"):
            if not f or not f.filename:
                continue
            safe = secure_filename(f.filename)
            if not safe:
                suf = Path(f.filename).suffix.lower()
                if suf not in (".txt", ".md"):
                    suf = ".txt"
                safe = f"upload_{uuid.uuid4().hex[:12]}{suf}"
            if not safe.lower().endswith((".txt", ".md")):
                continue
            raw = f.read()
            try:
                texts.append(raw.decode("utf-8"))
            except UnicodeDecodeError:
                texts.append(raw.decode("utf-8", errors="replace"))
    else:
        body = request.get_json(silent=True) or {}
        replace = bool(body.get("replace", True))
        if body.get("text"):
            texts.append(str(body["text"]))
        rel = body.get("source_path")
        if rel and not os.environ.get("VERCEL"):
            base = rag_sources_dir()
            name_only = secure_filename(Path(str(rel)).name)
            target = (base / name_only).resolve()
            if str(target).startswith(str(base)) and target.is_file():
                texts.append(target.read_text(encoding="utf-8", errors="replace"))

    if not texts:
        return jsonify({"error": "未提供可索引的文本（上传 .txt/.md 或使用 JSON text / source_path）"}), 400

    if use_supabase_sessions():
        import session_store_supabase as ssb

        require_client_user_id()
        cfg_src = ssb.fetch_global_config()
    else:
        cfg_src = load_data().get("config", {})
    cfg = merge_rag_config(cfg_src)
    rag = cfg["rag"]

    try:
        if backend == "local":
            from rag.ingest import ingest_to_local

            n = ingest_to_local(
                rag_index_prefix_path(rag["index_path"], get_valid_client_user_id()),
                texts,
                RAG_CHUNK_SIZE,
                RAG_CHUNK_OVERLAP,
            )
        else:
            from rag.ingest import ingest_to_supabase

            sb_uid = require_client_user_id()
            n = ingest_to_supabase(
                RAG_SUPABASE_TABLE,
                texts,
                RAG_CHUNK_SIZE,
                RAG_CHUNK_OVERLAP,
                replace,
                sb_uid,
            )
    except ModuleNotFoundError as e:
        return jsonify({"error": _rag_dependency_error_message(e)}), 503
    except Exception as e:
        current_app.logger.exception("rag_ingest failed")
        return jsonify({"error": _supabase_error_message(e)}), 500

    return jsonify({"ok": True, "chunks": n})


@app.route("/api/chat", methods=["POST"])
def chat():
    """发送消息并流式返回 DeepSeek 响应"""
    body = request.get_json() or {}
    sid = body.get("session_id")
    content = body.get("content", "").strip()
    use_rag = bool(body.get("use_rag"))

    if not sid or not content:
        return jsonify({"error": "缺少 session_id 或 content"}), 400

    use_sb_sess = use_supabase_sessions()
    chat_uid: str | None = None
    if use_sb_sess:
        import session_store_supabase as ssb

        chat_uid = require_client_user_id()
        sess_row = ssb.get_user_session(chat_uid, sid)
        if sess_row is None:
            return jsonify({"error": "会话不存在"}), 404
        history = sess_row.get("messages", [])
        config = merge_rag_config(ssb.fetch_global_config())
    else:
        data = load_data()
        if sid not in data.get("sessions", {}):
            return jsonify({"error": "会话不存在"}), 404
        config = merge_rag_config(data.get("config", {}))
        history = data["sessions"][sid].get("messages", [])

    name = config.get("name", "南瓜小助手")
    personality = config.get("personality", "You are a helpful assistant.")
    system_content = f"你的名字是 {name}。{personality}"

    user_message_for_model = content
    rag_meta = None
    if use_rag:
        rag_meta = {"hits": 0}
        backend, rerr = resolve_rag_backend()
        if not backend or rerr:
            rag_meta["error"] = rerr or "知识库暂不可用"
        else:
            if use_sb_sess:
                rc_uid = chat_uid
            elif backend == "supabase":
                rc_uid = require_client_user_id()
            else:
                rc_uid = get_valid_client_user_id()
            try:
                from rag.query import retrieve_chunks

                rag = config["rag"]
                chunks = retrieve_chunks(
                    backend,
                    content,
                    RAG_TOP_K,
                    rag_index_prefix_path(rag["index_path"], rc_uid),
                    rc_uid if backend == "supabase" else "",
                )
                rag_meta["hits"] = len(chunks)
                if chunks:
                    ctx = "\n\n".join(f"[{i + 1}] {c}" for i, c in enumerate(chunks))
                    user_message_for_model = (
                        "以下是可能相关的参考片段，请结合参考作答；若与问题无关可忽略。\n\n"
                        f"{ctx}\n\n---\n用户问题：\n{content}"
                    )
            except Exception as e:
                current_app.logger.exception("RAG retrieve failed")
                rag_meta["error"] = str(e)
                rag_meta["hits"] = 0

    api_messages = [{"role": "system", "content": system_content}]
    for m in history:
        api_messages.append({"role": m["role"], "content": m["content"]})
    api_messages.append({"role": "user", "content": user_message_for_model})

    def generate():
        import session_store_supabase as ssb_mod

        client = get_client()
        full_response = []
        try:
            stream = client.chat.completions.create(
                model="deepseek-chat",
                messages=api_messages,
                stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    full_response.append(delta)
                    yield f"data: {json.dumps({'delta': delta}, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            return

        assistant_content = "".join(full_response)
        new_title = "新会话"
        if use_sb_sess and chat_uid is not None:
            prev = ssb_mod.get_user_session(chat_uid, sid)
            if prev is not None:
                msgs = list(prev.get("messages", []))
                msgs.append({"role": "user", "content": content})
                msgs.append({"role": "assistant", "content": assistant_content})
                t = prev.get("title", "新会话")
                if len(msgs) == 2:
                    t = content[:30] + ("..." if len(content) > 30 else "")
                ssb_mod.save_user_session(chat_uid, sid, t, msgs)
                new_title = t
        else:
            fresh = load_data()
            s = fresh["sessions"].get(sid)
            if s is not None:
                s["messages"].append({"role": "user", "content": content})
                s["messages"].append({"role": "assistant", "content": assistant_content})
                if len(s["messages"]) == 2:
                    s["title"] = content[:30] + ("..." if len(content) > 30 else "")
                save_data(fresh)
                new_title = s.get("title", "新会话")
        done_payload = {"done": True, "title": new_title}
        if rag_meta is not None:
            done_payload["rag"] = rag_meta
        yield f"data: {json.dumps(done_payload, ensure_ascii=False)}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# 静态文件
@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("static", path)


if __name__ == "__main__":
    if not os.environ.get("VERCEL"):
        _rb, _ = resolve_rag_backend()
        if _rb == "local":
            try:
                import faiss  # noqa: F401
            except ModuleNotFoundError:
                print(
                    "[提示] 当前为本地 RAG 模式但未检测到 faiss，建库会失败。请执行 pip install -r requirements.txt "
                    "或使用 .venv/bin/python app.py 启动。\n"
                )
    app.run(host="0.0.0.0", port=5001, debug=True)
