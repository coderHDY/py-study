import os
from openai import OpenAI
import json

def text_analyse(user_prompt):
    client = OpenAI(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    text_break_prompt = """
    你是一个文本类型分析助手，不管后续提供多少文字，都分析其类型（单个或多个）并以数组的形式返回，仅能返回总结字段做成的一个数组，每个总结关键字不能超过十个字：
    1. 例子1（只有一段文字）: ["新闻报道"]
    1. 例子2（多段内容文字）: ["新闻报道", "财务公告"]
    """

    # 1. 例子1（只有一段文字）: [{"type": "新闻报道"}]
    # 1. 例子2（多段内容文字）: [{"type": "新闻报道"}, {"type": "财务公告"}]

    completion = client.chat.completions.create(
        model="qwen-plus",  # 此处以qwen-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        messages=[
            {"role": "system", "content": text_break_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    try:
        json_obj = json.loads(completion.choices[0].message.content)
        return json_obj
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return []

user_prompt = """"
1. 已学完，老师讲的深入浅出，通俗易懂[打call][打call]。复盘了一下就去美团面试了。面试官：看了你的简历，了解到你有两年半的送外卖经验，可以简单说下平时是怎么送外卖的吗？我：我首先在平台上接单，然后到店里取餐，取到餐后骑电动车到顾客留下的地址，再通知顾客取餐。面试官：你们也用电动车来配送啊，那能说一下电动车的运行原理吗？我：电动车的工作原理是通过锂电池释放存储的电能，经过电控系统将电能转化为电动机的机械能，然后电动机驱动电动车的机械结构，从而推动电动车行驶。面试官：锂电池是怎么把化学能转化为电能的呢？锂电池化学成分以及反应方程式有了解过吗？我：这个不太了解。面试官：没关系，平时有空应该多研究电动车的底层实现，这样才能提升送外卖水平。对了，你们平时开什么品牌的电动车？我：我们平时用雅迪电动车，还有深远电动车。面试官：我们团队用的是小刀电动车，看来我们的技术栈不太匹配，这次面试就到这里吧，我们过两天会通知您面试结果。
2. 3月16日，长沙市公安局天心分局发布警情通报，全文如下：2026年3月15日凌晨，天心区发生一起涉嫌寻衅滋事案件，涉案人员已被公安机关依法采取刑事强制措施。
3月15日2时28分，我局接群众报警称，辖区某火锅店门口有人发生不雅行为。民警迅速到场处置，依法将涉案人员传唤到公安机关接受调查。经查，外地来长人员张某某(男，36岁),唐某某(女，35岁)在公共场所实施不雅行为，起哄闹事，严重扰乱公共秩序，其行为已涉嫌犯罪。目前，案件正在进一步侦办中。
3. 阿里云百炼是一站式大模型开发与应用平台，集成了千问及主流第三方模型。它为开发者提供了兼容OpenAI的API及全链路模型服务；同时，也提供可视化应用构建能力，让业务人员能快速创建智能体、知识库问答等AI应用。
4. 特斯拉已开始将马斯克旗下 xAI 公司的 Grok 大模型 嵌入到车辆软件生态中：
智能座舱：搭载 AMD 处理器的 Model S/3/X/Y 及 Cybertruck（需软件版本 2025.26 或更高）已上线 Grok 助手，支持更自然的语音交互和行程规划。
FSD 深度集成：特斯拉正开发通过 Grok 语音指令控制 FSD（全自动驾驶）的功能。驾驶员未来可以通过日常用语指挥车辆，例如“去超市并在门口倒车入库”。
Optimus 机器人：Grok 将作为 Optimus 人形机器人 的“大脑”，为其提供语义理解和逻辑推理能力，而 FSD 算法则负责处理机器人的物理运动。
"""

res = text_analyse(user_prompt)
print(res)
print(type(res))
