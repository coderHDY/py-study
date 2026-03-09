"""
根据提供的班级学生的选课情况，完成如下需求：
    1． 找出同时选修了法语和艺术的学生
    2. 找出同时选修了所有四门课程的学生
    3. 找出选修了足球，但是没有选修篮球的学生
    4.统计每一个学生选修的课程数量
"""

# 选修足球学生名单
football_set = {
    "王林",
    "曾牛",
    "徐立国",
    "遁天",
    "天运子",
    "韩立",
    "厉飞雨",
    "乌丑",
    "紫灵",
}
# 选修篮球学生名单
basketball_set = {
    "张铁",
    "墨居仁",
    "王林",
    "姜老道",
    "曾牛",
    "王蝉",
    "韩立",
    "天运子",
    "李化元",
    "厉飞雨",
    "云露",
}
# 选修法语学生名单
french_set = {
    "许木",
    "王卓",
    "十三",
    "虎咆",
    "姜老道",
    "天运子",
    "红蝶",
    "厉飞雨",
    "韩立",
    "曾牛",
}
# 选修艺术学生名单
art_set = {"遁天", "天运子", "韩立", "虎咆", "姜老道", "紫灵"}


# 1． 找出同时选修了法语和艺术的学生
print(french_set & art_set)

# 2. 找出同时选修了所有四门课程的学生
print(football_set & basketball_set & french_set & art_set)

# 3. 找出选修了足球，但是没有选修篮球的学生
print(football_set - basketball_set)

# 4.统计每一个学生选修的课程数量
all_stu = tuple(football_set | basketball_set | french_set | art_set)
print(all_stu)
for s in all_stu:
    num = 0
    if s in football_set:
        num += 1
    if s in basketball_set:
        num += 1
    if s in french_set:
        num += 1
    if s in art_set:
        num += 1
    print(f"{s}参加了\t{num}\t门课程")

# 4. 方法2
all_stu2 = tuple(football_set | basketball_set | french_set | art_set)
all_join_name = [*football_set , *basketball_set , *french_set , *art_set]
print(f"{"\r\n".join([f"{s}: {all_join_name.count(s)}" for s in all_stu2])}")