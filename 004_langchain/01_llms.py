from langchain_community.llms.tongyi import Tongyi

model = Tongyi(model="qwen-plus")

# res = model.invoke("你好，你是谁")
# print(res)

# 流式输出
res = model.stream("你好，你是谁")
for chunk in res:
    print(chunk, end="", flush=True)