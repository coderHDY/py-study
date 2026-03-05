balance = 10000
account = "coderHDY"
password = "pas123"

input_account = input("请输入账号：")
if input_account != account:
    print("无效账户")
    exit()

input_password = input("请输入密码：")
if input_password != password:
    print("密码错误")
    exit()

try:
    amount = int(input("要取的钱："))
except ValueError:
    print("请输入有效金额")
    exit()

if amount > balance:
    print(f"余额不足，当前余额为{balance}元")
    exit()

balance -= amount
print(f"您取走了{amount}元，您的账户还剩{balance}元！")
