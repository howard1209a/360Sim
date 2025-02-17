def process_4g_network_trace():
    # 打开log文件读取数据
    input_file = '/Users/howard1209a/Desktop/codes/E3PO/e3po/source/network_trace/report_car_0008.log'
    output_file = '/Users/howard1209a/Desktop/codes/E3PO/e3po/source/network_trace/report_car_0008.txt'

    with open(input_file, 'r') as f:
        # 读取文件中的每一行
        lines = f.readlines()

    # 创建一个新的文件用于输出结果
    with open(output_file, 'w') as f:
        for i, line in enumerate(lines):
            # 拆分每一行，假设数据由空格分隔
            columns = line.strip().split()

            # 提取倒数第二列
            second_last_column = columns[-2]

            # 生成第一列的值：0, 1000, 2000, ...
            first_column_value = i * 1000

            # 写入到新文件
            f.write(f"{first_column_value} {second_last_column}\n")


if __name__ == '__main__':
    process_4g_network_trace()
