"""
根据提供的学生成绩单，完成如下需求：
1. 计算每个学生的总分、各科平均分，然后一并输出出来。
2. 统计各科成绩的最低分、最高分、平均分，并输出。
3． 查找成绩优秀（平均分大于90）的学生，并输出。
"""
students = (
    ("S001", "王林", 85, 92, 78),
    ("S002", "李慕绕", 92, 88, 95),
    ("S003", "十三", 78, 85, 82),
    ("S004", "留牛", 88, 79, 91),
    ("S005", "周铁", 95, 96, 89),
    ("S006", "王卓", 76, 82, 77),
    ("S007", "红蝶", 89, 91, 94),
    ("S008", "徐立国", 75, 69, 82),
    ("S009", "许术", 86, 89, 98),
    ("S010", "通天", 66, 59, 72),
)

stu_len = len(students)
chinese_all = 0
chinese_min = 100
chinese_max = 0
math_all = 0
math_min = 100
math_max = 0
english_all = 0
english_min = 100
english_max = 0
good_stu = []
for s in students:
    all = s[2] + s[3] + s[4]
    # avg_score = round(all / 3, 2)
    avg_score = all / 3
    print(
        f"学号{s[0]} \t 姓名：{s[1]} \t 语文：{s[2]} \t 数学：{s[3]} \t 英语：{s[4]} \t 总分：{all} \t 平均分：{avg_score:.2f}"
    )
    # 语文
    chinese_all += s[2]
    if s[2] > chinese_max:
        chinese_max = s[2]
    if s[2] < chinese_min:
        chinese_min = s[2]
    # 数学
    math_all += s[3]
    if s[3] > math_max:
        math_max = s[3]
    if s[3] < math_min:
        math_min = s[3]

    # 英语
    english_all += s[4]
    if s[4] > english_max:
        english_max = s[4]
    if s[4] < english_min:
        english_min = s[4]
    
    # 优秀学生
    if avg_score > 90:
        good_stu.append(s[1])

print(f"语文 最低分: {chinese_min} 最高分: {chinese_max} 平均分: {chinese_all / stu_len}")
print(f"数学 最低分: {math_min} 最高分: {math_max} 平均分: {math_all / stu_len}")
print(f"数学 最低分: {english_min} 最高分: {english_max} 平均分: {english_all / stu_len}")
print(f"优秀学生：{'、'.join(good_stu)}")


# 推导式
chinese_avg2 = sum([s[2] for s in students]) / stu_len
chinese_max2 = max([s[2] for s in students])
chinese_min2 = min([s[2] for s in students])
print(f"语文平均：{chinese_avg2}")
print(f"语文最高：{chinese_max2}")
print(f"语文平均：{chinese_min2}")

# 推导式所有学生优秀学生
good_stu = [s[1] for s in students if (s[2] + s[3] + s[4]) / 3 > 90]
print(f"好学生们：{"、".join(good_stu)}")

# 解包
for s in students:
    id,name,chinese,math,english = s
    print(f"学号{id} \t 姓名：{name} \t 语文：{chinese} \t 数学：{math} \t 英语：{english}")