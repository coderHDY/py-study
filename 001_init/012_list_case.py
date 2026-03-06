# arr = []
# for i in range(10):
#     ipt_num = int(input(f"请输入第{i + 1}个数字"))
#     arr.append(ipt_num)


# arr = [1, 11, 2, 3]
# arr.sort()
# sum = sum(arr)
# average = sum / len(arr)
# print(sum)
# print(average)


# arr1 = [1, 2, 3]
# arr2 = [4, 5, 6]
# arr3 = [*arr1, *arr2]
# print(arr3)

# ## 1-20平方列表
# mix_list = []
# for i in range(20):
#     mix_list.append((i + 1) ** 2)
# print(mix_list)

# ## 下列数字的偶数的平方
# arr1 = [32, 32, 23, 2, 3, 4, 35, 24525, 26, 2, 62, 2552, 6, 7, 73, 4, 5, 23]
# arr2 = []
# for i in arr1:
#     if i % 2 == 0:
#         num_pre = i ** 2
#         if num_pre not in arr2:
#             arr2.append(num_pre)
# print(arr2)

# # 列表推导式1
# num_list2 = [(i + 1) ** 2 for i in range(20)]
# print(num_list2)

# 列表推导式2
num_list3 = [(i + 1) ** 2 for i in range(20) if i % 2 == 0 or i == 3]
print(num_list3)
