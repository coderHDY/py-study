/**
 * AI 南瓜智能伴侣 - 前端逻辑
 */
const API = "/api";

/** 每浏览器 / 设备一个 ID，用于隔离 RAG 与会话（随请求头 X-Client-User-Id 发送） */
const CLIENT_USER_ID_KEY = "pumpkin-client-user-id";

function getOrCreateClientUserId() {
  try {
    let id = localStorage.getItem(CLIENT_USER_ID_KEY);
    if (!id || id.length < 8) {
      id = crypto.randomUUID();
      localStorage.setItem(CLIENT_USER_ID_KEY, id);
    }
    return id;
  } catch (_) {
    return "fallback-" + String(Date.now());
  }
}

const clientUserId = getOrCreateClientUserId();

function apiFetch(url, options = {}) {
  const headers = new Headers(options.headers || {});
  headers.set("X-Client-User-Id", clientUserId);
  const isForm = typeof FormData !== "undefined" && options.body instanceof FormData;
  if (!isForm && options.body && typeof options.body === "string" && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  return fetch(url, { ...options, headers });
}

let currentSessionId = null;
let sessions = [];

// DOM
const sessionList = document.getElementById("sessionList");
const chatArea = document.getElementById("chatArea");
const welcome = document.getElementById("welcome");
const messages = document.getElementById("messages");
const input = document.getElementById("input");
const btnNew = document.getElementById("btnNew");
const btnSend = document.getElementById("btnSend");
const btnConfig = document.getElementById("btnConfig");
const modalOverlay = document.getElementById("modalOverlay");
const btnClose = document.getElementById("btnClose");
const btnSave = document.getElementById("btnSave");
const configName = document.getElementById("configName");
const configPersonality = document.getElementById("configPersonality");
const chkUseRag = document.getElementById("chkUseRag");
const ragFiles = document.getElementById("ragFiles");
const btnIngest = document.getElementById("btnIngest");
const ragRuntime = document.getElementById("ragRuntime");
const ragStatusLine = document.getElementById("ragStatusLine");
const sidebar = document.querySelector(".sidebar");
const sidebarToggle = document.getElementById("sidebarToggle");

const USE_RAG_KEY = "pumpkin-use-rag";

// 侧边栏收缩状态（持久化）
const SIDEBAR_KEY = "pumpkin-sidebar-collapsed";

function isSidebarCollapsed() {
  return localStorage.getItem(SIDEBAR_KEY) === "true";
}

function setSidebarCollapsed(collapsed) {
  localStorage.setItem(SIDEBAR_KEY, String(collapsed));
  sidebar.classList.toggle("collapsed", collapsed);
}

function toggleSidebar() {
  setSidebarCollapsed(!isSidebarCollapsed());
}

// 加载会话列表
async function loadSessions() {
  try {
    const res = await apiFetch(`${API}/sessions`);
    const data = await res.json();
    sessions = data.sessions || [];
    renderSessionList();
    if (!currentSessionId && sessions.length > 0) {
      const withMessages = sessions.find(s => s.messages && s.messages.length > 0);
      if (withMessages) {
        switchSession(withMessages.id);
      } else {
        // 只有空会话，激活但不在侧边栏显示
        currentSessionId = sessions[0].id;
        renderSessionList();
        showWelcome();
        messages.innerHTML = "";
        messages.classList.remove("visible");
      }
    } else if (!currentSessionId) {
      await createSession();
    }
  } catch (e) {
    console.error("加载会话失败", e);
  }
}

// 渲染会话列表（只展示有消息的会话）
function renderSessionList() {
  const visibleSessions = sessions.filter(s => s.messages && s.messages.length > 0);
  sessionList.innerHTML = visibleSessions
    .map(
      (s) =>
        `<div class="session-item ${s.id === currentSessionId ? "active" : ""}" data-id="${s.id}">
          <span class="session-title">${escapeHtml(s.title || "新会话")}</span>
          <button class="btn-session-menu" data-id="${s.id}" title="更多操作">⋯</button>
          <div class="session-menu" data-id="${s.id}">
            <button class="session-menu-item delete" data-id="${s.id}">🗑 删除会话</button>
          </div>
        </div>`
    )
    .join("");

  sessionList.querySelectorAll(".session-item").forEach((el) => {
    el.addEventListener("click", (e) => {
      if (e.target.closest(".btn-session-menu") || e.target.closest(".session-menu")) return;
      switchSession(el.dataset.id);
    });
  });

  sessionList.querySelectorAll(".btn-session-menu").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const sid = btn.dataset.id;
      // 关闭其他已展开的菜单
      sessionList.querySelectorAll(".session-menu.open").forEach((m) => {
        if (m.dataset.id !== sid) m.classList.remove("open");
      });
      const menu = sessionList.querySelector(`.session-menu[data-id="${sid}"]`);
      menu.classList.toggle("open");
    });
  });

  sessionList.querySelectorAll(".session-menu-item.delete").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      deleteSession(btn.dataset.id);
    });
  });
}

