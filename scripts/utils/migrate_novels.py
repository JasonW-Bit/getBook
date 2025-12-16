#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小说文件迁移脚本
将已生成的小说文件移动到新的文件夹结构中
"""

import os
import re
import shutil
from pathlib import Path


def extract_title_from_filename(filename):
    """从文件名中提取小说标题"""
    # 移除扩展名
    title = os.path.splitext(filename)[0]
    return title


def extract_title_from_file(filepath):
    """从文件内容中提取小说标题（读取第一行）"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            # 尝试匹配 "标题: xxx" 格式
            match = re.search(r'标题[：:]\s*(.+)', first_line)
            if match:
                return match.group(1).strip()
    except Exception as e:
        print(f"  警告: 无法读取文件内容: {e}")
    return None


def migrate_novel_files(base_dir='.', output_base='novels'):
    """
    迁移小说文件到新的文件夹结构
    
    Args:
        base_dir: 当前目录（默认当前目录）
        output_base: 输出基础文件夹（默认'novels'）
    """
    print("=" * 60)
    print("📚 小说文件迁移工具")
    print("=" * 60)
    print()
    
    # 创建输出基础文件夹
    if not os.path.exists(output_base):
        os.makedirs(output_base)
        print(f"📁 创建输出文件夹: {output_base}/")
    
    # 查找所有TXT和JSON文件
    txt_files = list(Path(base_dir).glob("*.txt"))
    json_files = list(Path(base_dir).glob("*.json"))
    
    # 过滤掉非小说文件（如requirements.txt等）
    exclude_files = {'requirements.txt', 'README.txt', 'CHANGELOG.txt', 'ERROR_HANDLING.txt'}
    txt_files = [f for f in txt_files if f.name not in exclude_files]
    
    # 也查找进度文件（.xxx_progress.json格式）
    progress_files = list(Path(base_dir).glob(".*_progress.json"))
    
    all_files = txt_files + json_files + progress_files
    
    if not all_files:
        print("✅ 没有找到需要迁移的小说文件")
        return
    
    print(f"找到 {len(all_files)} 个文件需要处理:")
    for f in all_files:
        print(f"  - {f.name}")
    print()
    
    migrated_count = 0
    skipped_count = 0
    
    for filepath in all_files:
        filename = filepath.name
        print(f"\n处理文件: {filename}")
        
        # 处理进度文件（.xxx_progress.json格式）
        if filename.startswith('.') and filename.endswith('_progress.json'):
            # 从进度文件名中提取标题（移除.前缀和_progress.json后缀）
            title = filename[1:-len('_progress.json')]
            print(f"  进度文件，从文件名提取标题: {title}")
        else:
            # 尝试从文件名提取标题
            title = extract_title_from_filename(filename)
            
            # 如果是TXT文件，尝试从内容中提取更准确的标题
            if filepath.suffix == '.txt':
                content_title = extract_title_from_file(filepath)
                if content_title:
                    title = content_title
                    print(f"  从文件内容提取标题: {title}")
        
        # 清理标题，用于文件夹名称
        title_safe = re.sub(r'[<>:"/\\|?*]', '', title)
        
        # 创建小说文件夹
        novel_dir = os.path.join(output_base, title_safe)
        if not os.path.exists(novel_dir):
            os.makedirs(novel_dir)
            print(f"  📁 创建文件夹: {novel_dir}/")
        
        # 目标文件路径
        dest_path = os.path.join(novel_dir, filename)
        
        # 检查目标文件是否已存在
        if os.path.exists(dest_path):
            print(f"  ⚠️  目标文件已存在，跳过: {dest_path}")
            skipped_count += 1
            continue
        
        # 移动文件
        try:
            shutil.move(str(filepath), dest_path)
            print(f"  ✅ 已移动到: {dest_path}")
            migrated_count += 1
        except Exception as e:
            print(f"  ❌ 移动失败: {e}")
    
    print()
    print("=" * 60)
    print("📊 迁移完成统计")
    print("=" * 60)
    print(f"  成功迁移: {migrated_count} 个文件")
    if skipped_count > 0:
        print(f"  跳过: {skipped_count} 个文件（已存在）")
    print()
    print(f"所有文件已移动到: {output_base}/")
    print()


if __name__ == '__main__':
    import sys
    
    # 可以指定输出文件夹
    output_dir = sys.argv[1] if len(sys.argv) > 1 else 'novels'
    
    migrate_novel_files(output_base=output_dir)

