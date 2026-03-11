from random import randint

__all__ = ["add"]

def add(a, b):
    return a + b

# 只有执行当前文件的，才会被执行
if __name__ == "__main__":
    print(add(10, 12))