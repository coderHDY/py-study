"""天气 + 地点介绍智能体（ReAct + Tool Schema 驱动）

ReAct 终止条件（通用，与具体工具/业务无关）：
  1. 模型返回无 tool_calls          → 任务完成（标准 ReAct 出口）
  2. 模型重复相同 Action            → 判定卡住，转入合成阶段
  3. 达到 MAX_STEPS                   → 兜底，转入合成阶段

合成阶段：解除 bind_tools，仅生成 Final Answer。
"""

from __future__ import annotations

import json
import os
from typing import Annotated

import requests
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.messages.tool import ToolCall
from langchain_core.tools import tool
from pydantic import Field
from tavily import TavilyClient

MODEL_ID = os.getenv("MODEL_ID", "qwen-plus")
MAX_STEPS = 8
VERBOSE = os.getenv("AGENT_VERBOSE", "1").lower() in {"1", "true", "yes"}

# Action 阶段：模型通过 function calling 调工具，content 里可有简短推理（仅调试可见）
REACT_SYSTEM_PROMPT = """
你是通用旅行助手。通过 function calling 调用工具完成任务。

原则：
- 所有事实必须来自 ToolMessage（Observation），禁止编造。
- 每次只调用一个工具，读完 Observation 再决定下一步。
- 若某工具缺少必填参数，先调用其他工具补齐。
- 同一工具+相同参数只需调用一次；信息已足够时，停止调用工具（返回空 tool_calls）。
- 停止调工具后，系统会进入单独的合成阶段生成用户可见回答，你无需在 content 里写 Final Answer。
""".strip()

# Synthesis 阶段：独立 system prompt，与 Action 阶段分离（业界标准两阶段架构）
SYNTHESIS_SYSTEM_PROMPT = """
你是旅行助手。请根据对话中的用户问题和工具 Observation，生成面向用户的最终回答。

要求：
- 只输出用户应该看到的内容
- 不要输出思考过程，不要使用 Thought、Final Answer 等标签
- 综合 Observation 中的事实，用中文简洁回答
""".strip()


def print_title(title: str) -> None:
    print(f"\n{'=' * 20} {title} {'=' * 20}")


def build_model(**kwargs) -> ChatTongyi:
    return ChatTongyi(model=MODEL_ID, **kwargs)


@tool
def get_weather(
    city: Annotated[str, Field(description="城市或地区名，如「成都」「东京」")],
) -> str:
    """查询指定地点的当前实时天气。

    返回温度、体感、湿度、风力、天气状况等摘要，供 recommend_places 的 weather_context 使用。
    """
    try:
        response = requests.get(
            f"https://wttr.in/{city}",
            params={"format": "j1", "lang": "zh"},
            timeout=15,
            headers={"User-Agent": "curl/7.64.1"},
        )
        response.raise_for_status()
        data = response.json()
        current = data["current_condition"][0]
        area = data["nearest_area"][0]["areaName"][0]["value"]
        return (
            f"{area} 当前天气：{current['weatherDesc'][0]['value']}，"
            f"温度 {current['temp_C']}°C（体感 {current['FeelsLikeC']}°C），"
            f"湿度 {current['humidity']}%，风速 {current['windspeedKmph']} km/h。"
        )
    except Exception as exc:  # noqa: BLE001
        return f"查询「{city}」天气失败：{exc}"


@tool
def search_place_info(
    place: Annotated[str, Field(description="城市或地区名")],
    focus: Annotated[
        str,
        Field(description="搜索侧重，如「历史」「文化」「美食」「建筑」"),
    ] = "综合介绍",
) -> str:
    """搜索指定地点的背景介绍（历史、文化、美食等）。

    用于纯信息查询，不涉及「此刻适合去哪玩」的实时出行建议。
    """
    return _tavily_search(place=place, focus=focus, weather_context="")


@tool
def recommend_places(
    place: Annotated[str, Field(description="城市或地区名")],
    weather_context: Annotated[
        str,
        Field(
            description=(
                "必填。必须填入 get_weather 工具返回的完整 Observation 摘要，"
                "以便结合晴/雨/高温/大风等条件推荐合适的室内外景点与玩法。"
                "若尚未获取，请先调用 get_weather，不可编造。"
            )
        ),
    ],
    focus: Annotated[
        str,
        Field(description="推荐侧重，如「户外景点」「室内博物馆」「亲子」「美食打卡」"),
    ] = "景点与玩法",
) -> str:
    """结合实时天气，推荐指定地点此刻适合的景点与玩法。

    前置依赖：weather_context 必须来自 get_weather 的 Observation。
    """
    if not weather_context.strip() or weather_context.startswith("查询"):
        return (
            "无法推荐：weather_context 缺失或无效。"
            "请先调用 get_weather 获取真实天气，再将 Observation 原样传入本工具。"
        )
    return _tavily_search(place=place, focus=focus, weather_context=weather_context)


