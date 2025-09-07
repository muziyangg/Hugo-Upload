import os
import json
import argparse
from datetime import datetime
from pathlib import Path

# 配置目标文件和目录
MD_FILE_PATH = os.path.join("src", "upload.md")  # Markdown文件路径
UPLOAD_RECORDS = "upload_records.json"  # 上传记录JSON文件

def ensure_directory_exists(file_path):
    """确保文件所在目录存在"""
    directory = os.path.dirname(file_path)
    Path(directory).mkdir(parents=True, exist_ok=True)

def load_records():
    """加载已有的上传记录"""
    if os.path.exists(UPLOAD_RECORDS):
        with open(UPLOAD_RECORDS, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_record(filename, file_path, timestamp):
    """保存新的上传记录"""
    records = load_records()
    
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
        
    return new_record

def update_markdown_file(new_record):
    """更新Markdown文件，添加新的上传记录"""
    ensure_directory_exists(MD_FILE_PATH)
    
    # 读取现有内容
    if os.path.exists(MD_FILE_PATH):
        with open(MD_FILE_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        # 如果文件不存在，创建并添加标题和表格头
        content = "# 上传文件记录\n\n"
        content += "以下是所有上传文件的记录，按上传时间倒序排列：\n\n"
        content += "| 文件名 | 上传时间 | 文件路径 |\n"
        content += "|--------|----------|----------|\n"
    
    # 检查表格头是否存在，如果不存在则添加
    if "| 文件名 | 上传时间 | 文件路径 |" not in content:
        content += "\n| 文件名 | 上传时间 | 文件路径 |\n"
        content += "|--------|----------|----------|\n"
    
    # 构建新记录行
    new_row = f"| {new_record['filename']} | {new_record['formatted_date']} | {new_record['path']} |\n"
    
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
    else:
        # 如果没找到表格头，直接添加到末尾
        lines.append(new_row)
    
    # 写回文件
    with open(MD_FILE_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

def commit_changes(filename):
    """提交更改到仓库（由GitHub Actions处理实际提交）"""
    # 此函数在GitHub Actions环境中会被工作流自动处理
    print(f"已更新Markdown文件，添加了新文件: {filename}")

def main():
    parser = argparse.ArgumentParser(description='处理文件上传记录并更新Markdown文档')
    parser.add_argument('filename', help='上传的文件名')
    parser.add_argument('file_path', help='文件在仓库中的路径')
    parser.add_argument('timestamp', help='上传时间戳')
    
    args = parser.parse_args()
    
    # 保存记录
    new_record = save_record(args.filename, args.file_path, args.timestamp)
    
    # 更新Markdown
    update_markdown_file(new_record)
    
    # 提交更改（由GitHub Actions完成实际提交）
    commit_changes(args.filename)
    
    print(f"成功更新上传记录: {args.filename}")

if __name__ == "__main__":
    main()
    