# # global声明后才可以使用全局变量
# count = 0
# def add_count():
#     global count   # 声明使用全局变量
#     count += 1
# add_count()
# print(count)  # 1


# shop_menu = {
#     "鸡蛋": {"price": 6.5, "num": 10},
#     "牛奶": {"price": 35.0, "num": 3},
#     "面包": {"price": 12.8, "num": 5},
#     "苹果": {"price": 18.9, "num": 6},
#     "矿泉水": {"price": 2.5, "num": 12},
#     "薯片": {"price": 9.9, "num": 4},
#     "酸奶": {"price": 15.0, "num": 8},
#     "火腿肠": {"price": 3.5, "num": 20},
#     "方便面": {"price": 4.8, "num": 10},
#     "橙汁": {"price": 8.0, "num": 6},
# }

# sort = sorted(shop_menu.items(), key=lambda x:x[1]["price"], reverse=True)
# print(sort)

# # map
# m = list(map(lambda x: x ** 2, [1, 2, 3]))
# print(m)

# # filter
# f = list(filter(lambda x: x > 2, [1, 2, 3, 4]))
# print(f)

# # sorted
# s = sorted([1, 2, 2, 1, 6, 4, 3, 7], key=lambda x: x, reverse=True)
# print(s)

# log函数
def log_success(str):
    """
    错误log
    """
    print(f"\033[32m{str}\033[0m")
def log_warn(str):
    print(f"\033[33m{str}\033[0m")
def log_error(str):
    print(f"\033[31m{str}\033[0m")

log_error("错误！！！！！！！")
log_success("成功！！！！！！！")
log_warn("警告！！！！！！！")

help(log_success)

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

def square(n):
    """返回 n 的平方。"""
    return n ** 2
