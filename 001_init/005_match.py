score = 59

match score:
    case 90:
        print("A")
    case 80:
        print("B")
    case 70:
        print("C")
    case 60 | 61:
        print("D")
    case _:
        print("不及格")