def _tavily_search(place: str, focus: str, weather_context: str) -> str:
    tavily_key = os.getenv("TAVILY_API_KEY")
    if not tavily_key:
        return "未配置 TAVILY_API_KEY，无法搜索。请前往 https://tavily.com 注册获取。"

    query_parts = [place, focus, "旅游"]
    if weather_context.strip():
        query_parts.extend(
            ["景点推荐", f"当前天气：{weather_context}", "适合这种天气的玩法"]
        )
    else:
        query_parts.append("介绍")

    client = TavilyClient(api_key=tavily_key)
    try:
        result = client.search(
            query=" ".join(query_parts),
            max_results=5,
            search_depth="basic",
        )
    except Exception as exc:  # noqa: BLE001
        return f"搜索「{place}」失败：{exc}"

    header = f"【检索】地点={place}，侧重={focus}"
    if weather_context.strip():
        header += f"，天气={weather_context}"

    snippets = [header]
    for index, item in enumerate(result.get("results", []), start=1):
        snippets.append(
            f"{index}. {item.get('title', '无标题')}\n{item.get('content', '')}"
        )

    return (
        "\n\n".join(snippets) if len(snippets) > 1 else f"未找到关于「{place}」的资料。"
    )


TOOLS = [get_weather, search_place_info, recommend_places]
TOOLS_BY_NAME = {t.name: t for t in TOOLS}


def _log(msg: str) -> None:
    if VERBOSE:
        print(msg)


def _has_tool_observations(messages: list) -> bool:
    return any(isinstance(message, ToolMessage) for message in messages)


def _tool_call_fingerprint(tool_call: ToolCall) -> str:
    return json.dumps(
        {"name": tool_call["name"], "args": tool_call["args"]},
        sort_keys=True,
        ensure_ascii=False,
    )


def _executed_fingerprints(messages: list) -> set[str]:
    fingerprints: set[str] = set()
    for message in messages:
        if isinstance(message, AIMessage) and message.tool_calls:
            for tool_call in message.tool_calls:
                fingerprints.add(_tool_call_fingerprint(tool_call))
    return fingerprints


def _message_text(content: str | list[str | dict] | None) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    return str(content)


def _synthesize_answer(messages: list) -> str:
    """Synthesis 阶段：解除 bind_tools + 切换 system prompt，只生成用户可见回答。

    业界标准做法：Action 与 Answer 分两次调用、两套 prompt，不靠解析文本标记。
    """
    model = build_model(temperature=0)
    dialogue = [m for m in messages if not isinstance(m, SystemMessage)]
    response = model.invoke(
        [
            SystemMessage(content=SYNTHESIS_SYSTEM_PROMPT),
            *dialogue,
        ]
    )
    return _message_text(response.content)


def run_agent(user_prompt: str) -> str:
    """ReAct 两阶段：Action（bind_tools）→ Synthesis（纯文本回答）。"""
    model_with_tools = build_model(temperature=0).bind_tools(TOOLS)
    messages: list = [
        SystemMessage(content=REACT_SYSTEM_PROMPT),
        HumanMessage(content=user_prompt),
    ]
    executed = _executed_fingerprints(messages)

    for step in range(1, MAX_STEPS + 1):
        ai_message = model_with_tools.invoke(messages)

        if ai_message.content:
            _log(
                f"\n[Step {step} | Thought]\n{_message_text(ai_message.content).strip()}"
            )

        # 终止条件 1：模型停止调工具
        if not ai_message.tool_calls:
            if _has_tool_observations(messages):
                _log(f"\n[Step {step}] 模型停止调工具 → Synthesis 阶段")
                return _synthesize_answer(messages)
            return _message_text(ai_message.content)

        tool_call: ToolCall = ai_message.tool_calls[0]
        fingerprint = _tool_call_fingerprint(tool_call)

        # 终止条件 2：重复 Action
        if fingerprint in executed:
            _log(f"\n[Step {step}] 重复 Action → Synthesis 阶段")
            return _synthesize_answer(messages)

        if len(ai_message.tool_calls) > 1:
            skipped = [tc["name"] for tc in ai_message.tool_calls[1:]]
            _log(f"（本步仅执行 {tool_call['name']}，下轮再决策：{skipped}）")

        tool_call_id = tool_call.get("id") or ""
        _log(f"[Step {step} | Action] {tool_call['name']}({tool_call['args']})")
        observation = str(TOOLS_BY_NAME[tool_call["name"]].invoke(tool_call["args"]))
        _log(
            f"[Step {step} | Observation]\n{observation[:240]}{'...' if len(observation) > 240 else ''}"
        )

        messages.extend(
            [
                AIMessage(content=ai_message.content, tool_calls=[tool_call]),
                ToolMessage(content=observation, tool_call_id=tool_call_id),
            ]
        )
        executed.add(fingerprint)

    # 终止条件 3：步数上限
    _log("\n[达到 MAX_STEPS] → Synthesis 阶段")
    return _synthesize_answer(messages)


def main() -> None:
    print(f"ReAct Agent · ChatTongyi({MODEL_ID})\n")

    examples = [
        # "我周末想去成都，帮我查一下现在天气，并推荐有什么值得看的。",
        # "东京现在天气怎么样？",
        # "介绍一下西安的历史和必去景点。",
        "杭州今天适合去西湖还是逛博物馆？",
    ]

    for index, prompt in enumerate(examples, start=1):
        print_title(f"示例 {index}")
        print(f"用户：{prompt}")
        answer = run_agent(prompt)
        print("\n" + answer)


if __name__ == "__main__":
    main()
