# LangChain Chat Models 教案

**业务场景：** 电商 SaaS 平台"智能客服工单助手"  
**模型：** `ChatTongyi(model="qwen-plus")`

> **ChatModel vs LLM 根本区别**  
> - `LLM`：输入/输出是纯字符串  
> - `ChatModel`：输入是消息列表（`BaseMessage`），输出是消息对象（`AIMessage`）  
> 现代 LangChain 推荐优先使用 ChatModel

---

## 准备工作：公共常量与工具函数

```python
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_community.chat_models.tongyi import ChatTongyi

SERVICE_PROMPT = "你是电商 SaaS 平台的智能客服工单助手..."   # 系统提示词
TICKET_TEXT    = "用户昵称：木木 / 订单号：A20260325001..."  # 示例工单
BATCH_TICKETS  = ["工单A", "工单B", "工单C"]                # 批量工单

def build_model(**kwargs) -> ChatTongyi:
    return ChatTongyi(model="qwen-plus", **kwargs)
```

- `SERVICE_PROMPT` 作为 `SystemMessage` 贯穿所有演示，统一角色设定。
- `build_model()` 是工厂函数，方便每段演示按需覆盖参数（`temperature` 等）。

---

## 1. invoke

```python
def demo_invoke() -> None:
    model = build_model(temperature=0.2)
    response = model.invoke(ticket_messages(TICKET_TEXT))
    print(response.content)
```

**运行结果**

```
**一、用户问题总结：**
- 用户「木木」于昨日开通专业版服务（订单号：A20260325001）；
- 今日发现「高级报表」功能仍不可用，疑似未生效；
- 客服页面提示存在「重复扣费」，用户质疑资费异常；
- 有明确时效诉求：需在今日下午3点前恢复报表功能...
...
**二、处理建议：**
✅ 优先级：P0（紧急）
→ 涉及功能未开通 + 资金异常 + 明确截止时间（今日15:00），需立即响应与闭环。
...
```

- **作用**：把消息列表一次性发给模型，**阻塞等待**完整响应后返回 `AIMessage`。
- **定位**：所有同步场景的通用入口，是 LCEL `Runnable` 接口的核心方法之一。
- **vs `stream`**：`invoke` 拿到全部内容再返回；`stream` 是逐 token yield，两者功能等价，体验不同。
- **vs `LLM.invoke`**：`LLM` 接受字符串；`ChatModel` 接受消息列表，输出也是消息对象。

---

## 2. stream

```python
def demo_stream() -> None:
    model = build_model(temperature=0.3)
    stream = model.stream([SystemMessage(...), HumanMessage(...)])
    for chunk in stream:
        if chunk.content:
            print(chunk.content, end="", flush=True)
```

**运行结果**

```
木木您好，非常理解您的紧急需求。我们已紧急核查订单A20260325001，确认高级报表权限未生效及扣费异常问题。
技术团队正在实时处理，预计1小时内为您恢复功能并核实扣款明细。确认重复扣费将立即原路退款。
稍后专员将电话同步进展。感谢您的信任与耐心！
```

- **作用**：不等模型生成完就开始 yield，每次返回一个 `AIMessageChunk`（增量片段）。
- **定位**：前端"打字机效果"、长文本实时展示、降低首 token 延迟感（TTFT）。
- **vs `invoke`**：`invoke` 整块返回；`stream` 增量返回，体验更好，内存峰值更低。
- **注意**：`AIMessageChunk` 逐片累积，最终拼完等价于一次 `invoke` 的完整结果。

---

## 3. 多轮消息

```python
def demo_multi_turn() -> None:
    model = build_model(temperature=0.2)
    messages = [
        SystemMessage(content=SERVICE_PROMPT),
        HumanMessage(content="这是第一轮工单：\n..."),      # 用户第一轮
        AIMessage(content="初步判断为权限未同步..."),        # 模型历史回复
        HumanMessage(content="补充信息：权限10分钟内可补发..."),  # 用户第二轮
    ]
    response = model.invoke(messages)
```

**运行结果**

```
您好，木木，感谢您的及时反馈与耐心等待！
我们已紧急核查确认：
✅ 您的专业版权限已同步至系统，高级报表功能即刻可用...
✅ 财务侧核实确有一笔重复扣款，退款已发起，预计1–3个工作日内原路退回...
```

- **三种消息角色**：
  - `SystemMessage`：全局角色设定，放在列表最前面，贯穿整轮对话。
  - `HumanMessage`：用户输入，每轮至少一条。
  - `AIMessage`：模型历史回复，用于构造多轮上下文。
- **定位**：ChatModel 区别于 LLM 最核心的能力——原生支持多角色消息结构。
- **注意**：模型本身**无状态**，每次调用都要把完整历史传入，不会自动记忆上一轮。

---

## 4. with_structured_output

