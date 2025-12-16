#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理临时文件和目录
用于清理爬取过程中产生的临时文件，释放磁盘空间
"""

import os
import shutil
import argparse
from pathlib import Path


def cleanup_temp_dirs(base_dir: str = "data/training", dry_run: bool = False) -> dict:
    """
    清理所有临时目录和文件
    
    Args:
        base_dir: 基础目录
        dry_run: 是否只是预览，不实际删除
    
    Returns:
        清理统计
    """
    stats = {
        'temp_dirs_removed': 0,
        'temp_files_removed': 0,
        'space_freed_mb': 0,
        'errors': []
    }
    
    base_path = Path(base_dir)
    if not base_path.exists():
        print(f"❌ 目录不存在: {base_dir}")
        return stats
    
    print(f"🔍 正在扫描临时文件和目录: {base_dir}")
    if dry_run:
        print("   ⚠️  预览模式：不会实际删除文件")
    
    # 查找所有.temp目录
    temp_dirs = []
    for root, dirs, files in os.walk(base_dir):
        # 查找.temp目录
        if '.temp' in root:
            temp_dirs.append(root)
        
        # 查找临时文件
        for file in files:
            if file.startswith('.') or file.endswith('.tmp') or file.endswith('.temp'):
                file_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(file_path) / 1024 / 1024
                    stats['space_freed_mb'] += size
                    stats['temp_files_removed'] += 1
                    
                    if not dry_run:
                        os.remove(file_path)
                        print(f"   🗑️  删除临时文件: {file_path} ({size:.2f} MB)")
                except Exception as e:
                    stats['errors'].append(f"删除文件失败 {file_path}: {e}")
    
    # 删除临时目录（从最深层的开始，避免删除父目录后子目录不存在）
    temp_dirs_sorted = sorted(temp_dirs, key=lambda x: x.count(os.sep), reverse=True)
    
    for temp_dir in temp_dirs_sorted:
        # 检查目录是否还存在（可能已经被父目录删除）
        if not os.path.exists(temp_dir):
            continue
            
        try:
            # 计算目录大小
            total_size = 0
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        total_size += os.path.getsize(file_path)
                    except:
                        pass
            
            size_mb = total_size / 1024 / 1024
            stats['space_freed_mb'] += size_mb
            
            if not dry_run:
                shutil.rmtree(temp_dir)
                print(f"   🗑️  删除临时目录: {os.path.basename(temp_dir)} ({size_mb:.2f} MB)")
            else:
                print(f"   📁 将删除临时目录: {os.path.basename(temp_dir)} ({size_mb:.2f} MB)")
            
            stats['temp_dirs_removed'] += 1
        except Exception as e:
            # 如果目录不存在，忽略错误
            if os.path.exists(temp_dir):
                stats['errors'].append(f"删除目录失败 {temp_dir}: {e}")
    
    return stats


def cleanup_progress_files(base_dir: str = "data/training", dry_run: bool = False) -> dict:
    """
    清理进度文件
    
    Args:
        base_dir: 基础目录
        dry_run: 是否只是预览
    
    Returns:
        清理统计
    """
    stats = {
        'progress_files_removed': 0,
        'space_freed_mb': 0,
        'errors': []
    }
    
    base_path = Path(base_dir)
    if not base_path.exists():
        return stats
    
    # 查找所有进度文件
    progress_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.progress') or file.endswith('.progress.json'):
                progress_files.append(os.path.join(root, file))
    
    for file_path in progress_files:
        try:
            size = os.path.getsize(file_path) / 1024 / 1024
            stats['space_freed_mb'] += size
            
            if not dry_run:
                os.remove(file_path)
                print(f"   🗑️  删除进度文件: {file_path}")
            else:
                print(f"   📄 将删除进度文件: {file_path}")
            
            stats['progress_files_removed'] += 1
        except Exception as e:
            stats['errors'].append(f"删除进度文件失败 {file_path}: {e}")
    
    return stats


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='清理临时文件和目录',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 预览要删除的文件（不实际删除）
  python3 scripts/utils/cleanup_temp_files.py --dry-run
  
  # 实际清理临时文件
  python3 scripts/utils/cleanup_temp_files.py
  
  # 清理指定目录
  python3 scripts/utils/cleanup_temp_files.py --dir data/training/novels
        """
    )
    
    parser.add_argument('--dir', '-d', default='data/training',
                       help='要清理的基础目录（默认：data/training）')
    parser.add_argument('--dry-run', action='store_true',
                       help='预览模式，不实际删除文件')
    parser.add_argument('--progress-only', action='store_true',
                       help='只清理进度文件')
    parser.add_argument('--temp-only', action='store_true',
                       help='只清理临时目录和文件')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🧹 临时文件清理工具")
    print("=" * 60)
    
    total_stats = {
        'temp_dirs_removed': 0,
        'temp_files_removed': 0,
        'progress_files_removed': 0,
        'space_freed_mb': 0,
        'errors': []
    }
    
    # 清理临时文件
    if not args.progress_only:
        print("\n📁 清理临时目录和文件...")
        temp_stats = cleanup_temp_dirs(args.dir, args.dry_run)
        for key in total_stats:
            if key in temp_stats:
                if isinstance(total_stats[key], list):
                    total_stats[key].extend(temp_stats[key])
                else:
                    total_stats[key] += temp_stats[key]
    
    # 清理进度文件
    if not args.temp_only:
        print("\n📄 清理进度文件...")
        progress_stats = cleanup_progress_files(args.dir, args.dry_run)
        for key in total_stats:
            if key in progress_stats:
                if isinstance(total_stats[key], list):
                    total_stats[key].extend(progress_stats[key])
                else:
                    total_stats[key] += progress_stats[key]
    
    # 输出统计
    print("\n" + "=" * 60)
    print("📊 清理统计:")
    print(f"   临时目录: {total_stats['temp_dirs_removed']} 个")
    print(f"   临时文件: {total_stats['temp_files_removed']} 个")
    print(f"   进度文件: {total_stats['progress_files_removed']} 个")
    print(f"   释放空间: {total_stats['space_freed_mb']:.2f} MB")
    
    if total_stats['errors']:
        print(f"\n⚠️  错误: {len(total_stats['errors'])} 个")
        for error in total_stats['errors'][:5]:
            print(f"   - {error}")
    
    if args.dry_run:
        print("\n💡 这是预览模式，实际运行请移除 --dry-run 参数")
    else:
        print("\n✅ 清理完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()

