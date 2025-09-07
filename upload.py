import os
import json
import argparse
import time
from datetime import datetime
from pathlib import Path

# 配置目标文件和目录（与原逻辑一致）
MD_FILE_PATH = os.path.join("src", "upload.md")  # Markdown文件路径
UPLOAD_RECORDS = os.path.join("src", "upload_records.json")  # 上传记录JSON文件


def ensure_directory_exists(file_path):
    """确保文件所在目录存在（带调试日志）"""
    directory = os.path.dirname(file_path)
    Path(directory).mkdir(parents=True, exist_ok=True)
    print(f"[DEBUG] 确保目录存在: {directory} - {'已存在' if os.path.exists(directory) else '已创建'}")


def update_md_lastmod():
    """更新Markdown文件中的lastmod字段为当前时间（批量处理时统一更新一次）"""
    if not os.path.exists(MD_FILE_PATH):
        print(f"[DEBUG] MD文件不存在，无需更新lastmod: {MD_FILE_PATH}")
        return

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(MD_FILE_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    updated = False
    # 查找并更新lastmod（适配Hugo的frontmatter格式）
    for i, line in enumerate(lines):
        if line.startswith('lastmod:'):
            lines[i] = f'lastmod: {current_time}\n'
            updated = True
            break
    # 若未找到lastmod，在date后添加
    if not updated:
        for i, line in enumerate(lines):
            if line.startswith('date:'):
                lines.insert(i + 1, f'lastmod: {current_time}\n')
                updated = True
                break
    # 若仍未找到，在frontmatter末尾添加
    if not updated:
        for i, line in enumerate(lines):
            if line.strip() == '---' and i > 0:
                lines.insert(i, f'lastmod: {current_time}\n')
                updated = True
                break

    if updated:
        with open(MD_FILE_PATH, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"[DEBUG] 已更新MD文件lastmod为: {current_time}")
    else:
        print(f"[DEBUG] 未找到MD文件的lastmod/date字段，跳过更新")


def load_records():
    """加载已有的上传记录（带调试日志）"""
    if os.path.exists(UPLOAD_RECORDS):
        file_size = os.path.getsize(UPLOAD_RECORDS)
        print(f"[DEBUG] 加载记录文件: {UPLOAD_RECORDS} (大小: {file_size} bytes)")
        with open(UPLOAD_RECORDS, 'r', encoding='utf-8') as f:
            return json.load(f)
    print(f"[DEBUG] 记录文件不存在，初始化空列表: {UPLOAD_RECORDS}")
    return []


def save_batch_records(batch_files, batch_timestamp):
    """批量保存上传记录到JSON文件（单次写入，避免多次IO）"""
    records = load_records()
    new_records = []

    # 处理时间戳格式（兼容前端传递的Z后缀）
    if batch_timestamp.endswith('Z'):
        batch_timestamp = batch_timestamp.replace('Z', '+00:00')
    batch_formatted_date = datetime.fromisoformat(batch_timestamp).strftime("%Y-%m-%d %H:%M:%S")

    # 批量生成新记录（所有文件用统一的批量时间戳，或可改为每个文件的上传时间）
    for file in batch_files:
        file_name = file['name']
        file_path = file['path']
        new_record = {
            "filename": file_name,
            "path": file_path,
            "batch_timestamp": batch_timestamp,  # 批量操作时间戳
            "formatted_date": batch_formatted_date,  # 格式化时间
            "upload_time": datetime.now().isoformat()  # 实际写入时间
        }
        new_records.append(new_record)
        records.insert(0, new_record)  # 插入到列表开头（按时间倒序）
        print(f"[DEBUG] 生成新记录: {file_name} - {batch_formatted_date}")

    # 单次写入所有记录（避免多次打开文件）
    with open(UPLOAD_RECORDS, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    # 验证保存结果
    if os.path.exists(UPLOAD_RECORDS):
        new_size = os.path.getsize(UPLOAD_RECORDS)
        print(f"[DEBUG] 批量记录已保存: {UPLOAD_RECORDS} (新大小: {new_size} bytes)")
    else:
        print(f"[WARNING] 记录文件保存失败: {UPLOAD_RECORDS}")

    # 批量处理后统一更新MD的lastmod
    update_md_lastmod()
    return new_records


def update_markdown_file(batch_new_records):
    """批量更新MD文件（单次读写，批量插入所有文件行）"""
    ensure_directory_exists(MD_FILE_PATH)
    new_rows = []  # 收集所有新记录的MD行

    # 1. 读取现有MD内容
    if os.path.exists(MD_FILE_PATH):
        file_size = os.path.getsize(MD_FILE_PATH)
        print(f"[DEBUG] 读取现有MD文件: {MD_FILE_PATH} (大小: {file_size} bytes)")
        with open(MD_FILE_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        # 若MD不存在，初始化带表格头的内容（适配原逻辑的表格结构）
        print(f"[DEBUG] MD文件不存在，初始化新文件: {MD_FILE_PATH}")
        content = "---\ndate: 2024-01-01 00:00:00\nlastmod: 2024-01-01 00:00:00\n---\n\n"
        content += "# 上传文件记录\n\n"
        content += "以下是所有上传文件的记录，按上传时间倒序排列：\n\n"
        content += "| 文件名 | 上传时间 | 文件链接 | 上传人 |\n"
        content += "|--------|----------|----------|--------|\n"

    # 2. 批量生成所有新记录的MD行
    for record in batch_new_records:
        file_link = format_file_link(record['path'])  # 生成文件链接
        new_row = f"| {record['filename']} | {record['formatted_date']} | {file_link} | |\n"
        new_rows.append(new_row)
        print(f"[DEBUG] 生成MD行: {new_row.strip()}")

    # 3. 插入所有新行到表格（单次插入，避免多次修改）
    lines = content.split('\n')
    table_start_index = None
    # 找到表格头位置（"| 文件名 | 上传时间 | 文件链接 |"）
    for i, line in enumerate(lines):
        if "| 文件名 | 上传时间 | 文件链接 |" in line and "上传人" in line:
            table_start_index = i + 2  # 跳过表格头和分隔线（i+1是分隔线，i+2是数据行开始）
            break

    if table_start_index is not None:
        # 批量插入所有新行（保持顺序）
        lines[table_start_index:table_start_index] = new_rows
        print(f"[DEBUG] 批量插入 {len(new_rows)} 行到MD表格，位置: {table_start_index}")
    else:
        # 若未找到表格头，追加到文件末尾
        lines.extend(new_rows)
        print(f"[DEBUG] 未找到MD表格头，追加 {len(new_rows)} 行到文件末尾")

    # 4. 单次写入所有修改（强制刷新到磁盘，避免缓存）
    updated_content = '\n'.join(lines)
    with open(MD_FILE_PATH, 'w', encoding='utf-8') as f:
        f.write(updated_content)
        f.flush()  # 强制刷新缓冲区
        os.fsync(f.fileno())  # 确保写入磁盘（解决「日志显示成功但实际未写入」问题）

    # 5. 验证写入结果
    if os.path.exists(MD_FILE_PATH):
        new_size = os.path.getsize(MD_FILE_PATH)
        print(f"[DEBUG] MD文件已更新: {MD_FILE_PATH} (新大小: {new_size} bytes)")
        # 验证至少一条新行已写入
        with open(MD_FILE_PATH, 'r', encoding='utf-8') as f:
            if any(row in f.read() for row in new_rows):
                print(f"[DEBUG] 批量记录已成功写入MD文件")
            else:
                print(f"[WARNING] 未在MD文件中找到新记录（可能写入失败）")
    else:
        print(f"[ERROR] MD文件更新失败：文件不存在")


def format_file_link(file_path):
    """生成MD文件链接（适配原逻辑，处理空格转义）"""
    # 原逻辑：去掉 "src/upload/" 前缀，生成相对链接
    relative_path = file_path.replace("src/upload/", "", 1)
    file_name = os.path.basename(file_path)
    file_name_without_ext = os.path.splitext(file_name)[0]
    # 空格转义为 %20（确保链接可访问）
    encoded_path = relative_path.replace(" ", "%20")
    return f"[{file_name_without_ext}]({encoded_path})"


def main():
    # 关键：修改参数为「批量文件JSON」和「批量时间戳」，而非单个文件参数
    parser = argparse.ArgumentParser(description='批量处理文件上传记录并更新Markdown文档')
    parser.add_argument('batch_files_json', help='JSON格式的批量文件列表（如：[{"name":"a.docx","path":"src/..."}]）')
    parser.add_argument('batch_timestamp', help='批量上传的时间戳（ISO格式）')
    
    args = parser.parse_args()
    print(f"[DEBUG] 开始批量处理 - 文件数: {len(json.loads(args.batch_files_json))}, 时间戳: {args.batch_timestamp}")

    # 1. 解析JSON格式的批量文件列表（前端传递的batch_files）
    try:
        batch_files = json.loads(args.batch_files_json)
        if not isinstance(batch_files, list) or len(batch_files) == 0:
            raise ValueError("批量文件列表必须是非空数组")
    except json.JSONDecodeError as e:
        print(f"[ERROR] 解析批量文件JSON失败: {str(e)}")
        raise
    except ValueError as e:
        print(f"[ERROR] 批量文件列表格式错误: {str(e)}")
        raise

    # 2. 批量保存记录到JSON
    batch_new_records = save_batch_records(batch_files, args.batch_timestamp)

    # 3. 批量更新MD文件
    update_markdown_file(batch_new_records)

    print(f"[SUCCESS] 批量处理完成 - 共更新 {len(batch_new_records)} 个文件记录")


if __name__ == "__main__":
    main()