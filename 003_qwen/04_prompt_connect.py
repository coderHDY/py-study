"""
让模型返回是否是有关联的
1. 只给返回【是】或者【不是】
2. 给三个案例
"""

import os
from openai import OpenAI
import json


sys_prompt = f"你是一个股票文本分析助手，请分析多段文本是否相关，你只能回答：【是】或者【不是】,注意返回数组格式。"

examples = [
    {
        "content": f"{"股票市场今日大涨，投资者乐观","持续上涨的市场让投资者感到满意"}",
        "answers": "[是]",
    },
    {
        "content": f"{"油价大幅下跌，能源公司面临挑战", "未来智能城市的建设趋势愈发明显"}",
        "answers": "[不是]",
    },
    {
        "content": f"{"利率大幅下跌，能源公司面临挑战", "高利率对房地产有一定冲击"}",
        "answers": "[是]",
    },
]


def text_analyse(user_prompt: str):
    client = OpenAI(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    messages = [
        {
            "role": "system",
            "content": sys_prompt,
        },
    ]

    for ex in examples:
        messages += [
            {"role": "user", "content": ex["content"]},
            {"role": "assistant", "content": f"{ex["answers"]}"},
        ]

    messages.append({"role": "user", "content": user_prompt})

    completion = client.chat.completions.create(
        model="qwen-plus",  # 此处以qwen-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        messages=messages,
    )

    try:
        json_obj = json.loads(completion.choices[0].message.content)
        return json_obj
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return completion.choices[0].message.content


user_prompt = f""""
{
  "Qwen3是最好的模型，适合处理复杂、多步骤任务。",
  "Qwen3模型很强。",
}
"""
# user_prompt = f""""
# {
#   "阿里云百炼是一站式大模型开发与应用平台，集成了千问及主流第三方模型。它为开发者提供了兼容OpenAI的API及全链路模型服务；同时，也提供可视化应用构建能力，让业务人员能快速创建智能体、知识库问答等AI应用。",
#   "橘子不含对狗狗有毒的成分（不像葡萄、巧克力、洋葱等）。",
# }
# """

res = text_analyse(user_prompt)
print(res)
json_str = json.dumps(res, ensure_ascii=False)
print(f"json化：{json_str}")
