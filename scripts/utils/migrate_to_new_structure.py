#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将旧的数据结构迁移到新的结构：网站/类型/小说名
"""

import os
import sys
import json
import shutil
import re
import argparse
from pathlib import Path
from typing import Dict, List


def migrate_novels_data(source_dir: str, target_dir: str, site_name: str = "m.shuhaige.net", dry_run: bool = True) -> Dict:
    """
    迁移小说数据到新结构
    
    Args:
        source_dir: 源目录（data/training/novels）
        target_dir: 目标目录（data/training/novels）
        site_name: 网站名称
        dry_run: 是否只是预览
    
    Returns:
        迁移统计
    """
    stats = {
        'migrated': 0,
        'skipped': 0,
        'errors': 0,
        'files': []
    }
    
    # 查找所有小说文件
    for root, dirs, files in os.walk(source_dir):
        # 跳过目标目录本身
        if root == target_dir:
            continue
        
        for file in files:
            if not file.endswith(('.txt', '.json')):
                continue
            
            source_file = os.path.join(root, file)
            
            # 跳过已经在正确位置的文件
            if site_name in source_file and '/都市/' in source_file or '/玄幻/' in source_file:
                # 检查是否已经在正确的结构中
                parts = source_file.split(os.sep)
                if len(parts) >= 4 and parts[-4] == site_name:
                    stats['skipped'] += 1
                    continue
            
            try:
                # 提取小说信息
                novel_name = None
                category = None
                
                # 方法1: 从文件路径推断
                if '/都市/' in source_file:
                    category = '都市'
                    # 提取小说名（文件名去掉扩展名）
                    novel_name = Path(file).stem
                elif '/玄幻/' in source_file:
                    category = '玄幻'
                    novel_name = Path(file).stem
                else:
                    # 方法2: 从JSON文件读取
                    if file.endswith('.json'):
                        try:
                            with open(source_file, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                novel_name = data.get('title', Path(file).stem)
                                category = data.get('category', '其他')
                        except:
                            novel_name = Path(file).stem
                            category = '其他'
                    else:
                        # 方法3: 从TXT文件第一行读取标题
                        try:
                            with open(source_file, 'r', encoding='utf-8') as f:
                                first_line = f.readline()
                                if first_line.startswith('标题:'):
                                    novel_name = first_line.replace('标题:', '').strip()
                                else:
                                    novel_name = Path(file).stem
                        except:
                            novel_name = Path(file).stem
                        category = '其他'
                
                if not novel_name:
                    novel_name = Path(file).stem
                if not category:
                    category = '其他'
                
                # 清理小说名（移除非法字符）
                safe_novel_name = re.sub(r'[<>:"/\\|?*]', '', novel_name)
                
                # 构建目标路径：网站/类型/小说名/文件名
                target_novel_dir = os.path.join(target_dir, site_name, category, safe_novel_name)
                target_file = os.path.join(target_novel_dir, file)
                
                # 检查目标文件是否已存在
                if os.path.exists(target_file):
                    stats['skipped'] += 1
                    continue
                
                if not dry_run:
                    # 创建目标目录
                    os.makedirs(target_novel_dir, exist_ok=True)
                    # 移动文件
                    shutil.move(source_file, target_file)
                    print(f"✅ 迁移: {source_file} -> {target_file}")
                else:
                    print(f"📋 将迁移: {source_file} -> {target_file}")
                
                stats['migrated'] += 1
                stats['files'].append({
                    'source': source_file,
                    'target': target_file,
                    'novel': novel_name,
                    'category': category
                })
                
            except Exception as e:
                print(f"❌ 迁移失败 {source_file}: {e}")
                stats['errors'] += 1
    
    return stats


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='迁移小说数据到新结构（网站/类型/小说名）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 预览迁移
  python3 migrate_to_new_structure.py data/training/novels
  
  # 实际迁移
  python3 migrate_to_new_structure.py data/training/novels --execute --site m.shuhaige.net
        """
    )
    
    parser.add_argument('source_dir', type=str, help='源目录（data/training/novels）')
    parser.add_argument('--target-dir', type=str, default=None,
                       help='目标目录（默认与源目录相同）')
    parser.add_argument('--site', type=str, default='m.shuhaige.net',
                       help='网站名称（默认：m.shuhaige.net）')
    parser.add_argument('--execute', action='store_true',
                       help='实际执行迁移（默认只是预览）')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.source_dir):
        print(f"❌ 源目录不存在: {args.source_dir}")
        return
    
    target_dir = args.target_dir or args.source_dir
    
    mode = "预览模式" if not args.execute else "执行模式"
    print(f"\n🔄 {mode}: 正在迁移数据")
    print(f"   源目录: {args.source_dir}")
    print(f"   目标目录: {target_dir}")
    print(f"   网站名称: {args.site}")
    print("=" * 60)
    
    stats = migrate_novels_data(args.source_dir, target_dir, args.site, dry_run=not args.execute)
    
    print("=" * 60)
    print(f"\n📊 迁移统计:")
    print(f"   迁移: {stats['migrated']} 个文件")
    print(f"   跳过: {stats['skipped']} 个文件")
    print(f"   错误: {stats['errors']} 个文件")
    
    if not args.execute:
        print(f"\n💡 使用 --execute 参数实际执行迁移")


if __name__ == '__main__':
    main()

