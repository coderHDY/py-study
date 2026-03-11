# Python 面向对象（OOP）完整知识点

## 1) 核心概念

| 概念 | 说明 |
|---|---|
| 类（Class）| 模板 / 蓝图，定义属性和方法 |
| 对象（Object）| 类的实例，是真正"有数据"的个体 |
| 属性（Attribute）| 对象拥有的数据（变量） |
| 方法（Method）| 对象能做的事（函数） |
| 封装（Encapsulation）| 把数据和行为包在类里，控制访问权限 |
| 继承（Inheritance）| 子类复用父类的属性和方法 |
| 多态（Polymorphism）| 同一方法在不同类里有不同实现 |

---

## 2) 定义类与创建对象

```python
class Student:
    pass

s1 = Student()   # 创建对象（实例化）
s2 = Student()   # 每次都是独立对象
```

- 类名约定首字母大写，驼峰命名（`MyClass`）。

---

## 3) `__init__` 构造方法

- 对象创建时自动执行，用来初始化实例属性。
- 第一个参数必须是 `self`，代表当前对象本身。

```python
class Student:
    def __init__(self, name, age):
        self.name = name   # 实例属性
        self.age = age

s1 = Student("张三", 18)
print(s1.name)   # 张三
print(s1.age)    # 18
```

---

## 4) 实例属性 vs 类属性

```python
class Student:
    school = "Python学院"   # 类属性：所有对象共享

    def __init__(self, name):
        self.name = name    # 实例属性：每个对象独有

s1 = Student("张三")
s2 = Student("李四")

print(Student.school)   # 类属性通过类访问
print(s1.school)        # 也可以通过对象访问（先找实例属性，找不到再找类属性）
print(s1.name)          # 实例属性
```

规则：
- 修改类属性用 `Student.school = "新名字"`，通过 `s1.school = ...` 实际是给该实例新增了实例属性，不影响类属性。

---

## 5) 实例方法 / 类方法 / 静态方法

### 5.1 实例方法（最常用）

```python
class Student:
    def __init__(self, name):
        self.name = name

    def greet(self):          # 第一参数固定是 self
        print(f"我叫 {self.name}")

s1 = Student("张三")
s1.greet()
```

### 5.2 类方法 `@classmethod`

```python
class Student:
    school = "Python学院"

    @classmethod
    def show_school(cls):     # 第一参数固定是 cls（类本身）
        print(cls.school)

Student.show_school()
```

- 适合操作类属性，无需实例。

### 5.3 静态方法 `@staticmethod`

```python
class MathTools:
    @staticmethod
    def add(a, b):            # 既不需要 self 也不需要 cls
        return a + b

print(MathTools.add(3, 5))
```

- 与类有逻辑关联，但不访问类/实例属性时使用。

---

## 6) 访问权限（封装）

| 写法 | 含义 |
|---|---|
| `name` | 公有属性/方法，任何地方都可访问 |
| `_name` | 约定私有（保护），不建议外部直接用 |
| `__name` | 名称改写（name mangling），强制约束外部访问 |

```python
class Person:
    def __init__(self, name, age):
        self.name = name         # 公有
        self._id = "123456"      # 约定保护
        self.__salary = 5000     # 私有（会被改写为 _Person__salary）

    def get_salary(self):
        return self.__salary     # 类内部可以访问

p = Person("张三", 25)
print(p.name)           # 可以
print(p._id)            # 可以（但约定不这样用）
# print(p.__salary)     # 报错！
print(p._Person__salary) # 强行访问（不推荐）
print(p.get_salary())   # 推荐：通过方法访问
```

---

## 7) 属性装饰器 `@property`

将方法当属性用，同时保护内部数据。

```python
class Circle:
    def __init__(self, radius):
        self.__radius = radius

    @property
    def radius(self):              # getter
        return self.__radius

    @radius.setter
    def radius(self, value):       # setter，带验证
        if value <= 0:
            raise ValueError("半径必须大于 0")
        self.__radius = value

    @property
    def area(self):                # 只读计算属性
        import math
        return math.pi * self.__radius ** 2

c = Circle(5)
print(c.radius)   # 5
c.radius = 10     # 调用 setter
print(c.area)     # 自动计算
```

---

## 8) 继承

