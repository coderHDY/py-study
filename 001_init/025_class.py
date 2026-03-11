class StudentSystem:
    tip = """
请输入指令：
1. 添加学生
2. 修改学生成绩
3. 删除学生成绩
4. 查询学生成绩
5. 展示所有学生成绩
6. 退出系统
"""

    def __init__(self):
        self.stu_list: list[Student] = []
        print(self.tip)
        while True:
            cmd = input("请输入指令：")
            match cmd:
                case "1":
                    self.add_stu()
                case "2":
                    self.modify_stu()
                case "3":
                    self.del_stu()
                case "4":
                    self.search_stu()
                case "5":
                    self.show_all_stu()
                case "6":
                    Log.success("感谢使用，再见！")
                    break
                case _:
                    Log.error("指令错误！请重新输入！")

    def check_stu_exit(self, name):
        return self.get_stu(name) is not None

    def get_stu(self, name):
        return next((s for s in self.stu_list if s.name == name), None)

    def _input_scores(self):
        return (
            input("请输入学生的语文成绩："),
            input("请输入学生的数学成绩："),
            input("请输入学生的英语成绩："),
        )

    def add_stu(self):
        name = input("请输入学生的姓名：")
        if self.check_stu_exit(name):
            Log.error("学生已存在！")
            return
        chinese_score, math_score, english_score = self._input_scores()
        Log.success("添加成功！")
        self.stu_list.append(Student(name, chinese_score, math_score, english_score))

    def modify_stu(self):
        name = input("请输入学生的姓名：")
        stu = self.get_stu(name)
        if stu is None:
            Log.error("学生不存在！")
            return
        chinese_score, math_score, english_score = self._input_scores()
        stu.modify(chinese_score, math_score, english_score)
        Log.success("修改成功！")

    def del_stu(self):
        name = input("请输入学生的姓名：")
        stu = self.get_stu(name)
        if stu is None:
            Log.error("学生不存在！")
            return
        self.stu_list.remove(stu)
        Log.success("删除成功！")

    def search_stu(self):
        name = input("请输入学生的姓名：")
        stu = self.get_stu(name)
        if stu is None:
            Log.error("学生不存在！")
            return
        print(stu)

    def show_all_stu(self):
        [print(s) for s in self.stu_list]


class Log:
    @classmethod
    def success(self, str):
        print(f"\033[32m✅ {str}\033[0m")

    @classmethod
    def warn(self, str):
        print(f"\033[33m⚠️  {str}\033[0m")

    @classmethod
    def error(self, str):
        print(f"\033[31m❌ {str}\033[0m")


class Student:
    def __init__(self, name, chinese_score=0, math_score=0, english_score=0):
        self.name = name
        self.chinese_score = int(chinese_score)
        self.math_score = int(math_score)
        self.english_score = int(english_score)

    def modify(self, chinese_score=0, math_score=0, english_score=0):
        self.chinese_score = int(chinese_score)
        self.math_score = int(math_score)
        self.english_score = int(english_score)

    def __str__(self):
        return f"姓名: {self.name}\t 语文: {self.chinese_score}\t 数学: {self.math_score}\t 英语: {self.english_score}"


StudentSystem()
