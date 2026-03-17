import os
from openai import OpenAI

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

text_break_prompt = """
你是一个文本关键词提取助手，不管后续提供多少文字，都提供其中的关键字并以json的形式返回，仅能返回这三个字段：
1. "title": 15字以内
2. "description": 30字以内
3. "keyWord": 数组形式，每个项目8字以内

整体示例：
{
    "title": "教育局对学生上课睡觉问题的呼吁",
    "description": "",
    "keywords": ["高校新闻", "学生上课睡觉问题"]
}
"""


user_prompt = """
3月16日，长沙市公安局天心分局发布警情通报，全文如下：2026年3月15日凌晨，天心区发生一起涉嫌寻衅滋事案件，涉案人员已被公安机关依法采取刑事强制措施。
3月15日2时28分，我局接群众报警称，辖区某火锅店门口有人发生不雅行为。民警迅速到场处置，依法将涉案人员传唤到公安机关接受调查。经查，外地来长人员张某某(男，36岁),唐某某(女，35岁)在公共场所实施不雅行为，起哄闹事，严重扰乱公共秩序，其行为已涉嫌犯罪。目前，案件正在进一步侦办中。
"""


completion = client.chat.completions.create(
    model="qwen-plus",  # 此处以qwen-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    messages=[
        {"role": "system", "content": text_break_prompt},
        {"role": "user", "content": user_prompt},
    ],
)
print(completion.choices[0].message.content)
