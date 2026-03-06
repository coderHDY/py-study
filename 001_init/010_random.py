import random

random_number = random.randint(1, 100)

while True:
    try:
        user_input = int(input("请猜数字："))
        if user_input == random_number:
            print("----------  恭喜你，答对啦！ ————-----------")
            break
        elif user_input > random_number:
            print("大了")
        else:
            print("小了")
    except:
        pass
