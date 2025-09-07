import os
import json
import argparse
import time
from datetime import datetime
from pathlib import Path

# 配置目标文件和目录
MD_FILE_PATH = os.path.join("src", "upload.md")  # Markdown文件路径
UPLOAD_RECORDS = "upload_records.json"  # 上传记录JSON文件

def ensure_directory_exists(file_path):
    """确保文件所在目录存在"""
    directory = os.path.dirname(file_path)
    Path(directory).mkdir(parents=True, exist_ok=True)
    # 添加调试信息
    print(f"确保目录存在: {directory} - {'存在' if os.path.exists(directory) else '已创建'}")

def load_records():
    """加载已有的上传记录"""
    if os.path.exists(UPLOAD_RECORDS):
        file_size = os.path.getsize(UPLOAD_RECORDS)
        print(f"加载记录文件: {UPLOAD_RECORDS} (大小: {file_size} bytes)")
        with open(UPLOAD_RECORDS, 'r', encoding='utf-8') as f:
            return json.load(f)
    print(f"记录文件不存在，创建新列表: {UPLOAD_RECORDS}")
    return []

def save_record(filename, file_path, timestamp):
    """保存新的上传记录"""
    records = load_records()
    
    # 处理带有Z后缀的ISO时间格式
    if timestamp.endswith('Z'):
        timestamp = timestamp.replace('Z', '+00:00')
    
    # 创建新记录
    new_record = {
        "filename": filename,
        "path": file_path,
        "timestamp": timestamp,
        "formatted_date": datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # 添加到记录列表开头
    records.insert(0, new_record)
    
    # 保存更新后的记录
    with open(UPLOAD_RECORDS, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    
    # 验证保存结果
    if os.path.exists(UPLOAD_RECORDS):
        print(f"记录已保存: {UPLOAD_RECORDS} (新大小: {os.path.getsize(UPLOAD_RECORDS)} bytes)")
    else:
        print(f"警告: 记录文件未创建成功")
        
    return new_record

def update_markdown_file(new_record):
    """更新Markdown文件，添加新的上传记录"""
    ensure_directory_exists(MD_FILE_PATH)
    
    # 读取现有内容
    content = ""
    if os.path.exists(MD_FILE_PATH):
        file_size = os.path.getsize(MD_FILE_PATH)
        print(f"读取现有MD文件: {MD_FILE_PATH} (大小: {file_size} bytes)")
        with open(MD_FILE_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        # 如果文件不存在，创建并添加标题和表格头
        print(f"MD文件不存在，创建新文件: {MD_FILE_PATH}")
        content = "# 上传文件记录\n\n"
        content += "以下是所有上传文件的记录，按上传时间倒序排列：\n\n"
        content += "| 文件名 | 上传时间 | 文件路径 |\n"
        content += "|--------|----------|----------|\n"
    
    # 检查表格头是否存在，如果不存在则添加
    if "| 文件名 | 上传时间 | 文件路径 |" not in content:
        print("表格头不存在，添加表格结构")
        content += "\n| 文件名 | 上传时间 | 文件路径 |\n"
        content += "|--------|----------|----------|\n"
    
    # 构建新记录行
    new_row = f"| {new_record['filename']} | {new_record['formatted_date']} | {new_record['path']} |\n"
    print(f"添加新记录行: {new_row.strip()}")
    
    # 找到表格开始位置并插入新行
    lines = content.split('\n')
    table_start_index = None
    
    for i, line in enumerate(lines):
        if "| 文件名 | 上传时间 | 文件路径 |" in line:
            # 表格头的下一行是分隔线，新行应该插在分隔线后面
            table_start_index = i + 2
            break
    
    if table_start_index is not None:
        lines.insert(table_start_index, new_row)
        print(f"插入新行到位置: {table_start_index}")
    else:
        # 如果没找到表格头，直接添加到末尾
        lines.append(new_row)
        print("未找到表格头，添加新行到文件末尾")
    
    # 写回文件
    updated_content = '\n'.join(lines)
    with open(MD_FILE_PATH, 'w', encoding='utf-8') as f:
        f.write(updated_content)
        f.flush()  # 强制刷新缓冲区
        os.fsync(f.fileno())  # 确保写入磁盘
    
    # 验证写入结果
    if os.path.exists(MD_FILE_PATH):
        new_size = os.path.getsize(MD_FILE_PATH)
        print(f"MD文件已更新: {MD_FILE_PATH} (新大小: {new_size} bytes)")
        # 验证内容是否已写入
        with open(MD_FILE_PATH, 'r', encoding='utf-8') as f:
            if new_row in f.read():
                print("新记录已成功写入MD文件")
            else:
                print("警告: 新记录未在MD文件中找到")
    else:
        print(f"错误: MD文件未创建成功")

def main():
    parser = argparse.ArgumentParser(description='处理文件上传记录并更新Markdown文档')
    parser.add_argument('filename', help='上传的文件名')
    parser.add_argument('file_path', help='文件在仓库中的路径')
    parser.add_argument('timestamp', help='上传时间戳')
    
    args = parser.parse_args()
    
    print(f"开始处理: {args.filename}")
    print(f"文件路径: {args.file_path}")
    print(f"时间戳: {args.timestamp}")
    
    # 保存记录
    new_record = save_record(args.filename, args.file_path, args.timestamp)
    
    # 更新Markdown
    update_markdown_file(new_record)
    
    print(f"成功更新上传记录: {args.filename}")

if __name__ == "__main__":
    main()
