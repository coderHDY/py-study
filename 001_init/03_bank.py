have_money = 10000
account = "coderHDY"
password = "pas123"

input_account = input("请输入账号：")

if (input_account != account):
    print("无效账户")
    exit()
else:
    input_password = input("请输入密码：")
    if input_password != password:
        print("密码错误")
        exit()
    else: 
        input_get_money = int(input("要取的钱："))
        print(f"您取走了{input_get_money}元，您的账户还剩{have_money - input_get_money}元！")
