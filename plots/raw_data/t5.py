import csv

black_ratio_list = []
is_rebuffer_list = []

with open('record/SPB-360_record.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        clock = int(row['clock'])
        # 筛选整数秒：0-60秒，且clock是1000的倍数
        if clock <= 60000 and clock % 1000 == 0:
            # 提取black_ratio_in_view
            black_ratio = float(row['black_ratio_in_view'])
            black_ratio_list.append(black_ratio)

            # 提取is_rebuffer并转换为布尔值
            is_rebuffer_str = row['is_rebuffer']
            is_rebuffer_bool = is_rebuffer_str.lower() == 'true'
            is_rebuffer_list.append(is_rebuffer_bool)

print(f"整数秒个数: {len(black_ratio_list)}")
print(f"对应的秒数: {list(range(0, 61))}")
print(f"\nblack_ratio_in_view值列表: {black_ratio_list}")
print(f"\nis_rebuffer值列表: {is_rebuffer_list}")

# 如果需要将两个列表合并显示
print("\n秒数, black_ratio_in_view, is_rebuffer:")
for i in range(len(black_ratio_list)):
    print(f"{i}秒: black_ratio={black_ratio_list[i]}, is_rebuffer={is_rebuffer_list[i]}")