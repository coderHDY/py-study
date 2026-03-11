count = 0

def add_count():
    """你好

    我的目标：
    """
    global count   # 声明使用全局变量
    count += 1

add_count()
print(count)  # 1