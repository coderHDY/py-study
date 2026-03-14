/**
 * AI 南瓜智能伴侣 - 前端逻辑
 */
const API = "/api";

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
const sidebar = document.querySelector(".sidebar");
const sidebarToggle = document.getElementById("sidebarToggle");

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
    const res = await fetch(`${API}/sessions`);
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
    await fetch(`${API}/sessions/${sid}`, { method: "DELETE" });
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
    const res = await fetch(`${API}/sessions`, { method: "POST" });
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

  welcome.classList.add("hidden");
  messages.classList.add("visible");
  messages.insertAdjacentHTML("beforeend", renderMessage("user", content));

  const assistantEl = document.createElement("div");
  assistantEl.className = "msg assistant";
  assistantEl.innerHTML = `
    <div class="avatar">🎃</div>
    <div class="msg-body">
      <div class="role">南瓜</div>
      <div class="bubble markdown-body">思考中...</div>
    </div>
  `;
  messages.appendChild(assistantEl);
  chatArea.scrollTop = chatArea.scrollHeight;

  try {
    const res = await fetch(`${API}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: currentSessionId, content }),
    });

    const data = await res.json();

    if (!res.ok) {
      assistantEl.querySelector(".bubble").textContent = "错误: " + (data.error || res.statusText);
    } else {
      const bubble = assistantEl.querySelector(".bubble");
      bubble.innerHTML = marked.parse(data.assistant);
      const id = ++msgIdCounter;
      messageContents.set(id, data.assistant);
      const copyBtn = document.createElement("button");
      copyBtn.className = "btn-copy";
      copyBtn.textContent = "复制";
      copyBtn.setAttribute("data-msg-id", String(id));
      assistantEl.querySelector(".msg-body").appendChild(copyBtn);
    }

    loadSessions();
  } catch (e) {
    assistantEl.querySelector(".bubble").textContent = "网络错误: " + e.message;
  }

  chatArea.scrollTop = chatArea.scrollHeight;
  btnSend.disabled = false;
}

// 配置
async function loadConfig() {
  try {
    const res = await fetch(`${API}/config`);
    const data = await res.json();
    configName.value = data.name || "";
    configPersonality.value = data.personality || "";
  } catch (e) {
    console.error("加载配置失败", e);
  }
}

async function saveConfig() {
  try {
    await fetch(`${API}/config`, {
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
loadSessions();
