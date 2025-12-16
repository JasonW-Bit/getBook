#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理空文件夹工具
"""

import os
import sys
import argparse
from pathlib import Path


def remove_empty_dirs(path: str, dry_run: bool = True) -> int:
    """
    递归删除空文件夹
    
    Args:
        path: 要清理的目录
        dry_run: 是否只是预览（不实际删除）
    
    Returns:
        删除的文件夹数量
    """
    removed_count = 0
    
    # 从最深层的目录开始遍历
    for root, dirs, files in os.walk(path, topdown=False):
        # 检查当前目录是否为空
        if not os.listdir(root):
            if not dry_run:
                try:
                    os.rmdir(root)
                    print(f"✅ 删除空文件夹: {root}")
                    removed_count += 1
                except OSError as e:
                    print(f"⚠️  无法删除 {root}: {e}")
            else:
                print(f"📋 发现空文件夹: {root}")
                removed_count += 1
    
    return removed_count


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='清理空文件夹工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 预览要删除的空文件夹
  python3 cleanup_empty_folders.py data/training/novels
  
  # 实际删除空文件夹
  python3 cleanup_empty_folders.py data/training/novels --execute
        """
    )
    
    parser.add_argument('path', type=str, help='要清理的目录路径')
    parser.add_argument('--execute', action='store_true',
                       help='实际执行删除（默认只是预览）')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.path):
        print(f"❌ 路径不存在: {args.path}")
        return
    
    if not os.path.isdir(args.path):
        print(f"❌ 不是目录: {args.path}")
        return
    
    mode = "预览模式" if not args.execute else "执行模式"
    print(f"\n🔍 {mode}: 正在检查 {args.path}")
    print("=" * 60)
    
    removed_count = remove_empty_dirs(args.path, dry_run=not args.execute)
    
    print("=" * 60)
    if not args.execute:
        print(f"\n📋 发现 {removed_count} 个空文件夹")
        print("   使用 --execute 参数实际删除")
    else:
        print(f"\n✅ 已删除 {removed_count} 个空文件夹")


if __name__ == '__main__':
    main()

