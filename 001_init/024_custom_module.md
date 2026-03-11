# Python 自定义模块规则（完整整理）

## 1) 什么是自定义模块

- 模块本质：一个 `.py` 文件就是一个模块。
- 自定义模块：自己编写的 `.py` 文件，供其他文件复用函数、变量、类。
- 目的：减少重复代码、按功能拆分、方便维护。

示例：

```python
# my_fn.py
def add(a, b):
	return a + b
```

```python
# 023_module_import.py
import my_fn
print(my_fn.add(1, 3))
```

## 2) 自定义模块命名规则

- 文件名必须是合法 Python 标识符。
- 推荐：全小写，多个单词用下划线分隔，如 `user_utils.py`。
- 不要与内置库/第三方库重名，如 `random.py`、`json.py`、`os.py`。
- 不要用中文、空格、减号等不规范命名。

## 3) 导入自定义模块的 4 种常用方式

### 方式 1：`import 模块名`

```python
import my_fn
print(my_fn.add(2, 5))
```

特点：

- 最清晰，调用时要写模块前缀。
- 能明显区分“来自哪个模块”。

### 方式 2：`import 模块名 as 别名`

```python
import my_fn as mf
print(mf.add(2, 5))
```

特点：

- 适合模块名较长时简化书写。

### 方式 3：`from 模块名 import 名称`

```python
from my_fn import add
print(add(2, 5))
```

特点：

- 调用时不用模块前缀。
- 容易与当前文件同名变量/函数冲突。

### 方式 4：`from 模块名 import 名称 as 别名`

```python
from my_fn import add as fn_add
print(fn_add(2, 5))
```

特点：

- 既可简化名称，又可避免冲突。

## 4) `from 模块 import *` 的规则

```python
from my_fn import *
```

- 会把模块里“可导出的名称”全部放到当前命名空间。
- 简单场景可用，但项目中不推荐。
- 原因：可读性差、容易命名冲突、调试困难。

## 5) 模块执行与 `__name__`

每个模块都有一个内置变量 `__name__`：

- 模块被直接运行时：`__name__ == "__main__"`
- 模块被其他文件导入时：`__name__ == "模块名"`

常见写法：

```python
def add(a, b):
	return a + b

if __name__ == "__main__":
	# 只有直接运行本文件才执行
	print(add(1, 2))
```

作用：

- 让“测试代码/演示代码”不在导入时自动执行。

## 6) 模块搜索路径规则（为什么有时导入失败）

`import` 时，Python 会按顺序在以下位置找模块：

- 当前脚本所在目录。
- `PYTHONPATH` 环境变量指定目录。
- Python 安装目录及 `site-packages`。

可查看搜索路径：

```python
import sys
print(sys.path)
```

常见报错：

- `ModuleNotFoundError: No module named 'xxx'`

常见原因：

- 文件不在当前目录或搜索路径里。
- 文件名写错。
- 运行脚本的位置不对。
- 模块名和其他库重名导致冲突。

## 7) 模块中“私有”约定规则

- 以单下划线开头（如 `_helper`）表示“内部使用”，约定为不对外公开。
- 这是约定，不是绝对强制。

## 8) 控制 `from xxx import *` 导出范围：`__all__`

```python
# my_fn.py
__all__ = ["add"]

def add(a, b):
	return a + b

def _secret():
	return "internal"
```

说明：

- 使用 `from my_fn import *` 时，只会导入 `__all__` 中列出的名称。

## 9) 包（package）与自定义模块关系

- 一个文件夹中有 `__init__.py`，通常可视为一个包。
- 包里可以放多个模块，实现分层组织。

结构示例：

```text
utils/
  __init__.py
  math_tools.py
  str_tools.py
```

导入示例：

```python
from utils.math_tools import add
```

## 10) 自定义模块最佳实践

- 一个模块只做一类事，保持职责单一。
- 把可复用逻辑写成函数或类，不要全写在顶层。
- 测试代码放在 `if __name__ == "__main__":` 下。
- 避免循环导入（A 导入 B，B 又导入 A）。
- 模块名、函数名尽量语义化。

## 11) 结合当前项目的最小示例

`my_fn.py`：

```python
def add(a, b):
	return a + b
```

`023_module_import.py`：

```python
import my_fn

print(my_fn.add(1, 3))
print(my_fn.__name__)  # 被导入时通常是模块名
```

---

记忆口诀：

- 写模块：按功能拆分。
- 用模块：优先 `import 模块名`。
- 防误执行：`if __name__ == "__main__":`。
- 找不到模块：先看 `sys.path` 和运行位置。