// 删除会话
async function deleteSession(sid) {
  try {
    await apiFetch(`${API}/sessions/${sid}`, { method: "DELETE" });
    sessions = sessions.filter((s) => s.id !== sid);
    if (currentSessionId === sid) {
      currentSessionId = null;
      messages.innerHTML = "";
      messages.classList.remove("visible");
      if (sessions.length > 0) {
        switchSession(sessions[0].id);
      } else {
        await createSession();
      }
    } else {
      renderSessionList();
    }
  } catch (e) {
    console.error("删除会话失败", e);
  }
}

// 新建会话
async function createSession() {
  // 已有空会话则直接跳转，不重复创建
  const emptySession = sessions.find(s => !s.messages || s.messages.length === 0);
  if (emptySession) {
    currentSessionId = emptySession.id;
    renderSessionList();
    showWelcome();
    messages.innerHTML = "";
    messages.classList.remove("visible");
    return;
  }
  try {
    const res = await apiFetch(`${API}/sessions`, { method: "POST" });
    const data = await res.json();
    sessions.unshift(data);
    currentSessionId = data.id;
    renderSessionList();
    showWelcome();
    messages.innerHTML = "";
    messages.classList.remove("visible");
  } catch (e) {
    console.error("新建会话失败", e);
  }
}

// 切换会话
function switchSession(sid) {
  currentSessionId = sid;
  renderSessionList();
  const s = sessions.find((x) => x.id === sid);
  if (!s) return;

  if (s.messages && s.messages.length > 0) {
    welcome.classList.add("hidden");
    messages.classList.add("visible");
    messages.innerHTML = s.messages
      .map((m) => renderMessage(m.role, m.content))
      .join("");
    chatArea.scrollTop = chatArea.scrollHeight;
  } else {
    showWelcome();
    messages.innerHTML = "";
    messages.classList.remove("visible");
  }
}

// 显示欢迎
function showWelcome() {
  welcome.classList.remove("hidden");
}

// 存储 AI 原始文本用于复制
const messageContents = new Map();
let msgIdCounter = 0;

// 智能自动滚动：仅在用户靠近底部时才跟随
const SCROLL_THRESHOLD = 80; // px
function isNearBottom() {
  return chatArea.scrollHeight - chatArea.scrollTop - chatArea.clientHeight < SCROLL_THRESHOLD;
}
function scrollToBottomIfNeeded() {
  if (isNearBottom()) chatArea.scrollTop = chatArea.scrollHeight;
}

// 渲染单条消息
function renderMessage(role, content) {
  const avatar = role === "user" ? "你" : "🎃";
  const roleName = role === "user" ? "你" : "南瓜";
  if (role === "user") {
    const text = escapeHtml(content).replace(/\n/g, "<br>");
    return `<div class="msg ${role}">
      <div class="avatar">${avatar}</div>
      <div class="msg-body">
        <div class="role">${roleName}</div>
        <div class="bubble">${text}</div>
      </div>
    </div>`;
  } else {
    const id = ++msgIdCounter;
    messageContents.set(id, content);
    return `<div class="msg ${role}">
      <div class="avatar">${avatar}</div>
      <div class="msg-body">
        <div class="role">${roleName}</div>
        <div class="bubble markdown-body">${marked.parse(content)}</div>
        <button class="btn-copy" data-msg-id="${id}">复制</button>
      </div>
    </div>`;
  }
}

