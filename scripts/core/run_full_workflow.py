#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整工作流程执行脚本
修复所有导入问题，确保流程完整执行
"""

import os
import sys

# 添加路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, script_dir)
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'scripts'))

# 导入模块
from core.pipeline import DataPipeline

def main():
    """主函数"""
    print("\n" + "="*60)
    print("🚀 完整工作流程自动执行")
    print("="*60)
    
    # 初始化流水线
    pipeline = DataPipeline("data/training")
    
    # 检查现有数据
    novels_dir = pipeline.novels_dir
    novel_files = []
    if os.path.exists(novels_dir):
        for root, dirs, files in os.walk(novels_dir):
            for file in files:
                if file.endswith('.txt'):
                    novel_files.append(os.path.join(root, file))
    
    if not novel_files:
        print("\n❌ 未找到小说数据")
        return False
    
    print(f"\n✅ 找到 {len(novel_files)} 本小说")
    
    # 执行完整流程（跳过爬取，使用已有数据）
    success = pipeline.run_full_pipeline(
        site_name=None,  # 不爬取
        category=None,   # 不爬取
        count=0,
        use_ai=False,
        epochs=10,
        batch_size=8,
        incremental=False,
        organize_data=False,
        skip_steps=['scrape']  # 跳过爬取
    )
    
    if success:
        # 清理临时文件
        print("\n" + "="*60)
        print("🧹 清理临时文件")
        print("="*60)
        
        import shutil
        cleaned = 0
        
        # 清理.temp目录
        for root, dirs, files in os.walk(pipeline.output_dir):
            if '.temp' in root:
                try:
                    shutil.rmtree(root)
                    cleaned += 1
                    print(f"   🗑️  已清理: {os.path.basename(root)}")
                except:
                    pass
        
        # 清理进度文件
        for root, dirs, files in os.walk(pipeline.output_dir):
            for file in files:
                if file.endswith('_progress.json') or file.endswith('.tmp'):
                    try:
                        os.remove(os.path.join(root, file))
                        cleaned += 1
                    except:
                        pass
        
        if cleaned > 0:
            print(f"\n✅ 清理完成: {cleaned} 个文件/目录")
        else:
            print("ℹ️  没有需要清理的临时文件")
        
        # 最终验证
        print("\n" + "="*60)
        print("📋 最终验证")
        print("="*60)
        
        # 检查模型
        model_files = [
            os.path.join(pipeline.model_path, 'best_model.h5'),
            os.path.join(pipeline.model_path, 'final_model.h5'),
            os.path.join(pipeline.model_path, 'vocab.json')
        ]
        
        existing = [f for f in model_files if os.path.exists(f)]
        if existing:
            print(f"✅ 模型文件: {len(existing)}/{len(model_files)} 个文件已生成")
            for f in existing:
                size = os.path.getsize(f) / 1024 / 1024
                print(f"   - {os.path.basename(f)}: {size:.2f} MB")
        else:
            print("❌ 模型文件未生成")
            return False
        
        print("\n" + "="*60)
        print("🎉 完整工作流程执行成功！")
        print("="*60)
        return True
    else:
        print("\n❌ 工作流程执行失败")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

