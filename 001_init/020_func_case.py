"""
1.定义一个函数：根据传入的底和高计算三角形面积的函数（三角形面积=底*高/2）。
2.定义一个函数：计算传入的字符串中元音字母的个数（元音字母为 aeiouAEIOU）。
3.定义一个函数：计算传入的班级学员高考成绩列表中成绩的最高分、最低分、平均分（保留1位小数），并返回。
"""

# def calc_rec_area(l, h):
#     """
#     三角形面积.

#     Args:
#         l: 底
#         h: 高

#     Returns:
#         底 * 高 / 2
#     """
#     return l * h / 2


# print(calc_rec_area(3, 4))


# def count_vowels(str0: str):
#     """计算元音个数"""
#     vowels = "aeiouAEIOU"
#     count = 0
#     for i in vowels:
#         count += str0.count(i)
#     return count
# print(count_vowels("auwkdyek, Hello"))


# def calc_grade(grades):
#     """
#     Returns:
#         最高分
#         最低分
#         平均分
#     """
#     max_grade = round(max(grades), 1)
#     min_grade = round(min(grades), 1)
#     avg_grade = round(sum(grades) / len(grades),1)
#     return max_grade, min_grade, avg_grade
# grade = [100, 90, 30, 60, 20, 77, 78, 29, 78]
# print(calc_grade(grade))

"""
1．定义一个函数，根据传入的分数，计算对应的分数等级并返回。
• 分数 >= 90：A
• 分数 >= 75：B
• 分数 >= 60：C
• 分数<60:D
2．定义一个函数，用于判断一个字符串是否是回文串，返回bool值。
• 把字符串反转，如果和原字符串相同，就是回文串。（如："Level"，"radar"，"黄山落叶松叶落山黄"）
3.定义一个函数：完成时间转换功能，将传入的秒转换为小时、分钟、秒。
4. 定义一个函数：根据传入的三角形三个边的边长，判定三角形的类型（等边、等腰、普通，或者不能构成三角形）。
"""

# def get_grade_level(grade):
#     if grade > 100 | grade < 0:
#         return "-"
#     if grade >= 90:
#         return "A"
#     if grade >= 75:
#         return "B"
#     if grade >= 60:
#         return "B"
#     if 0 <= grade < 60:
#         return "D"
# print(get_grade_level(77))

# def is_reloop_str(str):
#     return str == str[::-1]
# print("回文字符串" if is_reloop_str("122231") else "非回文字符串")


# def trans_time(time: str):
#     hour,minute,seconds = time.split(":")
#     return f"{hour}小时{minute}分钟{seconds}秒"
# print(trans_time("10:20:00"))


# def print_user(name, age = 0, gender = "男"):
#     print(f"姓名：{name}\t年龄：{age}\t性别：{gender}")
# print_user(age=18, name="coderHDY")


# def get_sum(**args):
#     print(args.get("gender"))
#     # return sum(args)
# print(get_sum(name = 1, age = 2, gender = 3))


# def add(*args):
#     return sum(args)
# def substract(a, b):
#     return a - b
# def calc(*args, func):
#     """this is a func
#     Args:
#         func (doc): func
#     Returns:
#         num: 结果
#     """
#     return func(*args)
# print(calc(3, 4, func = substract))

"""
阶乘
"""

def multi_num(num: int) -> int:
    """函数

    这是一个函数

    Args:
        num(float): 初始值

    Returns:
        num(int): 返回值
    """
    return num * multi_num(num - 1) if num > 1 else num

print(multi_num(3))