```python
def demo_structured_output() -> None:
    schema = {
        "type": "object",
        "properties": {
            "category":           {"type": "string"},
            "priority":           {"type": "string"},
            "sentiment":          {"type": "string"},
            "need_human_followup": {"type": "boolean"},
            "reply_points":       {"type": "array", "items": {"type": "string"}},
        },
    }
    model = build_model(temperature=0).with_structured_output(schema)
    result = model.invoke([SystemMessage(...), HumanMessage(...)])
    pretty_print(result)  # → dict
```

**运行结果**

```json
{
  "category": "订阅与计费问题",
  "need_human_followup": true,
  "priority": "urgent",
  "reply_points": [
    "确认订单号 A20260325001 的开通状态和扣费明细",
    "核实高级报表功能是否已随专业版自动启用",
    "检查是否存在重复扣费，并承诺2小时内反馈核查结果",
    "如确属重复扣费，将安排原路退款并同步处理时效"
  ],
  "sentiment": "焦虑且急迫"
}
```

- **作用**：给模型套一层输出格式约束，返回结果自动解析为 `dict` 或 `Pydantic` 模型。
- **底层**：通过 function calling（tool call）实现——模型被要求按 schema 填参，框架再把参数解析为目标类型。
- **vs 手动 `OutputParser`**：不用自己写解析，更简洁；不合规范时抛异常而非返回脏数据。
- **vs `bind_tools`**：`with_structured_output` 强制格式化**单次输出**；`bind_tools` 让模型自主决定是否调用外部函数，侧重点不同。

---

## 5. bind

```python
def demo_bind() -> None:
    # bind 不改变原对象，返回一个新的 Runnable
    model = build_model().bind(temperature=0.1, top_p=0.8)
    response = model.invoke([...])
```

**运行结果**

```
1. 先致歉，再确认扣费笔数与时间
2. 明确告知权限未开通原因及解法
3. 承诺退款并同步处理时效
```

- **作用**：把固定参数（`temperature`、`top_p`、`stop` 等）提前锁定，返回"已配置的新 Runnable"。
- **定位**：LCEL `Runnable` 通用方法，所有 Runnable（Chain、Tool 等）都支持。
- **vs 构造函数传参**：构造函数参数随对象固定；`bind` 是运行时覆盖，不改变原对象，可轻松派生出多种参数版本（如宽松版/严格版）。
- **vs `bind_tools`**：`bind` 绑定任意参数；`bind_tools` 是专门注入工具定义的语义化封装。

---

## 6. bind_tools

```python
@tool
def query_refund_policy(order_age_days: int, activated: bool) -> str:
    """查询退款政策。"""
    ...

@tool
def create_escalation_ticket(reason: str, priority: str) -> str:
    """创建人工升级工单。"""
    ...

def demo_bind_tools() -> None:
    model = build_model(temperature=0).bind_tools([query_refund_policy, create_escalation_ticket])

    # 第 1 步：模型决定调哪些工具
    ai_message = model.invoke(messages)

    # 第 2 步：代码执行工具，包装为 ToolMessage
    for tool_call in ai_message.tool_calls:
        tool_result = tools[tool_call["name"]].invoke(tool_call["args"])
        tool_messages.append(ToolMessage(content=str(tool_result), tool_call_id=tool_call["id"]))

    # 第 3 步：把工具结果回传给模型，生成最终回复
    final_response = model.invoke(messages + [ai_message] + tool_messages)
```

**运行结果**

```
模型首轮回复：
用户问题重点总结：购买专业版1天内发现重复扣费，且功能权限尚未生效...

工具调用：
[
  {"name": "query_refund_policy",      "args": {"activated": false, "order_age_days": 1}},
  {"name": "create_escalation_ticket", "args": {"priority": "high", "reason": "用户购买专业版..."}}
]

最终结论：
✅ 用户符合「1天内未开通订单」的全额原路退款政策；
✅ 已同步创建高优人工升级工单，由财务与技术团队联合核查...
```

- **作用**：把 `@tool` 装饰的函数的签名和描述传给模型，让模型决定何时调用，并在响应中生成 `tool_calls` 字段，再由代码执行后回传结果。
- **调用流程（Agentic Loop 最小单元）**：
  1. `model.invoke(messages)` → `ai_message.tool_calls`（模型想调哪些工具）
  2. 代码执行工具，包装为 `ToolMessage`
  3. `model.invoke(... + tool_messages)` → 整合工具结果，生成最终回复
- **vs `with_structured_output`**：`bind_tools` 让模型"选择性调用外部函数"；`with_structured_output` 是强制把输出格式化为某个 schema，不涉及真实函数调用。

---

## 7. with_retry + with_fallbacks

```python
def demo_retry_and_fallback() -> None:
    primary_model  = build_model(temperature=0.2).with_retry(stop_after_attempt=2)
    fallback_model = build_model(temperature=0.4)
    resilient_model = primary_model.with_fallbacks([fallback_model])
    response = resilient_model.invoke([...])
```

**运行结果**

