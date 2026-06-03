import asyncio
import json

# LangChain chat_models 核心 API 演示
# 业务场景：电商 SaaS 平台"智能客服工单助手"
#
# 演示顺序：
#   invoke → stream → 多轮消息 → with_structured_output → bind
#   → bind_tools → with_retry + with_fallbacks → batch → ainvoke + abatch
#
# 核心区分点：ChatModel vs LLM
#   ChatModel 的输入/输出是消息对象（BaseMessage），LLM 直接用纯字符串。
#   现代 LangChain 推荐优先使用 ChatModel。

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_community.chat_models.tongyi import ChatTongyi


SERVICE_PROMPT = """
你是电商 SaaS 平台的智能客服工单助手。
你的任务是帮助客服同学完成三件事：
1. 读懂用户问题并总结重点
2. 判断优先级和处理方式
3. 产出专业、礼貌、简洁的中文回复

如果信息不足，不要编造订单状态，应该明确说明还需要什么信息。
""".strip()

TICKET_TEXT = """
用户昵称：木木
订单号：A20260325001
工单内容：
我昨天刚开通你们的专业版，结果今天发现高级报表还是不能用，客服页面还提示我重复扣费了两次。
我下午 3 点前要给老板看数据，现在非常着急。请尽快帮我处理，如果确认重复扣费我要求原路退款。
""".strip()

BATCH_TICKETS = [
    "用户反馈专业版已扣费但高级报表权限未生效，希望 3 点前处理。",
    "用户表示导出的 Excel 文件乱码，已经影响给客户发周报。",
    "用户咨询能否把企业版发票抬头从个人改成公司，需要操作指引。",
]


def print_title(title: str) -> None:
    print(f"\n{'=' * 20} {title} {'=' * 20}")


def build_model(**kwargs) -> ChatTongyi:
    return ChatTongyi(model="qwen-plus", **kwargs)


def pretty_print(data) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def ticket_messages(ticket_text: str):
    return [
        SystemMessage(content=SERVICE_PROMPT),
        HumanMessage(
            content=(
                "请先总结用户问题，再给出处理建议。\n" f"工单内容如下：\n{ticket_text}"
            )
        ),
    ]


def demo_invoke() -> None:
    # invoke —— 最基础的同步单次调用
    # 作用：把消息列表一次性发给模型，阻塞等待完整响应后返回 AIMessage。
    # 定位：所有同步场景的通用入口，是 LCEL Runnable 接口的核心方法之一。
    # vs stream  ：invoke 拿到全部内容再返回；stream 是逐 token yield。
    # vs LLM.invoke：LLM 接受字符串；ChatModel 接受消息列表，输出也是消息对象。
    print_title("1. invoke")
    model = build_model(temperature=0.2)
    response = model.invoke(ticket_messages(TICKET_TEXT))
    print(response.content)


def demo_stream() -> None:
    # stream —— 流式输出
    # 作用：不等模型生成完就开始 yield，每次返回一个 AIMessageChunk。
    # 定位：前端打字机效果、长文本实时展示、降低首 token 延迟感（TTFT）。
    # vs invoke：invoke 整块返回；stream 增量返回，体验更好，内存峰值更低。
    # 注意：AIMessageChunk 逐片累积，拼完等价于一次 invoke 的完整结果。
    print_title("2. stream")
    model = build_model(temperature=0.3)
    stream = model.stream(
        [
            SystemMessage(content=SERVICE_PROMPT),
            HumanMessage(
                content=(
                    "请直接写一段发给用户的正式回复，语气专业、安抚情绪、长度控制在 120 字以内。\n"
                    f"工单内容：\n{TICKET_TEXT}"
                )
            ),
        ]
    )
    for chunk in stream:
        if chunk.content:
            print(chunk.content, end="", flush=True)
    print()


def demo_multi_turn() -> None:
    # 多轮消息 —— SystemMessage / HumanMessage / AIMessage
    # 作用：把历史对话一起放进消息列表，让模型感知上下文并继续作答。
    # 三种消息角色：
    #   SystemMessage  → 全局角色设定，放在列表最前面，贯穿整轮对话。
    #   HumanMessage   → 用户输入，每轮至少一条。
    #   AIMessage      → 模型历史回复，用于构造多轮上下文。
    # 定位：ChatModel 区别于 LLM 最核心的能力——原生支持多角色消息结构。
    # 注意：模型本身无状态，每次调用都要把完整历史传入，不会自动记忆。
    print_title("3. 多轮消息")
    model = build_model(temperature=0.2)
    messages = [
        SystemMessage(content=SERVICE_PROMPT),
        HumanMessage(content=f"这是第一轮工单：\n{TICKET_TEXT}"),
        AIMessage(
            content=(
                "初步判断为权限未同步 + 疑似重复扣费，建议先核对订阅状态和支付流水，再给用户承诺处理时限。"
            )
        ),
        HumanMessage(
            content="补充信息：技术同学确认权限 10 分钟内可以补发，财务系统显示确实重复扣了一笔。请继续生成最终回复。"
        ),
    ]
    response = model.invoke(messages)
    print(response.content)


