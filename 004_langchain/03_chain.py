"""langchain_core.prompts 常用方法示例。

运行方式：
	python 004_langchain/03_chain.py

说明：
1) 本文件聚焦 langchain_core.prompts 的常用 API。
2) 默认使用 FakeListLLM，方便离线学习，不依赖 API Key。
3) 每个 demo 都有中文注释，按函数名即可快速定位。
"""

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import FewShotPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables import RunnablePassthrough
from langchain_community.llms.fake import FakeListLLM


def print_title(title: str) -> None:
	print(f"\n{'=' * 18} {title} {'=' * 18}")


def demo_01_from_template_and_format() -> None:
	"""PromptTemplate.from_template + format。"""
	print_title("01 from_template + format")
	prompt = PromptTemplate.from_template(
		"你是一个{role}，请用一句话解释 {topic}。"
	)
	formatted_text = prompt.format(role="Python 老师", topic="闭包")
	print(formatted_text)


def demo_02_format_prompt() -> None:
	"""PromptTemplate.format_prompt 返回 PromptValue。"""
	print_title("02 format_prompt")
	prompt = PromptTemplate.from_template("把 {topic} 讲给 10 岁小朋友听。")
	prompt_value = prompt.format_prompt(topic="列表推导式")
	print(type(prompt_value).__name__)
	print(prompt_value.to_string())


def demo_03_partial() -> None:
	"""PromptTemplate.partial：先绑定部分变量。"""
	print_title("03 partial")
	base = PromptTemplate.from_template("你是{role}，请回答：{question}")
	teacher_prompt = base.partial(role="耐心的 Python 导师")
	print(teacher_prompt.format(question="什么是生成器？"))


def demo_04_from_examples() -> None:
	"""PromptTemplate.from_examples：快速构造 few-shot 文本模板。"""
	print_title("04 from_examples")
	prompt = PromptTemplate.from_examples(
		examples=[
			"输入: 你好\n输出: Hello",
			"输入: 谢谢\n输出: Thank you",
		],
		suffix="输入: {text}\n输出:",
		input_variables=["text"],
		example_separator="\n\n",
	)
	print(prompt.format(text="晚上好"))


def demo_05_invoke_and_batch() -> None:
	"""PromptTemplate 是 Runnable，支持 invoke / batch。"""
	print_title("05 invoke + batch")
	prompt = PromptTemplate.from_template("请总结主题：{topic}")

	# invoke：单次输入
	one = prompt.invoke({"topic": "函数式编程"})
	print("invoke:", one.to_string())

	# batch：批量输入
	inputs = [{"topic": "装饰器"}, {"topic": "上下文管理器"}]
	batch_values = prompt.batch(inputs)
	print("batch:")
	for i, pv in enumerate(batch_values, start=1):
		print(f"  {i}. {pv.to_string()}")


def demo_06_chat_prompt_from_messages() -> None:
	"""ChatPromptTemplate.from_messages + format_messages。"""
	print_title("06 ChatPromptTemplate.from_messages")
	chat_prompt = ChatPromptTemplate.from_messages(
		[
			("system", "你是{role}"),
			("human", "请解释：{topic}"),
		]
	)
	messages = chat_prompt.format_messages(role="Python 讲师", topic="迭代器")
	for msg in messages:
		print(f"{msg.type}: {msg.content}")


def demo_07_messages_placeholder() -> None:
	"""MessagesPlaceholder：把多轮历史作为变量注入。"""
	print_title("07 MessagesPlaceholder")
	chat_prompt = ChatPromptTemplate.from_messages(
		[
			("system", "你是一个学习助手"),
			MessagesPlaceholder("history"),
			("human", "基于上面对话，继续回答：{question}"),
		]
	)

	history = [
		HumanMessage(content="我在学 Python。"),
		AIMessage(content="很好，先掌握变量和流程控制。"),
	]

	messages = chat_prompt.format_messages(history=history, question="下一步学什么？")
	for msg in messages:
		print(f"{msg.type}: {msg.content}")


def demo_08_few_shot_prompt_template() -> None:
	"""FewShotPromptTemplate：结构化 few-shot 提示。"""
	print_title("08 FewShotPromptTemplate")
	examples = [
		{"word": "happy", "antonym": "sad"},
		{"word": "hot", "antonym": "cold"},
	]
	example_prompt = PromptTemplate.from_template("单词: {word}\n反义词: {antonym}")

	few_shot_prompt = FewShotPromptTemplate(
		examples=examples,
		example_prompt=example_prompt,
		prefix="给出单词反义词：",
		suffix="单词: {input}\n反义词:",
		input_variables=["input"],
	)

	print(few_shot_prompt.format(input="big"))


def demo_09_prompt_chain_with_fake_llm() -> None:
	"""PromptTemplate + LLM + Parser 的完整 chain。"""
	print_title("09 Prompt Chain")
	prompt = PromptTemplate.from_template(
		"用户问题：{question}\n背景：{context}\n请给出简短建议。"
	)
	llm = FakeListLLM(responses=["建议先定一个 7 天可执行计划，每天完成 20 分钟。"])

	chain = (
		{
			"question": RunnablePassthrough(),
			"context": RunnableLambda(lambda _: "对方是 Python 初学者"),
		}
		| prompt
		| llm
		| StrOutputParser()
	)
	result = chain.invoke("我总是学到一半就放弃，怎么办？")
	print(result)


if __name__ == "__main__":
	demo_01_from_template_and_format()
	demo_02_format_prompt()
	demo_03_partial()
	demo_04_from_examples()
	demo_05_invoke_and_batch()
	demo_06_chat_prompt_from_messages()
	demo_07_messages_placeholder()
	demo_08_few_shot_prompt_template()
	demo_09_prompt_chain_with_fake_llm()