```
因为客服系统需保障高可用与强响应性，`with_retry` 可自动重试因网络抖动或临时服务不可用导致的
失败请求，而 `with_fallbacks` 能在主逻辑异常时优雅降级至备用策略，从而提升用户体验与系统鲁棒性。
```

**with_retry**
- **作用**：调用失败（超时、限速、网络抖动）时自动重试 N 次再最终报错。
- **定位**：LCEL Runnable 通用方法，不改变接口，仅在外层追加重试逻辑。
- **适用**：同一个模型因偶发错误失败的场景。

**with_fallbacks**
- **作用**：主 Runnable 彻底失败后，依次尝试备用 Runnable 列表。
- **定位**：同样是 LCEL 通用方法，常用于主备模型切换，可跨厂商/型号。
- **vs `with_retry`**：`retry` 是对同一个模型多次尝试；`fallbacks` 是切换到另一个模型。
- **两者可叠加**：先 retry，全部失败后再 fallback，构成双重保障。

---

## 8. batch

```python
def demo_batch() -> None:
    model = build_model(temperature=0.2)
    requests = [
        [SystemMessage(...), HumanMessage(content=f"请判断优先级：{ticket}")]
        for ticket in BATCH_TICKETS
    ]
    responses = model.batch(requests)   # 返回等长的响应列表
    for index, response in enumerate(responses, start=1):
        print(f"工单 {index}: {response.content}")
```

**运行结果**

```
工单 1: 优先级：高（P0）— 用户已付费但核心功能未开通，有明确时效要求（今日15:00前）...
工单 2: 优先级：高（P1）— 影响客户交付（周报发送），为高频、可快速验证的前端显示问题...
工单 3: 优先级：中高 — 涉及开票资质合规性，影响用户报销及财务入账，需及时响应但非紧急故障...
```

- **作用**：一次性传入多个消息列表，框架内部用**线程池**并发执行，返回等长的响应列表。
- **定位**：比循环调用 `invoke` 更高效，适合一次性处理大量独立请求（如批量工单分类）。
- **vs `invoke`**：`invoke` 处理一个请求；`batch` 处理多个，顺序与输入**严格对应**。
- **vs `abatch`**：`batch` 用线程池（同步阻塞直到全部完成）；`abatch` 用 `asyncio`（真正协程并发），若服务本身是异步框架，优先选 `abatch`。

---

## 9. ainvoke

```python
async def demo_async() -> None:
    model = build_model(temperature=0.2)
    response = await model.ainvoke([SystemMessage(...), HumanMessage(...)])
    print(response.content)
```

**运行结果**

```
`ainvoke` 适合在需要异步调用单个可等待对象（如异步函数、协程）并等待其结果的场景，
常用于 LangChain 等框架中执行非阻塞的单次链式调用。
```

- **作用**：`invoke` 的异步版，需在 `async` 函数里 `await`，不阻塞事件循环。
- **定位**：适合 `FastAPI`、`aiohttp` 等异步 Web 框架，或需要并发触发多个模型调用的场景。
- **vs `invoke`**：功能完全相同，区别在调用方式（协程 vs 同步阻塞）。

---

## 10. abatch

```python
async def demo_async() -> None:
    ...
    requests = [
        [SystemMessage(...), HumanMessage(content=f"请把工单压缩成一句摘要：{ticket}")]
        for ticket in BATCH_TICKETS[:2]
    ]
    responses = await model.abatch(requests)
    for index, response in enumerate(responses, start=1):
        print(f"异步工单 {index}: {response.content}")
```

**运行结果**

```
异步工单 1: 用户反馈专业版已扣费但高级报表权限未生效，要求今日15:00前解决。
异步工单 2: 用户反馈导出的 Excel 文件出现乱码，已影响向客户发送周报。
```

- **作用**：`batch` 的异步版，在单一事件循环内真正并发执行多个请求。
- **vs `batch`**：`batch` 用线程池模拟并发；`abatch` 基于 `asyncio`，对 IO 密集型请求（如批量调模型 API）性能更好，协程开销也更小。
- **实际项目**：若整个服务是异步驱动（如 `FastAPI`），用 `abatch` 而非 `batch`。

---

## API 速查对比

| API | 是否同步 | 处理数量 | 典型场景 |
|-----|---------|---------|--------|
| `invoke` | 同步 | 单条 | 普通请求处理 |
| `stream` | 同步（流式） | 单条 | 打字机效果、长文本 |
| `batch` | 同步 | 多条 | 批量离线任务 |
| `ainvoke` | 异步 | 单条 | 异步 Web 服务 |
| `abatch` | 异步 | 多条 | 异步高并发服务 |
| `bind` | — | — | 预设固定参数 |
| `bind_tools` | — | — | Function Calling |
| `with_structured_output` | — | — | 强制 JSON 输出 |
| `with_retry` | — | — | 自动重试 |
| `with_fallbacks` | — | — | 主备模型切换 |
