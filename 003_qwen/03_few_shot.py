"""
分析股票信息助手
"""
import os
from openai import OpenAI
import json


def text_analyse(user_prompt):
    client = OpenAI(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    schemas = ["日期", "股票名称", "开盘价", "收盘价", "成交量"]

    examples = [
        {
            "content": "2023-01-10，股市霞荡。股票强大科技A股今日开盘价100人民币，一度舰升至105人民币，随后回落至98人民币，最终以102人民币收盘，成交量达到520000手。",
            "answers": {
                "日期": "2023-01-10",
                "股票名称": "强大科技A股",
                "开盘价": "100人民币",
                "收盘价": "98人民币",
                "成交量": "520000",
            },
        },
        {
            "content": "2024-02-29（闰年！），“时间科技”开盘60.00，收盘61.00，成交量606060，纪念四年一次！",
            "answers": {
                "日期": "2024-02-29",
                "股票名称": "时间科技",
                "开盘价": "60.00",
                "收盘价": "61.00",
                "成交量": "606060",
            },
        },
    ]

    messages = [
        {
            "role": "system",
            "content": f"你是一个股票文本分析助手，请抽取文字中的关键内容：{schemas},注意返回标准json格式。如果没有抽取到目标信息，可以用'-'表示，例如：【'成交量': '-'】",
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
        # print(completion.choices[0].message.content)
        json_obj = json.loads(completion.choices[0].message.content)
        return json_obj
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return []


user_prompt = """"
2023-04-18：巨能电子（股票代码：600889）今儿个开在56.3元，盘中冲到59，尾盘跳水，最后收57.8，成交了整整1,230,000手！
"""

res = text_analyse(user_prompt)
print(res)
json_str = json.dumps(res, ensure_ascii=False)
print(f"json化：{json_str}")