def demo_structured_output() -> None:
    # with_structured_output —— 强制结构化输出
    # 作用：给模型套一层输出格式约束，返回结果自动解析为 dict 或 Pydantic 模型。
    # 定位：在 invoke 前插入解析层，形成 model → parser 的 Chain。
    # 底层：通常通过 function calling（tool call）实现——模型被要求按 schema 填参，
    #       框架再把 tool_call 的参数解析为目标类型。
    # vs 手动 OutputParser：不用自己写解析，更简洁；不合规范时抛异常而非返回脏数据。
    # vs bind_tools：with_structured_output 强制格式化单次输出；bind_tools 让模型
    #   自主决定是否调用外部函数，侧重点不同。
    print_title("4. with_structured_output")
    schema = {
        "title": "ticket_analysis",
        "description": "客服工单分析结果",
        "type": "object",
        "properties": {
            "category": {"type": "string", "description": "工单类别"},
            "priority": {
                "type": "string",
                "description": "优先级，low/medium/high/urgent",
            },
            "sentiment": {"type": "string", "description": "用户情绪"},
            "need_human_followup": {
                "type": "boolean",
                "description": "是否需要人工继续跟进",
            },
            "reply_points": {
                "type": "array",
                "items": {"type": "string"},
                "description": "客服回复应包含的要点",
            },
        },
        "required": [
            "category",
            "priority",
            "sentiment",
            "need_human_followup",
            "reply_points",
        ],
    }
    model = build_model(temperature=0).with_structured_output(schema)
    result = model.invoke(
        [
            SystemMessage(content=SERVICE_PROMPT),
            HumanMessage(content=f"请分析这条工单并返回结构化结果：\n{TICKET_TEXT}"),
        ]
    )
    pretty_print(result)


def demo_bind() -> None:
    # bind —— 预绑定运行时参数
    # 作用：把固定参数（temperature、top_p、stop 等）提前锁定，返回"已配置的新 Runnable"。
    # 定位：LCEL Runnable 通用方法，所有 Runnable（Chain、Tool 等）都支持。
    # vs 构造函数传参：构造函数参数随对象固定；bind 是运行时覆盖，不改变原对象，
    #   可轻松从同一模型派生出多种参数版本（如宽松版/严格版）。
    # vs bind_tools：bind 绑定任意参数；bind_tools 是专门注入工具定义的语义化封装。
    print_title("5. bind")
    model = build_model().bind(temperature=0.1, top_p=0.8)
    response = model.invoke(
        [
            SystemMessage(content=SERVICE_PROMPT),
            HumanMessage(
                content="请输出 3 条客服回复原则，每条不超过 18 个字，适用于‘权限未开通且重复扣费’场景。"
            ),
        ]
    )
    print(response.content)


@tool
def query_refund_policy(order_age_days: int, activated: bool) -> str:
    """查询退款政策。"""
    if activated:
        return f"订单已开通，购买 {order_age_days} 天内可提交人工审核退款，需先核对重复扣费记录。"
    return f"订单未开通，购买 {order_age_days} 天内可直接原路退款。"


@tool
def create_escalation_ticket(reason: str, priority: str) -> str:
    """创建人工升级工单。"""
    return f"已创建人工升级工单：原因={reason}，优先级={priority}。"


def demo_bind_tools() -> None:
    # bind_tools —— 注入工具定义，启用 Function Calling
    # 作用：把 @tool 装饰的 Python 函数的签名和描述传给模型，让模型决定何时调用，
    #       并在响应中生成 tool_calls 字段，再由代码执行后回传结果。
    # 定位：bind 的语义化封装，底层仍是把 tools 参数注入请求体。
    # 调用流程（Agentic Loop 最小单元）：
    #   1. model.invoke(messages)            → ai_message.tool_calls（想调哪些工具）
    #   2. 代码执行工具，包装为 ToolMessage
    #   3. model.invoke(... + tool_messages) → 整合工具结果，生成最终回复
    # vs with_structured_output：bind_tools 让模型"选择性调用外部函数"；
    #   with_structured_output 是强制把输出格式化为某个 schema，不涉及真实函数调用。
    print_title("6. bind_tools")
    model = build_model(temperature=0).bind_tools(
        [query_refund_policy, create_escalation_ticket]
    )
    messages = [
        SystemMessage(content=SERVICE_PROMPT),
        HumanMessage(
            content=(
                "用户购买专业版 1 天内发现重复扣费，且功能权限还没生效。"
                "请你先决定是否需要调用工具，再给出处理结论。"
            )
        ),
    ]

    ai_message = model.invoke(messages)
    print("模型首轮回复：")
    print(ai_message.content or "模型选择先调用工具，文本内容为空。")
    print("工具调用：")
    pretty_print(ai_message.tool_calls)

    tools = {
        query_refund_policy.name: query_refund_policy,
        create_escalation_ticket.name: create_escalation_ticket,
    }
    tool_messages = []
    for tool_call in ai_message.tool_calls:
        tool_result = tools[tool_call["name"]].invoke(tool_call["args"])
        tool_messages.append(
            ToolMessage(content=str(tool_result), tool_call_id=tool_call["id"])
        )

    final_response = model.invoke(messages + [ai_message] + tool_messages)
    print("最终结论：")
    print(final_response.content)


