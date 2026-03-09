# Python Dict 常用语法

## 创建

| 方法 | 作用 | 例子 |
|------|------|------|
| `{k: v}` | 直接创建字典 | `d = {"name": "王林", "age": 18}` |
| `dict(k=v)` | 关键字参数创建 | `dict(name="王林", age=18)` |
| `dict([(k,v)])` | 列表转字典 | `dict([("a",1),("b",2)])` |
| `{}` | 创建空字典 | `d = {}` |
| `dict.fromkeys(keys, v)` | 用键列表创建，值相同 | `dict.fromkeys(["a","b"], 0)` → `{"a":0,"b":0}` |

---

## 访问

| 方法 | 作用 | 例子 |
|------|------|------|
| `d[key]` | 获取值，不存在则报错 | `d["name"]` → `"王林"` |
| `d.get(key)` | 获取值，不存在返回 None | `d.get("age")` → `18` |
| `d.get(key, default)` | 获取值，不存在返回默认值 | `d.get("sex", "未知")` → `"未知"` |
| `d.keys()` | 获取所有键 | `d.keys()` → `dict_keys(["name","age"])` |
| `d.values()` | 获取所有值 | `d.values()` → `dict_values(["王林",18])` |
| `d.items()` | 获取所有键值对 | `d.items()` → `dict_items([("name","王林")])` |

---

## 增 / 改

| 方法 | 作用 | 例子 |
|------|------|------|
| `d[key] = v` | 新增或修改键值 | `d["score"] = 99` |
| `d.update(dict2)` | 批量更新/合并字典 | `d.update({"age": 20, "city": "北京"})` |
| `d.setdefault(key, v)` | 键不存在时插入默认值，已存在不修改 | `d.setdefault("age", 0)` |

---

## 删

| 方法 | 作用 | 例子 |
|------|------|------|
| `del d[key]` | 删除指定键，不存在则报错 | `del d["age"]` |
| `d.pop(key)` | 删除并返回值，不存在则报错 | `d.pop("age")` → `18` |
| `d.pop(key, default)` | 删除并返回值，不存在返回默认值 | `d.pop("x", None)` |
| `d.popitem()` | 删除并返回最后一个键值对 | `d.popitem()` → `("age", 18)` |
| `d.clear()` | 清空字典 | `d.clear()` |

---

## 判断

| 方法 | 作用 | 例子 |
|------|------|------|
| `key in d` | 判断键是否存在 | `"name" in d` → `True` |
| `key not in d` | 判断键是否不存在 | `"x" not in d` → `True` |
| `len(d)` | 获取键值对数量 | `len(d)` → `2` |

---

## 遍历

```python
d = {"name": "王林", "age": 18}

# 遍历键
for key in d:
    print(key)

# 遍历值
for v in d.values():
    print(v)

# 遍历键值对（最常用）
for key, value in d.items():
    print(key, value)
```

---

## 推导式

```python
# 字典推导式
d = {s[0]: s[1] for s in students}          # 学号 -> 姓名
d = {k: v*2 for k, v in d.items()}          # 值翻倍
d = {k: v for k, v in d.items() if v > 80}  # 过滤
```

---

## 合并字典（Python 3.9+）

```python
d1 = {"a": 1}
d2 = {"b": 2}
d3 = d1 | d2   # {"a": 1, "b": 2}
```
