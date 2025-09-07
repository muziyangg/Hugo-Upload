import os
import json
import argparse
import requests
from datetime import datetime
from pathlib import Path

# 配置目标目录 - 文件将被上传到这里
TARGET_DIR = os.path.join("src", "upload", "assets")

def ensure_directory_exists(directory):
    """确保目标目录存在，如果不存在则创建"""
    Path(directory).mkdir(parents=True, exist_ok=True)

def download_file(url, destination):
    """从URL下载文件并保存到目标路径"""
    try:
        # 处理GitHub Gist URL
        if "gist.github.com" in url:
            api_url = url.replace("gist.github.com", "api.github.com/gists")
            response = requests.get(api_url)
            response.raise_for_status()
            
            gist_data = response.json()
            filename = next(iter(gist_data["files"].keys()))
            file_content = gist_data["files"][filename]["content"]
            
            with open(destination, "wb") as f:
                f.write(file_content.encode("utf-8"))
        else:
            # 常规文件下载
            response = requests.get(url)
            response.raise_for_status()
            
            with open(destination, "wb") as f:
                f.write(response.content)
                
        return True
    except Exception as e:
        print(f"下载文件失败: {str(e)}")
        return False

def load_uploads(records_file):
    """加载已有的上传记录"""
    if os.path.exists(records_file):
        with open(records_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_uploads(records_file, uploads):
    """保存上传记录到JSON文件"""
    with open(records_file, 'w', encoding='utf-8') as f:
        json.dump(uploads, f, ensure_ascii=False, indent=2)

def update_md_file(md_file, new_entry, uploads):
    """更新Markdown文件，将最新上传放在最上方"""
    # 确保目录存在
    md_dir = os.path.dirname(md_file)
    if md_dir and not os.path.exists(md_dir):
        os.makedirs(md_dir)
    
    # 读取现有内容
    if os.path.exists(md_file):
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = "# 文件上传记录\n\n| 文件名 | 上传时间 | 文件路径 |\n|--------|----------|----------|\n"

    # 检查是否已有表格
    if "| 文件名 | 上传时间 | 文件路径 |" not in content:
        content += "\n| 文件名 | 上传时间 | 文件路径 |\n|--------|----------|----------|\n"

    # 分割内容为表头和表格部分
    lines = content.split('\n')
    table_start = None
    for i, line in enumerate(lines):
        if "| 文件名 | 上传时间 | 文件路径 |" in line:
            table_start = i + 2  # 表格标题行的下一行是分隔线，再下一行开始是数据
            break

    # 构建新条目
    new_line = f"| {new_entry['filename']} | {new_entry['timestamp']} | {new_entry['path']} |"

    # 插入新条目到表格开头
    if table_start is not None:
        lines.insert(table_start, new_line)
    else:
        # 如果没有找到表格，添加新表格
        lines.append("| 文件名 | 上传时间 | 文件路径 |")
        lines.append("|--------|----------|----------|")
        lines.append(new_line)

    # 写回文件
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

def main():
    parser = argparse.ArgumentParser(description='处理文件上传并更新记录')
    parser.add_argument('filename', help='上传的文件名')
    parser.add_argument('file_url', help='文件的URL地址')
    parser.add_argument('--records', default='uploads.json', help='记录上传信息的JSON文件')
    parser.add_argument('--mdfile', default=os.path.join('src', 'upload.md'), help='要更新的Markdown文件')
    
    args = parser.parse_args()

    # 确保目标目录存在
    ensure_directory_exists(TARGET_DIR)
    
    # 构建目标文件路径
    target_path = os.path.join(TARGET_DIR, args.filename)
    
    # 下载文件
    if not download_file(args.file_url, target_path):
        print(f"无法下载文件: {args.filename}")
        return
    
    # 创建新的上传记录
    new_upload = {
        'filename': args.filename,
        'path': target_path,
        'timestamp': datetime.now().isoformat()
    }

    # 加载并更新上传记录
    uploads = load_uploads(args.records)
    uploads.insert(0, new_upload)  # 添加到开头
    save_uploads(args.records, uploads)

    # 更新Markdown文件
    update_md_file(args.mdfile, new_upload, uploads)

    print(f"成功处理上传: {args.filename}")

if __name__ == "__main__":
    main()
