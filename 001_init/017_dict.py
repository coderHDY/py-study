"""
开发一个购物车管理系统，实现商品信息的添加、修改、删除、查询功能。系统使用字典结构存储商品数据，
通过控制台菜单与用户交互。具体功能如下：
    1．添加购物车：用户根据提示录入商品名称、以及该商品的价格、数量，保存该商品信息到购物车。
    2． 修改购物车：要求用户输入要修改的购物车商品名称，然后再提示输入该商品的价格、数量，输入完成后修改该商品信息。
    3．删除购物车：要求用户输入要删除的购物车名称，根据名称删除购物车中的商品。
    4.查询购物车：将购物车中的商品信息展示出来，格式为：“商品名称：xxx，商品价格：xxx，商品数量：xxx"。
    5．退出购物车
"""

shop_menu = {
    "鸡蛋": {"price": 6.5, "num": 10},
    "牛奶": {"price": 35.0, "num": 3},
    "面包": {"price": 12.8, "num": 5},
    "苹果": {"price": 18.9, "num": 6},
    "矿泉水": {"price": 2.5, "num": 12},
    "薯片": {"price": 9.9, "num": 4},
    "酸奶": {"price": 15.0, "num": 8},
    "火腿肠": {"price": 3.5, "num": 20},
    "方便面": {"price": 4.8, "num": 10},
    "橙汁": {"price": 8.0, "num": 6},
}

while True:
    user_cmd = int(
        input(
"""
╔══════════════════════════╗
║       🛒 购物车管理系统     ║
╠══════════════════════════╣
║  1. 添加商品               ║
║  2. 修改商品               ║
║  3. 删除商品               ║
║  4. 查询购物车             ║
║  5. 退出系统               ║
╚══════════════════════════╝
请输入指令：
"""
        )
    )

    match user_cmd:
        case 1:
            # 1. 输入
            name = input("商品名称: ")
            price = round(float(input("商品价格: ")), 2)
            num = int(input("商品数量: "))
            # 2. 插入menus
            # "鸡蛋": {"price": 6.5, "num": 10},
            shop_menu[name] = {"price": price, "num": num}
        case 2:
            name = input("商品名称: ")
            if name not in shop_menu:
                print("\033[33m⚠️  商品不存在！\033[0m")
                continue
            price = round(float(input("商品价格: ")), 2)
            num = int(input("商品数量: "))
            # 2. 修改menus,
            shop_menu[name] = {"price": price, "num": num}
        case 3:
            # 1. 输入
            name = input("商品名称: ")
            # 2. 删除menus
            if name not in shop_menu:
                print("\033[33m⚠️  商品不存在，无法删除！\033[0m")
                continue
            del shop_menu[name]
        case 4:
            # 1. 输入
            name = input("商品名称: ")
            # 2. 查询menus
            if name not in shop_menu:
                print("\033[33m⚠️  商品不存在！\033[0m")
                continue
            good = shop_menu[name]
            good_price = good["price"]
            good_num = good["num"]
            print(f"名称：{name}\t 数量：{good_num}\t 价格：{good_price}")
            
        case 5:
            break
        case _:
            print("\033[31m❌ 非法操作，请输入 1-5！\033[0m")