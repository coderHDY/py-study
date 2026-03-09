"""
开发一个教务管理系统，在该系统中可以维护和管理学员的成绩信息，具体需求如下：
    1. 添加学生信息：根据提示录入学生姓名、语文、数学、英语成绩，录入完成保存到系统中。
    2. 修改学生信息：要求输入要修改的学生姓名，然后再提示输入语文、数学、英语成绩，输入完成后修改学员信息。
    3. 删除学生信息：要求输入要删除的学生姓名，根据姓名删除学生信息。
    4. 查询学生信息：要求输入要查询的学生姓名，根据姓名查询学生信息并输出。
    5. 列出所有学生：遍历所有学生信息并输出。
    6. 统计班级成绩：统计班级语文、数学、英语成绩的最高分、最低分、平均分，以及语文、数学、英语最高分和最低分的学员姓名。
    7. 退出系统。
"""

students = {
    "张三": {"chinese": 90, "math": 80, "english": 59},
    "李四": {"chinese": 85, "math": 92, "english": 78},
    "王五": {"chinese": 72, "math": 68, "english": 88},
    "赵六": {"chinese": 95, "math": 76, "english": 91},
}

while True:
    cmd = int(
        input(
            """
╔════════════════════════════════╗
║        📚 教务管理系统           ║
╠════════════════════════════════╣
║  1. 添加学生信息                 ║
║  2. 修改学生信息                 ║
║  3. 删除学生信息                 ║
║  4. 查询学生信息                 ║
║  5. 列出所有学生                 ║
║  6. 统计班级成绩                 ║
║  7. 退出系统                    ║
╚════════════════════════════════╝
请输入指令："""
        )
    )
    match cmd:
        case 1:
            # 添加
            # 1. 输入姓名
            name = input("请输入学生姓名")
            # 2. 查重
            exiting_names = set(students.keys())
            if name in exiting_names:
                print("\033[33m⚠️  该学生已存在，请勿重复添加！\033[0m")
                continue
            # 3. 输入语文/数学/英语
            chinese_score = int(input("请输入语文成绩："))
            math_score = int(input("请输入数学成绩："))
            english_score = int(input("请输入英语成绩："))
            # 4. 插入
            students[name] = {
                "chinese": chinese_score,
                "math": math_score,
                "english": english_score,
            }
            print("\033[32m✅ 学生信息添加成功！\033[0m")
        case 2:
            # 修改
            # 1. 输入姓名
            name = input("请输入学生姓名")
            # 2. 查重
            exiting_names = set(students.keys())
            if name not in exiting_names:
                print("\033[33m⚠️  学生不存在！\033[0m")
                continue
            # 3. 输入语文/数学/英语
            chinese_score = int(input("请输入语文成绩："))
            math_score = int(input("请输入数学成绩："))
            english_score = int(input("请输入英语成绩："))
            # 4. 插入
            students[name] = {
                "chinese": chinese_score,
                "math": math_score,
                "english": english_score,
            }
            print("\033[32m✅ 学生信息修改成功！\033[0m")
        case 3:
            # 删除
            # 1. 输入姓名
            name = input("请输入学生姓名")
            # 2. 查重
            exiting_names = set(students.keys())
            if name not in exiting_names:
                print("\033[33m⚠️  学生不存在！\033[0m")
                continue
            # 3. 删除
            del students[name]
            print("\033[32m✅ 学生信息删除成功！\033[0m")
        case 4:
            # 查询
            # 1. 输入姓名
            name = input("请输入学生姓名")
            # 2. 查重
            exiting_names = set(students.keys())
            if name not in exiting_names:
                print("\033[33m⚠️  学生不存在！\033[0m")
                continue
            # 3. 打印学生信息
            print(
                f"{name}\t语文：{chinese_score}\t数学：{math_score}\t英语：{english_score}"
            )
        case 5:
            # 列出所有学生
            for name, info in students.items():
                print(
                    f"{name}\t语文：{info["chinese"]}\t数学：{info["math"]}\t英语：{info["english"]}"
                )
        case 6:
            # 统计班级成绩
            # 班级语文、数学、英语成绩的最高分、最低分、平均分，以及语文、数学、英语最高分和最低分的学员姓名
            chinese_max = max([info["chinese"] for _, info in students.items()])
            chinese_min = min([info["chinese"] for _, info in students.items()])
            chinese_sum = sum([info["chinese"] for _, info in students.items()])
            chinese_avg = round(chinese_sum / len(students.keys()), 2)
            math_max = max([info["math"] for _, info in students.items()])
            math_min = min([info["math"] for _, info in students.items()])
            math_sum = sum([info["math"] for _, info in students.items()])
            math_avg = math_sum / len(students.keys())
            english_max = max([info["english"] for _, info in students.items()])
            english_min = min([info["english"] for _, info in students.items()])
            english_sum = sum([info["english"] for _, info in students.items()])
            english_avg = english_sum / len(students.keys())
            chinese_max_score_name = [name for name,info in students.items() if info["chinese"] == chinese_max]
            chinese_min_score_name = [name for name,info in students.items() if info["chinese"] == chinese_min]
            math_max_score_name = [name for name,info in students.items() if info["math"] == math_max]
            math_min_score_name = [name for name,info in students.items() if info["math"] == math_min]
            english_max_score_name = [name for name,info in students.items() if info["english"] == english_max]
            english_min_score_name = [name for name,info in students.items() if info["english"] == english_min]
            print(f"""
语文最高分: {chinese_max}\t 语文最低分: {chinese_min}\t 语文平均分: {chinese_avg}
数学最高分: {math_max}\t 数学最低分: {math_min}\t 数学平均分: {math_avg}
英语最高分: {english_max}\t 英语最低分: {english_min}\t 英语平均分: {english_avg}
语文最高分同学: {"、".join(chinese_max_score_name)}
语文最低分同学: {"、".join(chinese_min_score_name)}
数学最高分同学: {"、".join(math_max_score_name)}
数学最低分同学: {"、".join(math_min_score_name)}
英语最高分同学: {"、".join(english_max_score_name)}
英语最低分同学: {"、".join(english_min_score_name)}
""")
        case 7:
            break
        case _:
            print("\033[31m❌ 输入错误，请输入 1-7！\033[0m")
