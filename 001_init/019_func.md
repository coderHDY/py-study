# Python 函数常用知识点

## 1. 基本定义与调用

```python
def 函数名(参数):
    函数体
    return 返回值

# 调用
函数名(参数)
```

```python
def greet(name):
    return f"你好，{name}！"

print(greet("张三"))  # 你好，张三！
```

---

## 2. 参数类型

| 类型 | 说明 | 例子 |
|------|------|------|
| 位置参数 | 按顺序传入 | `def add(a, b)` |
| 默认参数 | 有默认值，可不传 | `def add(a, b=0)` |
| 关键字参数 | 按名称传入 | `add(b=2, a=1)` |
| 可变位置参数 | 接收任意多个参数 → tuple | `def fn(*args)` |
| 可变关键字参数 | 接收任意多个关键字参数 → dict | `def fn(**kwargs)` |

```python
# 默认参数
def greet(name, msg="你好"):
    print(f"{msg}，{name}")

greet("张三")           # 你好，张三
greet("李四", "早上好") # 早上好，李四

# *args
def total(*args):
    return sum(args)

total(1, 2, 3)  # 6

# **kwargs
def info(**kwargs):
    for k, v in kwargs.items():
        print(f"{k}: {v}")

info(name="张三", age=18)
```

---

## 3. 返回值

```python
# 返回单个值
def square(n):
    return n ** 2

# 返回多个值（本质是 tuple）
def min_max(lst):
    return min(lst), max(lst)

lo, hi = min_max([3, 1, 2])  # lo=1, hi=3

# 无 return → 默认返回 None
def say():
    print("hi")

result = say()  # result = None
```

---

## 4. 变量作用域

| 作用域 | 说明 |
|--------|------|
| 局部变量 | 函数内定义，函数外不可访问 |
| 全局变量 | 函数外定义，函数内可读但不能直接改写 |
| `global` | 在函数内声明全局变量后可修改 |

```python
count = 0

def add_count():
    global count   # 声明使用全局变量
    count += 1

add_count()
print(count)  # 1
```

---

## 5. Lambda 匿名函数

```python
# 语法：lambda 参数: 表达式
square = lambda x: x ** 2
add    = lambda x, y: x + y

square(3)   # 9
add(1, 2)   # 3

# 常配合 sorted / map / filter 使用
students = [("张三", 90), ("李四", 75), ("王五", 85)]
sorted(students, key=lambda s: s[1])           # 按成绩升序
sorted(students, key=lambda s: s[1], reverse=True)  # 降序
```

---

## 6. 高阶函数

```python
# map：对每个元素应用函数
list(map(lambda x: x*2, [1,2,3]))   # [2, 4, 6]

# filter：过滤元素
list(filter(lambda x: x>2, [1,2,3,4]))  # [3, 4]

# sorted：排序
sorted([3,1,2])                      # [1, 2, 3]
sorted([3,1,2], reverse=True)        # [3, 2, 1]
```

---

## 7. 递归函数

```python
# 函数调用自身，必须有终止条件
def factorial(n):
    if n <= 1:       # 终止条件
        return 1
    return n * factorial(n - 1)

factorial(5)  # 120
```

---

## 8. 函数注解（类型提示）

```python
def add(a: int, b: int) -> int:
    return a + b

def greet(name: str) -> str:
    return f"你好，{name}"
```

---

## 9. 函数文档字符串（Docstring）

函数定义后**第一行**用三引号写的字符串，用于描述函数用途，可通过 `help()` 或 `.__doc__` 查看。

```python
def add(a: int, b: int) -> int:
    """
    计算两个数的和。

    Args:
        a (int): 第一个数
        b (int): 第二个数

    Returns:
        int: 两数之和
    """
    return a + b

# 查看文档
help(add)       # 打印完整文档
print(add.__doc__)  # 直接访问字符串
```

**常见风格：**

| 风格 | 说明 |
|------|------|
| Google 风格 | `Args:` / `Returns:` / `Raises:` 分块 |
| NumPy 风格 | `Parameters` / `Returns` 用 `---` 分隔 |
| reStructuredText | `:param x:` / `:returns:` （Sphinx 文档生成常用） |

```python
# 最简单写法（单行）
def square(n):
    """返回 n 的平方。"""
    return n ** 2

# Google 风格（推荐）
def divide(a: float, b: float) -> float:
    """
    除法运算。

    Args:
        a (float): 被除数
        b (float): 除数，不能为 0

    Returns:
        float: 商

    Raises:
        ZeroDivisionError: 当 b 为 0 时抛出
    """
    if b == 0:
        raise ZeroDivisionError("除数不能为 0")
    return a / b
```

---

## 10. 常用内置函数速查

| 函数 | 说明 | 例子 |
|------|------|------|
| `len(x)` | 长度 | `len([1,2,3])` → `3` |
| `range(n)` | 生成序列 | `range(1, 6)` → `1~5` |
| `print(*args)` | 输出 | `print("a", "b", sep=",")` |
| `input(prompt)` | 输入 | `input("请输入：")` |
| `type(x)` | 获取类型 | `type(1)` → `<class 'int'>` |
| `isinstance(x, t)` | 判断类型 | `isinstance(1, int)` → `True` |
| `zip(a, b)` | 并行遍历 | `zip([1,2], ["a","b"])` |
| `enumerate(x)` | 带索引遍历 | `enumerate(["a","b"])` |
| `sorted(x)` | 排序返回新列表 | `sorted([3,1,2])` |
| `map(fn, x)` | 映射 | `map(str, [1,2,3])` |
| `filter(fn, x)` | 过滤 | `filter(None, [0,1,2])` |
