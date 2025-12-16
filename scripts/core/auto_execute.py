#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动执行完整流程
包括：数据检查、结构化处理、训练数据生成、模型训练、清理等
"""

import os
import sys
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional

# 导入核心模块
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from .pipeline import DataPipeline
    from .config_center import ConfigCenter
except ImportError:
    from pipeline import DataPipeline
    from config_center import ConfigCenter


class AutoExecutor:
    """自动执行器 - 执行完整的工作流程"""
    
    def __init__(self, output_dir: str = "data/training"):
        """
        初始化自动执行器
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = output_dir
        self.pipeline = DataPipeline(output_dir)
        self.config = ConfigCenter()
        
        # 执行统计
        self.stats = {
            'novels_found': 0,
            'structured': 0,
            'training_samples': 0,
            'model_trained': False,
            'errors': []
        }
    
    def check_existing_data(self) -> Dict:
        """
        检查现有数据
        
        Returns:
            数据状态字典
        """
        print("\n" + "="*60)
        print("📋 检查现有数据")
        print("="*60)
        
        status = {
            'novels_exist': False,
            'novels_count': 0,
            'structured_exist': False,
            'structured_count': 0,
            'training_data_exist': False,
            'model_exist': False
        }
        
        # 检查小说数据
        novels_dir = os.path.join(self.output_dir, 'novels')
        if os.path.exists(novels_dir):
            novel_files = []
            for root, dirs, files in os.walk(novels_dir):
                for file in files:
                    if file.endswith('.txt'):
                        novel_files.append(os.path.join(root, file))
            
            status['novels_exist'] = len(novel_files) > 0
            status['novels_count'] = len(novel_files)
            self.stats['novels_found'] = len(novel_files)
            
            print(f"✅ 找到 {len(novel_files)} 本小说")
        
        # 检查结构化数据
        structured_dir = os.path.join(self.output_dir, 'structured')
        if os.path.exists(structured_dir):
            structured_files = [f for f in os.listdir(structured_dir) 
                              if f.endswith('_structured.json')]
            status['structured_exist'] = len(structured_files) > 0
            status['structured_count'] = len(structured_files)
            self.stats['structured'] = len(structured_files)
            
            if structured_files:
                print(f"✅ 找到 {len(structured_files)} 个结构化数据文件")
        
        # 检查训练数据
        training_file = os.path.join(self.output_dir, 'processed', 'training_data.txt')
        if os.path.exists(training_file):
            with open(training_file, 'r', encoding='utf-8') as f:
                lines = [line for line in f if line.strip() and '\t' in line]
            status['training_data_exist'] = len(lines) > 0
            self.stats['training_samples'] = len(lines)
            
            if lines:
                print(f"✅ 找到训练数据: {len(lines)} 条样本")
        
        # 检查模型
        model_path = self.pipeline.model_path
        if os.path.exists(model_path):
            model_files = [
                os.path.join(model_path, 'best_model.h5'),
                os.path.join(model_path, 'final_model.h5'),
                os.path.join(model_path, 'vocab.json')
            ]
            status['model_exist'] = any(os.path.exists(f) for f in model_files)
            
            if status['model_exist']:
                print(f"✅ 找到已有模型: {model_path}")
        
        return status
    
    def execute_full_workflow(self, 
                             epochs: int = 10,
                             batch_size: int = 8,
                             use_ai: bool = False,
                             auto_fix: bool = True,
                             max_retries: int = 3) -> bool:
        """
        执行完整工作流程
        
        Args:
            epochs: 训练轮数
            batch_size: 批次大小
            use_ai: 是否使用AI
            auto_fix: 是否自动修复问题
            max_retries: 最大重试次数
        
        Returns:
            是否成功
        """
        print("\n" + "="*60)
        print("🚀 开始执行完整工作流程")
        print("="*60)
        
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # 1. 检查现有数据
                data_status = self.check_existing_data()
                
                if not data_status['novels_exist']:
                    print("\n❌ 未找到小说数据，无法继续")
                    return False
                
                # 2. 结构化处理（如果需要）
                if not data_status['structured_exist'] or retry_count > 0:
                    print("\n" + "="*60)
                    print("步骤 1.5: 结构化数据处理")
                    print("="*60)
                    
                    # 检查data_processor是否可用
                    if hasattr(self.pipeline, 'data_processor') and self.pipeline.data_processor:
                        # 查找小说目录
                        novels_dir = self.pipeline.novels_dir
                        if os.path.exists(novels_dir):
                            # 尝试从目录结构推断category
                            category = self._infer_category(novels_dir)
                            site = "m.shuhaige.net"  # 默认
                            
                            stats = self.pipeline.data_processor.process_batch(
                                novels_dir, category, site
                            )
                            
                            if stats['success'] > 0:
                                print(f"✅ 结构化处理完成: {stats['success']} 本")
                            else:
                                print("⚠️  结构化处理失败，继续执行")
                    else:
                        print("⚠️  数据处理器不可用，跳过结构化处理")
                
                # 3. 生成训练数据
                print("\n" + "="*60)
                print("步骤 3: 生成训练数据")
                print("="*60)
                
                # 优先使用增强版生成器
                training_file = None
                if hasattr(self.pipeline, 'enhanced_generator') and self.pipeline.enhanced_generator:
                    structured_dir = os.path.join(self.output_dir, 'structured')
                    if os.path.exists(structured_dir):
                        training_file = self.pipeline.enhanced_generator.generate_from_structured_data(
                            use_ai=use_ai
                        )
                
                # 如果增强版失败，使用传统方法
                if not training_file or not os.path.exists(training_file):
                    print("⚠️  增强版生成失败，使用传统方法")
                    if not self.pipeline.step3_generate_training_data(use_ai=use_ai):
                        if auto_fix:
                            print("⚠️  训练数据生成失败，尝试修复...")
                            # 删除可能有问题的文件
                            old_file = os.path.join(self.output_dir, 'processed', 'training_data.txt')
                            if os.path.exists(old_file):
                                os.remove(old_file)
                                print("   已删除旧训练数据文件")
                            
                            # 重试
                            if retry_count < max_retries - 1:
                                retry_count += 1
                                print(f"   重试 {retry_count}/{max_retries}")
                                continue
                        
                        print("❌ 训练数据生成失败")
                        return False
                    else:
                        training_file = os.path.join(self.output_dir, 'processed', 'training_data.txt')
                
                # 验证训练数据
                if training_file and os.path.exists(training_file):
                    valid_samples = self._validate_training_data(training_file)
                    if valid_samples == 0:
                        print("❌ 训练数据验证失败：没有有效样本")
                        if auto_fix and retry_count < max_retries - 1:
                            retry_count += 1
                            print(f"   重试 {retry_count}/{max_retries}")
                            continue
                        return False
                    
                    self.stats['training_samples'] = valid_samples
                    print(f"✅ 训练数据验证通过: {valid_samples} 条有效样本")
                
                # 4. 训练模型
                print("\n" + "="*60)
                print("步骤 4: 训练模型")
                print("="*60)
                
                if not self.pipeline.step4_train(epochs=epochs, batch_size=batch_size, incremental=False):
                    print("❌ 模型训练失败")
                    if auto_fix and retry_count < max_retries - 1:
                        retry_count += 1
                        print(f"   重试 {retry_count}/{max_retries}")
                        continue
                    return False
                
                self.stats['model_trained'] = True
                
                # 5. 验证模型
                print("\n" + "="*60)
                print("📋 最终验证")
                print("="*60)
                
                model_files = [
                    os.path.join(self.pipeline.model_path, 'best_model.h5'),
                    os.path.join(self.pipeline.model_path, 'final_model.h5'),
                    os.path.join(self.pipeline.model_path, 'vocab.json')
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
                
                # 6. 清理临时文件
                self.cleanup_temp_files()
                
                print("\n" + "="*60)
                print("✅ 完整工作流程执行成功！")
                print("="*60)
                print(f"\n📊 执行统计:")
                print(f"   小说数量: {self.stats['novels_found']}")
                print(f"   结构化数据: {self.stats['structured']}")
                print(f"   训练样本: {self.stats['training_samples']}")
                print(f"   模型训练: {'成功' if self.stats['model_trained'] else '失败'}")
                
                return True
                
            except Exception as e:
                print(f"\n❌ 执行过程中出错: {e}")
                import traceback
                traceback.print_exc()
                
                self.stats['errors'].append(str(e))
                
                if auto_fix and retry_count < max_retries - 1:
                    retry_count += 1
                    print(f"\n🔄 自动修复并重试 {retry_count}/{max_retries}")
                    continue
                else:
                    return False
        
        return False
    
    def _infer_category(self, novels_dir: str) -> str:
        """从目录结构推断小说类型"""
        # 检查第一层目录
        if os.path.exists(novels_dir):
            items = os.listdir(novels_dir)
            for item in items:
                item_path = os.path.join(novels_dir, item)
                if os.path.isdir(item_path):
                    # 检查是否是类型目录
                    common_categories = ['都市', '玄幻', '言情', '武侠', '科幻', '悬疑']
                    if item in common_categories:
                        return item
            
            # 检查第二层目录
            for item in items:
                item_path = os.path.join(novels_dir, item)
                if os.path.isdir(item_path):
                    sub_items = os.listdir(item_path)
                    for sub_item in sub_items:
                        if sub_item in common_categories:
                            return sub_item
        
        return '都市'  # 默认
    
    def _validate_training_data(self, training_file: str) -> int:
        """验证训练数据"""
        valid_count = 0
        
        try:
            with open(training_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    parts = line.split('\t')
                    if len(parts) >= 3:
                        try:
                            orig = parts[0].strip()
                            rew = parts[1].strip()
                            style_id = int(parts[2])
                            
                            if len(orig) >= 10 and len(rew) >= 10 and 0 <= style_id <= 20:
                                valid_count += 1
                        except (ValueError, IndexError):
                            continue
        except Exception as e:
            print(f"⚠️  验证训练数据时出错: {e}")
        
        return valid_count
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        print("\n" + "="*60)
        print("🧹 清理临时文件")
        print("="*60)
        
        cleaned_count = 0
        cleaned_size = 0
        
        # 清理.temp目录
        temp_dirs = []
        for root, dirs, files in os.walk(self.output_dir):
            if '.temp' in root:
                temp_dirs.append(root)
        
        for temp_dir in temp_dirs:
            try:
                size = sum(os.path.getsize(os.path.join(dirpath, filename))
                          for dirpath, dirnames, filenames in os.walk(temp_dir)
                          for filename in filenames)
                shutil.rmtree(temp_dir)
                cleaned_count += 1
                cleaned_size += size
                print(f"   🗑️  已清理: {os.path.basename(temp_dir)} ({size/1024/1024:.2f} MB)")
            except Exception as e:
                print(f"   ⚠️  清理失败 {temp_dir}: {e}")
        
        # 清理进度文件
        progress_files = []
        for root, dirs, files in os.walk(self.output_dir):
            for file in files:
                if file.endswith('_progress.json') or file.endswith('.tmp'):
                    progress_files.append(os.path.join(root, file))
        
        for progress_file in progress_files:
            try:
                size = os.path.getsize(progress_file)
                os.remove(progress_file)
                cleaned_count += 1
                cleaned_size += size
            except Exception as e:
                pass
        
        if cleaned_count > 0:
            print(f"\n✅ 清理完成: {cleaned_count} 个文件/目录，释放 {cleaned_size/1024/1024:.2f} MB")
        else:
            print("ℹ️  没有需要清理的临时文件")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='自动执行完整工作流程')
    parser.add_argument('--epochs', type=int, default=10, help='训练轮数')
    parser.add_argument('--batch-size', type=int, default=8, help='批次大小')
    parser.add_argument('--use-ai', action='store_true', help='使用AI生成改写样本')
    parser.add_argument('--no-auto-fix', action='store_true', help='禁用自动修复')
    parser.add_argument('--max-retries', type=int, default=3, help='最大重试次数')
    
    args = parser.parse_args()
    
    executor = AutoExecutor()
    
    success = executor.execute_full_workflow(
        epochs=args.epochs,
        batch_size=args.batch_size,
        use_ai=args.use_ai,
        auto_fix=not args.no_auto_fix,
        max_retries=args.max_retries
    )
    
    if success:
        print("\n🎉 所有任务完成！")
        sys.exit(0)
    else:
        print("\n❌ 执行失败，请检查错误信息")
        sys.exit(1)


if __name__ == '__main__':
    main()