def demo_retry_and_fallback() -> None:
    # with_retry —— 自动重试
    # 作用：调用失败（超时、限速、网络抖动）时自动重试 N 次再最终报错。
    # 定位：LCEL Runnable 通用方法，不改变接口，仅在外层追加重试逻辑。
    # 适用：同一个模型因偶发错误失败的场景。
    #
    # with_fallbacks —— 备用模型兜底
    # 作用：主 Runnable 彻底失败后，依次尝试备用 Runnable 列表。
    # 定位：同样是 LCEL 通用方法，常用于主备模型切换，可跨厂商/型号。
    # vs with_retry：retry 是对同一个模型多次尝试；fallbacks 是切换到另一个模型。
    # 两者可叠加：先 retry，全部失败后再 fallback，构成双重保障。
    print_title("7. with_retry + with_fallbacks")
    primary_model = build_model(temperature=0.2).with_retry(stop_after_attempt=2)
    fallback_model = build_model(temperature=0.4)
    resilient_model = primary_model.with_fallbacks([fallback_model])
    response = resilient_model.invoke(
        [
            SystemMessage(content=SERVICE_PROMPT),
            HumanMessage(
                content="请用一句话解释：为什么客服系统适合使用 with_retry 和 with_fallbacks？"
            ),
        ]
    )
    print(response.content)


def demo_batch() -> None:
    # batch —— 同步批量调用
    # 作用：一次性传入多个消息列表，框架内部用线程池并发执行，返回等长的响应列表。
    # 定位：比循环 invoke 更高效，适合一次性处理大量独立请求（如批量工单分类）。
    # vs invoke：invoke 处理一个请求；batch 处理多个，顺序与输入严格对应。
    # vs abatch：batch 用线程池（同步阻塞直到全部完成）；
    #   abatch 用 asyncio（真正协程并发），若服务本身是异步框架，优先选 abatch。
    print_title("8. batch")
    model = build_model(temperature=0.2)
    requests = [
        [
            SystemMessage(content=SERVICE_PROMPT),
            HumanMessage(content=f"请判断优先级并给一句处理建议：{ticket}"),
        ]
        for ticket in BATCH_TICKETS
    ]
    responses = model.batch(requests)
    for index, response in enumerate(responses, start=1):
        print(f"工单 {index}: {response.content}")


async def demo_async() -> None:
    # ainvoke —— 异步单次调用
    # 作用：invoke 的异步版，需在 async 函数里 await，不阻塞事件循环。
    # 定位：适合 FastAPI、aiohttp 等异步 Web 框架，或需要并发触发多个模型调用的场景。
    # vs invoke：功能完全相同，区别在调用方式（协程 vs 同步阻塞）。
    print_title("9. ainvoke")
    model = build_model(temperature=0.2)
    response = await model.ainvoke(
        [
            SystemMessage(content=SERVICE_PROMPT),
            HumanMessage(content="请用一句话说明 `ainvoke` 适合什么场景。"),
        ]
    )
    print(response.content)

    # abatch —— 异步批量调用
    # 作用：batch 的异步版，在单一事件循环内真正并发执行多个请求。
    # vs batch：batch 用线程池模拟并发；abatch 基于 asyncio，对 IO 密集型
    #   请求（如批量调模型 API）性能更好，协程开销也更小。
    # 实际项目：若整个服务是异步驱动（如 FastAPI），用 abatch 而非 batch。
    print_title("10. abatch")
    requests = [
        [
            SystemMessage(content=SERVICE_PROMPT),
            HumanMessage(content=f"请把下面工单压缩成一句摘要：{ticket}"),
        ]
        for ticket in BATCH_TICKETS[:2]
    ]
    responses = await model.abatch(requests)
    for index, response in enumerate(responses, start=1):
        print(f"异步工单 {index}: {response.content}")


def main() -> None:
    print("客服工单助手示例启动：以下演示均基于 ChatTongyi(model='qwen-plus')")
    # demo_invoke()
    # demo_stream()
    # demo_multi_turn()
    # demo_structured_output()
    # demo_bind()
    demo_bind_tools()
    # demo_retry_and_fallback()
    # demo_batch()
    # asyncio.run(demo_async())


if __name__ == "__main__":
    main()
