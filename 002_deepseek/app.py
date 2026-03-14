"""
AI 南瓜智能伴侣 - 后端 API
"""
import os
import json
import uuid
from pathlib import Path

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from openai import OpenAI

app = Flask(__name__, static_folder="static")
CORS(app)

DATA_DIR = Path(__file__).parent / "data"
SESSIONS_FILE = DATA_DIR / "sessions.json"


def load_data():
    """加载 sessions.json"""
    if not SESSIONS_FILE.exists():
        return {"sessions": {}, "config": {"name": "南瓜小助手", "personality": "You are a helpful assistant. 你是一个友好的AI南瓜智能伴侣。"}}
    with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    """保存 sessions.json"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_client():
    api_key = os.environ.get('DEEPSEEK_API_KEY')
    return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")


# ============ API 路由 ============

@app.route("/api/sessions", methods=["GET"])
def list_sessions():
    """获取所有会话列表"""
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
    data = load_data()
    sid = str(uuid.uuid4())[:8]
    data["sessions"][sid] = {"messages": [], "title": "新会话"}
    save_data(data)
    return jsonify({"id": sid, "title": "新会话", "messages": []})


@app.route("/api/sessions/<sid>", methods=["GET"])
def get_session(sid):
    """获取单个会话"""
    data = load_data()
    if sid not in data.get("sessions", {}):
        return jsonify({"error": "会话不存在"}), 404
    s = data["sessions"][sid]
    return jsonify({"id": sid, "title": s.get("title", "新会话"), "messages": s.get("messages", [])})


@app.route("/api/sessions/<sid>", methods=["DELETE"])
def delete_session(sid):
    """删除会话"""
    data = load_data()
    if sid not in data.get("sessions", {}):
        return jsonify({"error": "会话不存在"}), 404
    del data["sessions"][sid]
    save_data(data)
    return jsonify({"ok": True})


@app.route("/api/config", methods=["GET"])
def get_config():
    """获取配置"""
    data = load_data()
    config = data.get("config", {})
    return jsonify(config)


@app.route("/api/config", methods=["PUT"])
def update_config():
    """更新配置（名字/性格）"""
    data = load_data()
    body = request.get_json() or {}
    config = data.setdefault("config", {})
    if "name" in body:
        config["name"] = body["name"]
    if "personality" in body:
        config["personality"] = body["personality"]
    save_data(data)
    return jsonify(config)


@app.route("/api/chat", methods=["POST"])
def chat():
    """发送消息并调用 DeepSeek API"""
    body = request.get_json() or {}
    sid = body.get("session_id")
    content = body.get("content", "").strip()

    if not sid or not content:
        return jsonify({"error": "缺少 session_id 或 content"}), 400

    data = load_data()
    if sid not in data.get("sessions", {}):
        return jsonify({"error": "会话不存在"}), 404

    config = data.get("config", {})
    name = config.get("name", "南瓜小助手")
    personality = config.get("personality", "You are a helpful assistant.")

    # 构建 system 消息
    system_content = f"你的名字是 {name}。{personality}"

    session = data["sessions"][sid]
    messages = session.get("messages", [])

    # 构建 API 消息：[system] + 历史 + 新 user
    api_messages = [{"role": "system", "content": system_content}]
    for m in messages:
        api_messages.append({"role": m["role"], "content": m["content"]})
    api_messages.append({"role": "user", "content": content})

    try:
        client = get_client()
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=api_messages,
            stream=False,
        )
        assistant_content = response.choices[0].message.content or ""
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # 更新会话
    session["messages"].append({"role": "user", "content": content})
    session["messages"].append({"role": "assistant", "content": assistant_content})

    # 首条消息作为标题
    if len(session["messages"]) == 2:
        session["title"] = content[:30] + ("..." if len(content) > 30 else "")

    save_data(data)

    return jsonify({
        "user": content,
        "assistant": assistant_content,
    })


# 静态文件
@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("static", path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
