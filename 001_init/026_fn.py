# users = [
#     {"name": "张三", "age": 18},
#     {"name": "李四", "age": 25},
#     {"name": "王五", "age": 18},
# ]

# age_18_user = next((u for u in users if u["age"] == 18), None)


# print(age_18_user)


users = [
    {"name": "张三", "age": 18},
    {"name": "李四", "age": 25},
    {"name": "王五", "age": 18},
]

age_18_user = {u["name"] for u in users if u["age"] == 18}
print(age_18_user)  # {'张三', '王五'}  集合（无序、去重）

# ── 字典推导式 {key: value for ... in ...} ──────────────────
# 把列表转成 {姓名: 年龄} 的字典
name_age = {u["name"]: u["age"] for u in users}
print(name_age)  # {'张三': 18, '李四': 25, '王五': 18}

# 带过滤条件：只保留年龄 >= 20 的
adults = {u["name"]: u["age"] for u in users if u["age"] >= 20}
print(adults)  # {'李四': 25}

# ── 四种推导式对比 ──────────────────────────────────────────
nums = [1, 2, 3, 4, 5]

list_comp = [x * 2 for x in nums if x > 2]  # 列表 → 有序、可重复
set_comp = {x * 2 for x in nums if x > 2}  # 集合 → 无序、去重
dict_comp = {x: x * 2 for x in nums if x > 2}  # 字典 → key:value
gen_exp1 = (x * 2 for x in nums if x > 2)  # 生成器 → 惰性求值
gen_exp2 = (x * 2 for x in nums if x > 2)  # 生成器 → 惰性求值

print(list_comp)  # [6, 8, 10]
print(set_comp)  # {8, 10, 6}  顺序不固定
print(dict_comp)  # {3: 6, 4: 8, 5: 10}
print(next((gen_exp1), None))  # 6
print(list(gen_exp2))  # [6, 8, 10]