```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        print(f"{self.name} 发出声音")

class Dog(Animal):              # Dog 继承 Animal
    def speak(self):            # 方法重写（Override）
        print(f"{self.name} 汪汪叫")

class Cat(Animal):
    def speak(self):
        print(f"{self.name} 喵喵叫")

d = Dog("旺财")
d.speak()   # 汪汪叫
```

继承规则：
- 子类继承父类所有公有属性和方法。
- 子类可重写（override）父类方法。
- 子类可新增自己的属性和方法。
- 子类对象可以当父类对象使用（向上转型）。

---

## 9) `super()` 调用父类

```python
class Animal:
    def __init__(self, name):
        self.name = name

class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)   # 调用父类 __init__
        self.breed = breed

d = Dog("旺财", "柴犬")
print(d.name, d.breed)
```

---

## 10) 多继承

```python
class A:
    def hello(self):
        print("A")

class B:
    def hello(self):
        print("B")

class C(A, B):    # 先找 A，再找 B（MRO 顺序）
    pass

C().hello()     # A
print(C.__mro__)  # 查看方法解析顺序
```

---

## 11) 多态

```python
class Animal:
    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        return "汪"

class Cat(Animal):
    def speak(self):
        return "喵"

def let_speak(animal):   # 只关心有没有 speak 方法
    print(animal.speak())

let_speak(Dog())   # 汪
let_speak(Cat())   # 喵
```

---

## 12) 常用魔法方法（双下划线方法）

| 方法 | 触发时机 | 示例 |
|---|---|---|
| `__init__` | 创建对象 | `Student("张三", 18)` |
| `__str__` | `print(obj)` / `str(obj)` | 返回可读字符串 |
| `__repr__` | 调试 / `repr(obj)` | 返回开发者字符串 |
| `__len__` | `len(obj)` | 返回长度 |
| `__eq__` | `==` 比较 | 判断相等 |
| `__lt__` / `__gt__` | `<` / `>` 比较 | 排序比较 |
| `__add__` | `+` 运算 | 运算符重载 |
| `__contains__` | `in` 判断 | `x in obj` |
| `__iter__` / `__next__` | `for` 循环迭代 | 自定义迭代器 |
| `__del__` | 对象被销毁时 | 清理资源 |

```python
class Student:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __str__(self):
        return f"Student({self.name}, {self.age})"

    def __eq__(self, other):
        return self.name == other.name and self.age == other.age

s1 = Student("张三", 18)
print(s1)              # Student(张三, 18)
s2 = Student("张三", 18)
print(s1 == s2)        # True
```

---

## 13) `__dict__` 与常用内置方法

```python
class Student:
    school = "Python学院"
    def __init__(self, name):
        self.name = name

s = Student("张三")
print(s.__dict__)          # {'name': '张三'}  实例属性字典
print(Student.__dict__)    # 类的所有属性和方法
print(isinstance(s, Student))   # True  判断是否是某类的实例
print(issubclass(Student, object))  # True  判断继承关系
print(hasattr(s, 'name'))  # True  是否有某属性
print(getattr(s, 'name'))  # 张三  获取属性值
setattr(s, 'age', 18)      # 动态设置属性
delattr(s, 'age')          # 删除属性
print(type(s))             # <class '__main__.Student'>
```

---

## 14) 抽象类（抽象方法）

需要 `abc` 模块，强制子类实现某些方法。

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self):   # 子类必须实现此方法
        pass

class Circle(Shape):
    def __init__(self, r):
        self.r = r
    def area(self):
        import math
        return math.pi * self.r ** 2

# Shape()   # 报错！抽象类不能直接实例化
c = Circle(5)
print(c.area())
```

---

## 15) 知识点速查表

| 知识点 | 关键写法 |
|---|---|
| 定义类 | `class MyClass:` |
| 构造方法 | `def __init__(self, ...):` |
| 实例属性 | `self.name = value` |
| 类属性 | 直接写在类体内 |
| 实例方法 | `def method(self):` |
| 类方法 | `@classmethod  def method(cls):` |
| 静态方法 | `@staticmethod  def method():` |
| 私有属性 | `self.__attr` |
| 属性装饰器 | `@property` |
| 继承 | `class Dog(Animal):` |
| 调用父类 | `super().__init__(...)` |
| 方法重写 | 子类定义同名方法 |
| 抽象类 | 继承 `ABC`，用 `@abstractmethod` |
