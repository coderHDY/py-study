# Python 常用内置语法总结

## 数字 / 序列类

| 语法 | 作用 | 例子 |
|------|------|------|
| `len(x)` | 获取长度 | `len([1,2,3])` → `3` |
| `sum(x)` | 求和 | `sum([1,2,3])` → `6` |
| `max(x)` | 最大值 | `max([1,2,3])` → `3` |
| `min(x)` | 最小值 | `min([1,2,3])` → `1` |
| `abs(x)` | 绝对值 | `abs(-5)` → `5` |
| `round(x, n)` | 四舍五入保留n位小数 | `round(3.1415, 2)` → `3.14` |
| `pow(x, y)` | x的y次方 | `pow(2, 3)` → `8` |
| `range(n)` | 生成数字序列 | `range(3)` → `0,1,2` |

---

## 类型转换类

| 语法 | 作用 | 例子 |
|------|------|------|
| `int(x)` | 转整数 | `int("3")` → `3` |
| `float(x)` | 转浮点数 | `float("3.14")` → `3.14` |
| `str(x)` | 转字符串 | `str(100)` → `"100"` |
| `bool(x)` | 转布尔值 | `bool(0)` → `False` |
| `list(x)` | 转列表 | `list("abc")` → `['a','b','c']` |
| `tuple(x)` | 转元组 | `tuple([1,2])` → `(1,2)` |

---

## 字符串类

| 语法 | 作用 | 例子 |
|------|------|------|
| `str.upper()` | 转大写 | `"abc".upper()` → `"ABC"` |
| `str.lower()` | 转小写 | `"ABC".lower()` → `"abc"` |
| `str.strip()` | 去除首尾空格 | `" ab ".strip()` → `"ab"` |
| `str.split(sep)` | 按分隔符拆分成列表 | `"a,b".split(",")` → `['a','b']` |
| `sep.join(list)` | 列表合并成字符串 | `",".join(['a','b'])` → `"a,b"` |
| `str.replace(a,b)` | 替换字符串 | `"ab".replace("a","x")` → `"xb"` |
| `str.find(x)` | 查找子串位置 | `"abc".find("b")` → `1` |
| `str.count(x)` | 统计子串出现次数 | `"aaa".count("a")` → `3` |
| `str.startswith(x)` | 是否以x开头 | `"abc".startswith("a")` → `True` |
| `str.endswith(x)` | 是否以x结尾 | `"abc".endswith("c")` → `True` |
| `str[::-1]` | 字符串反转 | `"abc"[::-1]` → `"cba"` |

---

## 列表类

| 语法 | 作用 | 例子 |
|------|------|------|
| `list.append(x)` | 末尾追加元素 | `[1,2].append(3)` → `[1,2,3]` |
| `list.insert(i, x)` | 指定位置插入 | `[1,2].insert(0,0)` → `[0,1,2]` |
| `list.remove(x)` | 删除第一个匹配值 | `[1,2,2].remove(2)` → `[1,2]` |
| `list.pop(i)` | 删除并返回指定位置元素 | `[1,2,3].pop(0)` → `1` |
| `list.sort()` | 升序排序（原地） | `[3,1,2].sort()` → `[1,2,3]` |
| `list.reverse()` | 反转列表（原地） | `[1,2,3].reverse()` → `[3,2,1]` |
| `list.index(x)` | 查找元素位置 | `[1,2,3].index(2)` → `1` |
| `list.count(x)` | 统计元素出现次数 | `[1,1,2].count(1)` → `2` |
| `sorted(x)` | 返回新的排序列表 | `sorted([3,1,2])` → `[1,2,3]` |

---

## 判断 / 遍历类

| 语法 | 作用 | 例子 |
|------|------|------|
| `in` | 判断是否在序列中 | `2 in [1,2,3]` → `True` |
| `not in` | 判断是否不在序列中 | `5 not in [1,2]` → `True` |
| `isinstance(x, type)` | 判断类型 | `isinstance(1, int)` → `True` |
| `enumerate(x)` | 遍历带索引 | `for i,v in enumerate(['a','b'])` |
| `zip(a, b)` | 同时遍历多个序列 | `for x,y in zip([1,2],[3,4])` |
| `map(fn, x)` | 对序列每个元素应用函数 | `list(map(str,[1,2]))` → `['1','2']` |
| `filter(fn, x)` | 过滤序列 | `list(filter(lambda x:x>1,[1,2,3]))` → `[2,3]` |

---

## 输入 / 输出类

| 语法 | 作用 | 例子 |
|------|------|------|
| `print(x)` | 输出 | `print("hello")` |
| `input(x)` | 获取用户输入（返回字符串） | `name = input("请输入")` |
| `f"..."` | 格式化字符串 | `f"分数:{score:.2f}"` |
