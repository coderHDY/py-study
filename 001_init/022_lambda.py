data_list = [
    "C",
    "C++",
    "Python",
    "Java",
    "JavaScript",
    "Go",
    "Rust",
    "Kotlin",
    "Swift",
    "TypeScript",
]

data_list.sort(key=lambda x: len(x), reverse=True)

print(data_list)
