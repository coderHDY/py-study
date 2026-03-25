# ChatTongyi Customer Support Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 编写一个基于 `ChatTongyi(model="qwen-plus")` 的单文件教学脚本，在统一客服工单场景下演示 LangChain 主要 `chat_models` API。

**Architecture:** 使用单文件脚本组织多个演示函数。每个函数复用同一个业务场景，但只突出一个核心 API，避免示例互相干扰。脚本通过同步和异步两类入口展示 `ChatTongyi` 的常见调用模式。

**Tech Stack:** Python, LangChain, langchain-community, ChatTongyi, DashScope/Qwen

---

### Task 1: Write the design and scenario scaffold

**Files:**
- Create: `docs/plans/2026-03-25-chat-tongyi-customer-support-design.md`
- Modify: `004_langchain/02_chat_models.py`

**Step 1: Write the scenario constants**

在脚本中加入客服系统提示词、示例工单文本和输出分隔函数。

**Step 2: Run file syntax check**

Run: `python -m py_compile 004_langchain/02_chat_models.py`
Expected: PASS

### Task 2: Implement synchronous chat model demos

**Files:**
- Modify: `004_langchain/02_chat_models.py`

**Step 1: Add `invoke`, `stream`, multi-turn, `bind` demos**

每个 demo 独立为函数，统一打印标题。

**Step 2: Smoke test the script sections**

Run: `python 004_langchain/02_chat_models.py`
Expected: 脚本按顺序输出各段标题和模型结果

### Task 3: Implement structured output and tool calling

**Files:**
- Modify: `004_langchain/02_chat_models.py`

**Step 1: Add `with_structured_output` demo**

使用 JSON Schema 输出工单分类、优先级、情绪和回复要点。

**Step 2: Add `bind_tools` demo**

定义退款政策查询和升级工单工具，打印工具调用信息，并继续生成最终结论。

**Step 3: Smoke test**

Run: `python 004_langchain/02_chat_models.py`
Expected: 输出结构化 JSON 和工具调用结果

### Task 4: Implement resiliency and batch demos

**Files:**
- Modify: `004_langchain/02_chat_models.py`

**Step 1: Add `with_retry` and `with_fallbacks` demo**

让主模型带重试策略，再追加一个备用模型实例作为兜底。

**Step 2: Add `batch` demo**

使用两到三条不同工单进行批量分析。

**Step 3: Smoke test**

Run: `python 004_langchain/02_chat_models.py`
Expected: 可以看到批量输出和稳健调用输出

### Task 5: Implement async demos and final verification

**Files:**
- Modify: `004_langchain/02_chat_models.py`

**Step 1: Add `ainvoke` and `abatch` demo**

用 `asyncio.run()` 驱动异步示例。

**Step 2: Run final verification**

Run: `python -m py_compile 004_langchain/02_chat_models.py`
Expected: PASS

Run: `python 004_langchain/02_chat_models.py`
Expected: 脚本完整运行，展示主要 `chat_models` API

### Task 6: Commit

**Files:**
- Modify: `docs/plans/2026-03-25-chat-tongyi-customer-support-design.md`
- Modify: `docs/plans/2026-03-25-chat-tongyi-customer-support.md`
- Modify: `004_langchain/02_chat_models.py`

**Step 1: Commit changes**

```bash
git add docs/plans/2026-03-25-chat-tongyi-customer-support-design.md \
  docs/plans/2026-03-25-chat-tongyi-customer-support.md \
  004_langchain/02_chat_models.py
git commit -m "feat: add ChatTongyi chat model examples"
```