// 发送消息
async function sendMessage() {
  const content = input.value.trim();
  if (!content || !currentSessionId) return;

  btnSend.disabled = true;
  input.value = "";
  input.style.height = "auto";

  welcome.classList.add("hidden");
  messages.classList.add("visible");
  messages.insertAdjacentHTML("beforeend", renderMessage("user", content));

  const assistantEl = document.createElement("div");
  assistantEl.className = "msg assistant";
  assistantEl.innerHTML = `
    <div class="avatar">🎃</div>
    <div class="msg-body">
      <div class="role">南瓜</div>
      <div class="bubble markdown-body"><span class="typing-cursor">▋</span></div>
    </div>
  `;
  messages.appendChild(assistantEl);
  // 发送新消息时强制滚到底部
  chatArea.scrollTop = chatArea.scrollHeight;

  const bubble = assistantEl.querySelector(".bubble");
  let fullText = "";
  const sentWithRag = chkUseRag.checked;

  try {
    const res = await apiFetch(`${API}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: currentSessionId,
        content,
        use_rag: sentWithRag,
      }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      bubble.textContent = "错误: " + (err.error || res.statusText);
      btnSend.disabled = false;
      return;
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      const lines = buffer.split("\n");
      buffer = lines.pop();

      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        const jsonStr = line.slice(6).trim();
        if (!jsonStr) continue;
        try {
          const msg = JSON.parse(jsonStr);
          if (msg.error) {
            bubble.textContent = "错误: " + msg.error;
          } else if (msg.delta) {
            fullText += msg.delta;
            bubble.innerHTML = marked.parse(fullText) + '<span class="typing-cursor">▋</span>';
            scrollToBottomIfNeeded();
          } else if (msg.done) {
            bubble.innerHTML = marked.parse(fullText);
            const id = ++msgIdCounter;
            messageContents.set(id, fullText);
            const copyBtn = document.createElement("button");
            copyBtn.className = "btn-copy";
            copyBtn.textContent = "复制";
            copyBtn.setAttribute("data-msg-id", String(id));
            const msgBody = assistantEl.querySelector(".msg-body");
            msgBody.appendChild(copyBtn);
            if (sentWithRag && msg.rag) {
              const foot = document.createElement("div");
              foot.className = "rag-footnote";
              if (msg.rag.error) {
                foot.classList.add("rag-footnote-error");
                foot.textContent = "知识库未生效：" + msg.rag.error;
              } else if (msg.rag.hits > 0) {
                foot.textContent = "已结合知识库 · " + msg.rag.hits + " 条片段";
              } else {
                foot.textContent = "知识库已开启，本次未匹配到相关片段（可换关键词或检查索引）";
              }
              msgBody.appendChild(foot);
            }
            if (msg.title) {
              const s = sessions.find(x => x.id === currentSessionId);
              if (s) s.title = msg.title;
            }
            loadSessions();
          }
        } catch (_) {}
      }
    }
  } catch (e) {
    bubble.textContent = "网络错误: " + e.message;
  }

  scrollToBottomIfNeeded();
  btnSend.disabled = false;
}

// 配置
async function loadConfig() {
  try {
    const res = await apiFetch(`${API}/config`);
    const data = await res.json();
    configName.value = data.name || "";
    configPersonality.value = data.personality || "";
    const rt = data.rag_runtime || {};
    const kb =
      rt.backend === "cloud" ? "云端" : rt.backend === "local" ? "本地" : "—";
    const ss =
      data.sessions_storage === "cloud" ? "云端（按设备同步）" : "本地文件";
    ragRuntime.textContent = (rt.error
      ? `知识库存储：${kb}（${rt.error}）`
      : `知识库存储：${kb}`) + ` · 会话：${ss}`;
    await refreshRagStatus();
  } catch (e) {
    console.error("加载配置失败", e);
  }
}

async function refreshRagStatus() {
  try {
    const res = await apiFetch(`${API}/rag/status`);
    const s = await res.json();
    if (s.error) {
      ragStatusLine.textContent = `状态: ${s.chunk_count ?? 0} 条 · ${s.error}`;
    } else {
      const t = s.updated_at ? ` · 更新 ${s.updated_at}` : "";
      ragStatusLine.textContent = `状态: ${s.chunk_count ?? 0} 条片段${t}`;
    }
  } catch (e) {
    ragStatusLine.textContent = "状态: 无法获取";
  }
}

async function saveConfig() {
  try {
    await apiFetch(`${API}/config`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: configName.value.trim(),
        personality: configPersonality.value.trim(),
      }),
    });
    modalOverlay.classList.remove("visible");
  } catch (e) {
    console.error("保存配置失败", e);
  }
}

async function ingestRag() {
  const files = ragFiles.files;
  if (!files || files.length === 0) {
    alert("请先选择 .txt 或 .md 文件");
    return;
  }
  btnIngest.disabled = true;
  ragStatusLine.textContent = "正在建库…";
  try {
    const fd = new FormData();
    for (let i = 0; i < files.length; i++) fd.append("files", files[i]);
    fd.append("replace", "true");
    const res = await apiFetch(`${API}/rag/ingest`, { method: "POST", body: fd });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      ragStatusLine.textContent = data.error || res.statusText;
      return;
    }
    ragStatusLine.textContent = `建库完成，共 ${data.chunks} 个片段（已自动勾选「知识库」）`;
    ragFiles.value = "";
    chkUseRag.checked = true;
    localStorage.setItem(USE_RAG_KEY, "true");
    await refreshRagStatus();
  } catch (e) {
    ragStatusLine.textContent = "建库失败: " + e.message;
  } finally {
    btnIngest.disabled = false;
  }
}

function initUseRagToggle() {
  const stored = localStorage.getItem(USE_RAG_KEY);
  if (stored !== null) {
    chkUseRag.checked = stored === "true";
    return;
  }
  chkUseRag.checked = true;
}

chkUseRag.addEventListener("change", () => {
  localStorage.setItem(USE_RAG_KEY, String(chkUseRag.checked));
});

function escapeHtml(s) {
  const div = document.createElement("div");
  div.textContent = s;
  return div.innerHTML;
}

// 输入框自动高度
input.addEventListener("input", function () {
  this.style.height = "auto";
  this.style.height = Math.min(this.scrollHeight, 120) + "px";
});

input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

// 事件绑定
btnNew.addEventListener("click", createSession);
btnSend.addEventListener("click", sendMessage);
btnConfig.addEventListener("click", () => {
  loadConfig();
  modalOverlay.classList.add("visible");
});
btnIngest.addEventListener("click", ingestRag);
btnClose.addEventListener("click", () => modalOverlay.classList.remove("visible"));
btnSave.addEventListener("click", saveConfig);
modalOverlay.addEventListener("click", (e) => {
  if (e.target === modalOverlay) modalOverlay.classList.remove("visible");
});

// 点击空白关闭会话菜单
document.addEventListener("click", () => {
  sessionList.querySelectorAll(".session-menu.open").forEach((m) => m.classList.remove("open"));
});

// 侧边栏收缩
sidebarToggle.addEventListener("click", toggleSidebar);
setSidebarCollapsed(isSidebarCollapsed());

// 复制按钮事件委托
messages.addEventListener("click", (e) => {
  const btn = e.target.closest(".btn-copy");
  if (!btn) return;
  const id = parseInt(btn.getAttribute("data-msg-id"), 10);
  const text = messageContents.get(id) || "";
  navigator.clipboard.writeText(text).then(() => {
    btn.textContent = "已复制 ✓";
    setTimeout(() => { btn.textContent = "复制"; }, 2000);
  }).catch(() => {
    btn.textContent = "复制失败";
    setTimeout(() => { btn.textContent = "复制"; }, 2000);
  });
});

// 初始化
initUseRagToggle();
loadSessions();
