# Python 常用内置库与常用方法

下面按库整理高频方法，统一格式：方法 / 作用 / 例子。

## 1) random 随机库

| 方法 | 作用 | 例子 |
|---|---|---|
| random.random() | 生成 [0, 1) 的随机小数 | r = random.random() |
| random.randint(a, b) | 生成 [a, b] 的随机整数 | n = random.randint(1, 10) |
| random.uniform(a, b) | 生成 [a, b] 的随机小数 | x = random.uniform(1.5, 3.5) |
| random.choice(seq) | 从序列中随机选 1 个元素 | c = random.choice(['A', 'B', 'C']) |
| random.sample(seq, k) | 从序列中随机选 k 个不重复元素 | s = random.sample([1,2,3,4], 2) |
| random.shuffle(list) | 原地打乱列表顺序 | random.shuffle(arr) |

## 2) math 数学库

| 方法 | 作用 | 例子 |
|---|---|---|
| math.ceil(x) | 向上取整 | math.ceil(3.1) 结果 4 |
| math.floor(x) | 向下取整 | math.floor(3.9) 结果 3 |
| math.sqrt(x) | 开平方 | math.sqrt(16) 结果 4.0 |
| math.pow(x, y) | 幂运算，返回浮点数 | math.pow(2, 3) 结果 8.0 |
| math.fabs(x) | 绝对值（浮点） | math.fabs(-5.2) 结果 5.2 |
| math.pi | 圆周率常量 | area = math.pi * r * r |

## 3) os 操作系统相关

| 方法 | 作用 | 例子 |
|---|---|---|
| os.getcwd() | 获取当前工作目录 | p = os.getcwd() |
| os.listdir(path) | 列出目录下内容 | files = os.listdir('.') |
| os.mkdir(path) | 创建单级目录 | os.mkdir('data') |
| os.makedirs(path, exist_ok=True) | 创建多级目录 | os.makedirs('a/b/c', exist_ok=True) |
| os.remove(path) | 删除文件 | os.remove('a.txt') |
| os.path.exists(path) | 判断路径是否存在 | ok = os.path.exists('a.txt') |
| os.path.join(a, b) | 拼接路径 | p = os.path.join('data', 'a.csv') |

## 4) sys 解释器与参数

| 方法 | 作用 | 例子 |
|---|---|---|
| sys.argv | 获取命令行参数列表 | print(sys.argv) |
| sys.exit(code) | 退出程序 | sys.exit(0) |
| sys.path | 模块搜索路径列表 | print(sys.path) |
| sys.version | Python 版本信息 | print(sys.version) |
| sys.platform | 当前操作系统平台 | print(sys.platform) |

## 5) time 时间戳与睡眠

| 方法 | 作用 | 例子 |
|---|---|---|
| time.time() | 返回当前时间戳（秒） | ts = time.time() |
| time.sleep(sec) | 程序休眠 sec 秒 | time.sleep(1) |
| time.localtime(ts) | 时间戳转本地时间结构 | t = time.localtime(time.time()) |
| time.strftime(fmt, t) | 时间格式化为字符串 | s = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) |
| time.strptime(s, fmt) | 字符串转时间结构 | t = time.strptime('2026-03-11', '%Y-%m-%d') |

## 6) datetime 日期时间

| 方法 | 作用 | 例子 |
|---|---|---|
| datetime.now() | 获取当前日期时间 | now = datetime.now() |
| datetime.today() | 获取当前本地日期时间 | d = datetime.today() |
| datetime.strptime(s, fmt) | 字符串转 datetime | dt = datetime.strptime('2026-03-11', '%Y-%m-%d') |
| dt.strftime(fmt) | datetime 转格式化字符串 | s = dt.strftime('%Y/%m/%d') |
| timedelta(days=n) | 时间增减 | next_day = now + timedelta(days=1) |
| date.today() | 获取今天日期 | d = date.today() |

## 7) re 正则表达式

| 方法 | 作用 | 例子 |
|---|---|---|
| re.match(pattern, s) | 从字符串开头匹配 | re.match('^a', 'abc') |
| re.search(pattern, s) | 在字符串中搜索第一个匹配 | re.search('b.', 'abcbd') |
| re.findall(pattern, s) | 找到所有匹配并返回列表 | re.findall('\d+', 'a12b34') |
| re.sub(pattern, repl, s) | 替换匹配内容 | re.sub('\s+', '-', 'a b  c') |
| re.split(pattern, s) | 按模式切分字符串 | re.split('[,; ]+', 'a,b; c') |

## 8) csv 表格文件读写

| 方法 | 作用 | 例子 |
|---|---|---|
| csv.reader(f) | 按行读取 csv | for row in csv.reader(f): print(row) |
| csv.writer(f) | 创建写入器 | w = csv.writer(f) |
| writer.writerow(row) | 写入一行 | w.writerow(['name', 'age']) |
| writer.writerows(rows) | 写入多行 | w.writerows([['a',1], ['b',2]]) |
| csv.DictReader(f) | 读取为字典行 | for row in csv.DictReader(f): print(row['name']) |
| csv.DictWriter(f, fieldnames) | 按字段写字典行 | dw = csv.DictWriter(f, fieldnames=['name','age']) |

## 9) json 常见数据交换

| 方法 | 作用 | 例子 |
|---|---|---|
| json.loads(s) | JSON 字符串转 Python 对象 | obj = json.loads('{"a":1}') |
| json.dumps(obj, ensure_ascii=False) | Python 对象转 JSON 字符串 | s = json.dumps({'name':'张三'}, ensure_ascii=False) |
| json.load(f) | 从文件读取 JSON | data = json.load(f) |
| json.dump(obj, f, ensure_ascii=False) | 写 JSON 到文件 | json.dump(data, f, ensure_ascii=False) |

## 10) collections 常用容器增强

| 方法 | 作用 | 例子 |
|---|---|---|
| Counter(iterable) | 统计元素出现次数 | c = Counter('aabcc') |
| defaultdict(type) | 提供默认值的字典 | d = defaultdict(int) |
| deque() | 双端队列，头尾高效增删 | q = deque([1,2,3]) |
| namedtuple(name, fields) | 生成具名元组类型 | Point = namedtuple('Point', ['x','y']) |

## 常见导入方式示例

import random
import math
import os
import sys
import time
from datetime import datetime, date, timedelta
import re
import csv
import json
from collections import Counter, defaultdict, deque, namedtuple
