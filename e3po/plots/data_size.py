import os

def get_folder_size(folder_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if os.path.isfile(file_path):  # 避免链接或无效文件
                total_size += os.path.getsize(file_path)
    return total_size

def format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes / 1024**2:.2f} MB"
    else:
        return f"{size_bytes / 1024**3:.2f} GB"

if __name__ == "__main__":
    folder = r"D:\codes\360Sim\e3po\source\video\dash_gop8s"  # 例如："./mydata"
    size = get_folder_size(folder)
    print(f"总大小：{format_size(size)}")
