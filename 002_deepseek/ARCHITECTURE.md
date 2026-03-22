# AI 南瓜智能伴侣 - 项目架构文档

## 一、项目概述

**AI 南瓜智能伴侣** 是一个基于 DeepSeek API 的智能对话应用，支持多会话管理、流式响应与可定制的 AI 性格。采用前后端分离架构，后端为 Flask REST API，前端为纯原生 HTML/JS/CSS，数据以 JSON 文件持久化。

---

## 二、技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3, Flask 3.x, Flask-CORS |
| AI 集成 | OpenAI SDK（兼容 DeepSeek API） |
| 前端 | 原生 HTML5, Vanilla JavaScript, CSS3 |
| 数据存储 | JSON 文件 |
| 部署 | 本地开发 + Vercel Serverless |

---

## 三、项目结构

```
002_deepseek/
├── app.py              # 主应用入口，Flask 后端 + API
├── deepseek.py         # 独立脚本：DeepSeek API 调用示例（非主应用）
├── requirements.txt    # Python 依赖
├── vercel.json         # Vercel 部署配置
├── data/
│   └── sessions.json  # 会话与配置数据（本地持久化）
├── static/
│   ├── index.html      # 单页应用主页面
│   ├── app.js          # 前端逻辑
│   └── style.css       # 主题样式
└── README.md
```

---

## 四、架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         Browser (用户)                            │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                     static/ 静态资源                               │
│  index.html │ app.js │ style.css │ marked.js (CDN)               │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  │ HTTP / Fetch API
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                     app.py (Flask 后端)                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ 会话 API    │  │ 配置 API    │  │ 聊天 API (SSE 流式)      │  │
│  │ GET/POST    │  │ GET/PUT     │  │ POST → Server-Sent Events│  │
│  │ /api/sessions│  │ /api/config │  │ /api/chat               │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
         │                    │                      │
         └────────────────────┼──────────────────────┘
                              ▼
         ┌────────────────────────────────────────────┐
         │  data/sessions.json 或 /tmp/sessions.json   │
         │  (本地: data/ | Vercel: /tmp)               │
         └────────────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────────────┐
         │  DeepSeek API (https://api.deepseek.com)   │
         │  使用 OpenAI SDK 兼容接口                   │
         └────────────────────────────────────────────┘
```

---

## 五、核心模块说明

### 5.1 后端 (app.py)

| 模块 | 职责 |
|------|------|
| **数据层** | `load_data()` / `save_data()`：读写 `sessions.json` |
| **AI 客户端** | `get_client()`：创建 OpenAI 兼容客户端，指向 DeepSeek API |
| **路由** | 会话 CRUD、配置、聊天、静态文件托管 |

#### API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/sessions` | 获取所有会话列表 |
| POST | `/api/sessions` | 新建会话 |
| GET | `/api/sessions/<sid>` | 获取单个会话 |
| DELETE | `/api/sessions/<sid>` | 删除会话 |
| GET | `/api/config` | 获取配置（名字、性格） |
| PUT | `/api/config` | 更新配置 |
| POST | `/api/chat` | 发送消息，SSE 流式返回 AI 回复 |
| GET | `/` | 返回 index.html |
| GET | `/<path>` | 静态文件 |

#### 数据存储策略

- **本地**：使用 `data/sessions.json`
- **Vercel**：使用 `/tmp/sessions.json`（因 Vercel 文件系统仅 `/tmp` 可写）

### 5.2 前端 (static/)

| 文件 | 职责 |
|------|------|
| **index.html** | 布局：侧边栏、对话区、输入区、配置弹窗 |
| **app.js** | 会话管理、消息渲染、流式聊天、配置读写、Markdown 渲染 |
| **style.css** | 南瓜主题（深色）、响应式、Markdown 样式 |

#### 前端状态

- `currentSessionId`：当前会话 ID
- `sessions`：会话列表
- `messageContents`：Map，用于复制 AI 回复
- `localStorage`：侧边栏收起状态 (`pumpkin-sidebar-collapsed`)

### 5.3 数据模型 (sessions.json)

```json
{
  "sessions": {
    "<session_id>": {
      "messages": [
        { "role": "user" | "assistant", "content": "..." }
      ],
      "title": "首条消息摘要或自定义标题"
    }
  },
  "config": {
    "name": "南瓜小助手",
    "personality": "系统提示词，定义 AI 性格"
  }
}
```

---

## 六、关键流程

### 6.1 聊天流程（流式）

1. 用户输入 → 前端 `POST /api/chat`（`session_id`, `content`）
2. 后端构造 `[system, ...history, user]` 消息列表
3. 调用 DeepSeek API `stream=True`，逐 chunk 返回
4. 后端通过 SSE (`data: {...}\n\n`) 推送 `delta` 给前端
5. 前端用 `marked.parse()` 实时渲染 Markdown
6. 流结束后推送 `done`，后端将完整消息写入 `sessions.json`，首条消息作为 `title`

### 6.2 会话与配置

- 新建会话：`POST /api/sessions` → 生成 8 位 UUID 作为 `sid`
- 侧边栏仅展示有消息的会话
- 配置中的 `personality` 作为 system 角色内容注入每次聊天

---

## 七、部署

### 7.1 本地

```bash
pip3 install -r requirements.txt
export DEEPSEEK_API_KEY=xxx  # 可选，否则需在代码中提供
python3 app.py
```

访问：http://localhost:5001

### 7.2 Vercel

- `vercel.json` 指定 `app.py` 为 Python 入口
- 路由 `/(.*)` 全部转发至 `app.py`
- 需在 Vercel 环境变量中配置 `DEEPSEEK_API_KEY`

---

## 八、依赖说明 (requirements.txt)

| 包 | 用途 |
|----|------|
| openai | 兼容 DeepSeek API 的 OpenAI SDK |
| flask | Web 框架 |
| flask-cors | 跨域支持 |
| socksio | 代理/网络支持 |

---

## 九、补充说明

- **deepseek.py**： standalone 脚本，用于快速验证 DeepSeek API 调用，不参与主应用。
- **Markdown**：前端通过 CDN 引入 `marked.js`，对 AI 回复进行 Markdown 渲染。
- **流式输出**：使用 Server-Sent Events，前端通过 `fetch` + `ReadableStream` 解析行并更新 DOM。
