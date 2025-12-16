#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查当前运行任务状态
"""

import os
import sys
import time
import subprocess
from pathlib import Path


def check_running_processes():
    """检查运行中的进程"""
    print("=" * 60)
    print("🔄 运行中的进程")
    print("=" * 60)
    
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        relevant_processes = []
        for line in lines:
            if 'python' in line.lower():
                keywords = ['workflow', 'execute', 'pipeline', 'train', 'auto']
                if any(kw in line.lower() for kw in keywords):
                    parts = line.split()
                    if len(parts) > 10:
                        relevant_processes.append({
                            'pid': parts[1],
                            'cpu': parts[2],
                            'mem': parts[3],
                            'time': parts[9],
                            'cmd': ' '.join(parts[10:])[:100]
                        })
        
        if relevant_processes:
            for proc in relevant_processes:
                print(f"\nPID: {proc['pid']}")
                print(f"  CPU: {proc['cpu']}% | MEM: {proc['mem']}% | 时间: {proc['time']}")
                print(f"  命令: {proc['cmd']}")
        else:
            print("\nℹ️  没有找到相关运行进程")
            
    except Exception as e:
        print(f"❌ 检查进程失败: {e}")


def check_log_files():
    """检查日志文件"""
    print("\n" + "=" * 60)
    print("📄 日志文件状态")
    print("=" * 60)
    
    log_files = [
        '/tmp/full_workflow_final.log',
        '/tmp/auto_execute_full.log',
        '/tmp/workflow_execution.log'
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            size = os.path.getsize(log_file) / 1024
            mtime = os.path.getmtime(log_file)
            age = time.time() - mtime
            
            print(f"\n📄 {os.path.basename(log_file)}:")
            print(f"   大小: {size:.1f} KB")
            print(f"   最后更新: {int(age)} 秒前 ({'活跃' if age < 60 else '可能已完成'})")
            
            # 读取关键信息
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    if lines:
                        # 查找Epoch信息
                        epoch_lines = [l for l in lines if 'Epoch' in l]
                        if epoch_lines:
                            print(f"   训练进度: {epoch_lines[-1].strip()[:80]}")
                        
                        # 查找完成信息
                        complete_lines = [l for l in lines if any(x in l for x in ['完成', '成功', '失败', '模型已'])]
                        if complete_lines:
                            print(f"   最新状态: {complete_lines[-1].strip()[:80]}")
                        else:
                            print(f"   最新输出: {lines[-1].strip()[:80]}")
            except Exception as e:
                print(f"   ⚠️  读取失败: {e}")
        else:
            print(f"\n📄 {os.path.basename(log_file)}: 不存在")


def check_model_files():
    """检查模型文件"""
    print("\n" + "=" * 60)
    print("📁 模型文件状态")
    print("=" * 60)
    
    model_path = 'models/text_rewriter_model'
    
    if os.path.exists(model_path):
        files = os.listdir(model_path)
        model_files = [f for f in files if f.endswith('.h5') or f.endswith('.json')]
        
        if model_files:
            print(f"\n✅ 找到 {len(model_files)} 个模型文件:")
            total_size = 0
            for f in model_files:
                fpath = os.path.join(model_path, f)
                size = os.path.getsize(fpath) / 1024 / 1024
                mtime = os.path.getmtime(fpath)
                age = time.time() - mtime
                total_size += size
                status = "✅ 最新" if age < 3600 else "⚠️  较旧"
                print(f"   {status} {f}: {size:.2f} MB (更新于 {int(age/60)} 分钟前)")
            
            print(f"\n   总大小: {total_size:.2f} MB")
        else:
            print("\n⚠️  模型目录存在但没有模型文件")
            print("   训练可能正在进行中或未开始")
    else:
        print("\n❌ 模型目录不存在")
        print("   训练可能未开始")


def check_training_data():
    """检查训练数据"""
    print("\n" + "=" * 60)
    print("📊 训练数据状态")
    print("=" * 60)
    
    training_file = 'data/training/processed/training_data.txt'
    
    if os.path.exists(training_file):
        size = os.path.getsize(training_file) / 1024 / 1024
        mtime = os.path.getmtime(training_file)
        age = time.time() - mtime
        
        # 统计行数
        try:
            with open(training_file, 'r', encoding='utf-8') as f:
                lines = [l for l in f if l.strip() and '\t' in l]
            
            print(f"\n✅ 训练数据文件存在:")
            print(f"   文件: {training_file}")
            print(f"   大小: {size:.2f} MB")
            print(f"   样本数: {len(lines)} 条")
            print(f"   更新时间: {int(age/60)} 分钟前")
        except Exception as e:
            print(f"\n⚠️  读取训练数据失败: {e}")
    else:
        print("\n❌ 训练数据文件不存在")


def check_temp_files():
    """检查临时文件"""
    print("\n" + "=" * 60)
    print("🧹 临时文件检查")
    print("=" * 60)
    
    temp_items = []
    
    # 查找.temp目录
    for root, dirs, files in os.walk('data/training'):
        if '.temp' in root:
            size = sum(os.path.getsize(os.path.join(dirpath, filename))
                      for dirpath, dirnames, filenames in os.walk(root)
                      for filename in filenames)
            temp_items.append(('目录', root, size))
    
    # 查找进度文件
    for root, dirs, files in os.walk('data/training'):
        for file in files:
            if file.endswith('_progress.json') or file.endswith('.tmp'):
                fpath = os.path.join(root, file)
                size = os.path.getsize(fpath)
                temp_items.append(('文件', fpath, size))
    
    if temp_items:
        print(f"\n⚠️  找到 {len(temp_items)} 个临时文件/目录:")
        total_size = 0
        for item_type, path, size in temp_items[:10]:  # 只显示前10个
            total_size += size
            print(f"   {item_type}: {os.path.basename(path)} ({size/1024/1024:.2f} MB)")
        
        if len(temp_items) > 10:
            print(f"   ... 还有 {len(temp_items) - 10} 个")
        
        print(f"\n   总大小: {total_size/1024/1024:.2f} MB")
        print("   💡 建议: 运行清理脚本删除临时文件")
    else:
        print("\n✅ 没有临时文件")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("📋 当前任务状态检查")
    print("=" * 60)
    print()
    
    check_running_processes()
    check_log_files()
    check_model_files()
    check_training_data()
    check_temp_files()
    
    print("\n" + "=" * 60)
    print("✅ 检查完成")
    print("=" * 60)


if __name__ == '__main__':
    main()

