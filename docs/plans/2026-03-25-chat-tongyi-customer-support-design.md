# ChatTongyi Customer Support Design

## Goal

在一个统一的“智能客服工单助手”业务场景下，演示 LangChain `chat_models` 的主要 API，帮助学习者理解 `ChatTongyi(model="qwen-plus")` 在真实业务中的常见用法。

## Why This Scenario

客服工单场景天然包含分类、总结、回复建议、工具调用、多轮沟通、批量分析和异步处理，能够较自然地覆盖 `invoke`、`stream`、`batch`、`ainvoke`、`abatch`、`bind`、`bind_tools`、`with_structured_output`、`with_retry`、`with_fallbacks` 等核心 API。

## Script Shape

脚本保持和 `004_langchain/01_llms.py` 一样的单文件、直接运行风格，但会拆成多个演示函数，每个函数聚焦一个 API：

1. `invoke`：分析单条工单并输出摘要和建议
2. `stream`：流式生成客服回复
3. 多轮消息：基于 `SystemMessage`、`HumanMessage`、`AIMessage` 继续对话
4. `with_structured_output`：返回结构化工单分析结果
5. `bind`：绑定温度等固定参数，生成更稳定的回复
6. `bind_tools`：让模型先调用“退款政策查询”“人工升级工单”工具
7. `with_retry` + `with_fallbacks`：演示更稳健的调用方式
8. `batch`：批量分析多条工单
9. `ainvoke` + `abatch`：异步处理单条和多条工单

## Data Flow

所有示例都复用同一组客服提示词和工单文本，避免每一段都重新解释业务背景。工具调用部分会先让模型决定是否调用工具，再把工具结果通过 `ToolMessage` 回传给模型，生成最终客服结论。

## Error Handling

- 不额外引入复杂异常封装，保持教学脚本简洁。
- 使用 `with_retry` 和 `with_fallbacks` 展示 LangChain 原生的稳健调用方式。
- 保留少量说明，提示脚本依赖 `DASHSCOPE_API_KEY`。

## Testing Strategy

这是一个依赖外部模型服务的教学脚本，不适合做严格单元测试。验证方式采用运行脚本进行 smoke test，确认各段 API 至少能完成一次成功调用。

## Constraints

- 模型主体使用 `qwen-plus`。
- 优先使用当前环境已经支持的 API，避免写入本地版本无法运行的示例。
- 代码注释保持简洁，避免把示例写成框架工程。
