#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一的数据处理流水线
整合爬取、整理、生成训练数据、训练模型等完整流程
"""

import os
import sys
import argparse
from typing import Optional, List

# 添加路径
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scraper.multi_site_scraper import MultiSiteScraper
from scraper.novel_analyzer import NovelAnalyzer
from core.training_data_generator import TrainingDataGenerator
from ai.models.train_model import main as train_main
from ai.models.incremental_train import IncrementalTrainer

# 可选导入：数据整理功能
try:
    from utils.data_organizer import DataOrganizer
    HAS_DATA_ORGANIZER = True
except ImportError:
    HAS_DATA_ORGANIZER = False


class DataPipeline:
    """统一的数据处理流水线"""
    
    def __init__(self, output_dir: str = "data/training"):
        """
        初始化流水线
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = os.path.abspath(output_dir)
        self.novels_dir = os.path.join(self.output_dir, 'novels')
        self.processed_dir = os.path.join(self.output_dir, 'processed')
        # 统一模型路径：使用绝对路径，确保路径正确
        model_path_relative = os.path.join(self.output_dir, '..', 'models', 'text_rewriter_model')
        self.model_path = os.path.abspath(os.path.normpath(model_path_relative))
        
        # 初始化组件
        self.scraper = MultiSiteScraper(output_dir)
        self.analyzer = NovelAnalyzer()
        self.data_generator = TrainingDataGenerator(output_dir)
        
        # 导入新的智能处理模块
        try:
            import sys as sys_module
            core_path = os.path.dirname(__file__)
            if core_path not in sys_module.path:
                sys_module.path.insert(0, core_path)
            
            from data_processor import DataProcessor
            from enhanced_training_data_generator import EnhancedTrainingDataGenerator
            self.data_processor = DataProcessor(output_dir)
            self.enhanced_generator = EnhancedTrainingDataGenerator(output_dir)
        except ImportError:
            self.data_processor = None
            self.enhanced_generator = None
            # 静默失败，不影响主流程
            pass
    
    def step1_scrape(self, site_name: str, category: str, count: int, 
                     filter_completed: bool = True) -> bool:
        """
        步骤1: 爬取小说
        
        Args:
            site_name: 网站名称
            category: 小说类型
            count: 爬取数量
            filter_completed: 是否只爬取已完结的
        
        Returns:
            是否成功
        """
        print("\n" + "="*60)
        print("步骤 1/5: 爬取小说")
        print("="*60)
        
        stats = self.scraper.batch_scrape(site_name, category, count, filter_completed)
        
        if stats['success'] > 0:
            print(f"\n✅ 爬取完成: 成功 {stats['success']} 本，失败 {stats['failed']} 本")
            return True
        else:
            print(f"\n❌ 爬取失败: 没有成功爬取任何小说")
            return False
    
    def step2_organize(self, organize_data: bool = False) -> bool:
        """
        步骤2: 整理数据（可选）或分析小说
        
        Args:
            organize_data: 是否先整理数据（清理、分类等）
        
        Returns:
            是否成功
        """
        if organize_data and HAS_DATA_ORGANIZER:
            print("\n" + "="*60)
            print("步骤 2/6: 整理数据")
            print("="*60)
            
            organizer = DataOrganizer(self.novels_dir, self.processed_dir)
            summary = organizer.organize()
            
            if summary['stats']['processed_files'] > 0:
                print(f"\n✅ 数据整理完成")
                # 整理后，使用processed_dir作为数据源
                data_source = self.processed_dir
            else:
                print(f"\n⚠️  数据整理失败，使用原始数据")
                data_source = self.novels_dir
        else:
            data_source = self.novels_dir
        
        print("\n" + "="*60)
        print("步骤 2/6: 分析小说特征")
        print("="*60)
        
        results = self.analyzer.analyze_batch(data_source)
        
        if results:
            summary = self.analyzer.generate_summary()
            analysis_file = os.path.join(self.processed_dir, 'analysis.json')
            self.analyzer.save_analysis(analysis_file)
            
            print(f"\n✅ 分析完成:")
            print(f"   总小说数: {summary.get('total_novels', 0)}")
            print(f"   总字符数: {summary.get('total_chars', 0):,}")
            return True
        else:
            print(f"\n⚠️  分析失败: 没有找到可分析的小说")
            return False
    
    def step3_generate_training_data(self, use_ai: bool = False, 
                                     source_dir: Optional[str] = None) -> bool:
        """
        步骤3: 生成训练数据
        
        Args:
            use_ai: 是否使用AI生成改写样本
        
        Returns:
            是否成功
        """
        print("\n" + "="*60)
        print("步骤 3/6: 生成训练数据")
        print("="*60)
        
        # 如果指定了源目录，临时修改生成器的novels_dir
        # 如果使用processed目录，提供novels目录作为回退
        if source_dir:
            original_novels_dir = self.data_generator.novels_dir
            self.data_generator.novels_dir = source_dir
            # 如果source_dir是processed，提供novels作为回退
            fallback_dir = self.novels_dir if 'processed' in source_dir else None
        else:
            fallback_dir = None
        
        training_file = self.data_generator.generate_from_novels(use_ai=use_ai, fallback_dir=fallback_dir)
        
        # 恢复原始目录
        if source_dir:
            self.data_generator.novels_dir = original_novels_dir
        
        if training_file and os.path.exists(training_file):
            with open(training_file, 'r', encoding='utf-8') as f:
                lines = [line for line in f if line.strip()]
            
            print(f"\n✅ 训练数据生成完成: {len(lines)} 条样本")
            return len(lines) > 0
        else:
            print(f"\n❌ 训练数据生成失败")
            return False
    
    def step4_train(self, epochs: int = 20, batch_size: int = 16, 
                    incremental: bool = False) -> bool:
        """
        步骤4: 训练模型
        
        Args:
            epochs: 训练轮数
            batch_size: 批次大小
            incremental: 是否增量训练
        
        Returns:
            是否成功
        """
        print("\n" + "="*60)
        print(f"步骤 4/5: {'增量' if incremental else '基础'}训练模型")
        print("="*60)
        
        training_file = os.path.join(self.processed_dir, 'training_data.txt')
        
        if not os.path.exists(training_file):
            print(f"❌ 训练数据文件不存在: {training_file}")
            return False
        
        # 检查数据量
        with open(training_file, 'r', encoding='utf-8') as f:
            lines = [line for line in f if line.strip()]
        
        if len(lines) < 10:
            print(f"⚠️  警告: 训练数据量较少 ({len(lines)} 条)")
            return False
        
        if incremental:
            if IncrementalTrainer is None:
                print(f"❌ 无法导入IncrementalTrainer，请检查依赖")
                return False
            
            # 增量训练
            trainer = IncrementalTrainer(self.model_path)
            if trainer.load_existing_model():
                success = trainer.incremental_train(training_file, epochs=epochs)
                if success:
                    trainer.merge_models(keep_best=True)
                return success
            else:
                print(f"⚠️  未找到已有模型，将进行基础训练")
                incremental = False
        
        if not incremental:
            # 基础训练
            if train_main is None:
                print(f"❌ 无法导入train_model，请检查依赖")
                return False
            
            old_argv = sys.argv
            try:
                sys.argv = [
                    'train_model.py',
                    training_file,
                    '--model-path', self.model_path,
                    '--epochs', str(epochs),
                    '--batch-size', str(batch_size)
                ]
                train_main()
                
                # 验证模型是否成功生成
                model_files = [
                    os.path.join(self.model_path, 'best_model.h5'),
                    os.path.join(self.model_path, 'final_model.h5'),
                    os.path.join(self.model_path, 'vocab.json')
                ]
                
                all_exist = all(os.path.exists(f) for f in model_files)
                if all_exist:
                    print(f"\n✅ 模型已成功生成:")
                    print(f"   模型路径: {self.model_path}")
                    for f in model_files:
                        size = os.path.getsize(f) / 1024 / 1024
                        print(f"   - {os.path.basename(f)} ({size:.2f} MB)")
                    return True
                else:
                    print(f"\n⚠️  警告: 部分模型文件未生成")
                    print(f"   期望路径: {self.model_path}")
                    missing = [f for f in model_files if not os.path.exists(f)]
                    print(f"   缺失文件: {[os.path.basename(f) for f in missing]}")
                    return False
                    
            except Exception as e:
                print(f"\n❌ 训练失败: {e}")
                import traceback
                traceback.print_exc()
                return False
            finally:
                sys.argv = old_argv
        
        return False
    
    def run_full_pipeline(self, site_name: Optional[str] = None, 
                         category: Optional[str] = None, 
                         count: int = 10,
                         use_ai: bool = False,
                         epochs: int = 20,
                         batch_size: int = 16,
                         incremental: bool = False,
                         organize_data: bool = False,
                         skip_steps: Optional[List[str]] = None) -> bool:
        """
        运行完整流水线
        
        Args:
            site_name: 网站名称
            category: 小说类型
            count: 爬取数量
            use_ai: 是否使用AI生成改写样本
            epochs: 训练轮数
            batch_size: 批次大小
            incremental: 是否增量训练
            skip_steps: 跳过的步骤列表
        
        Returns:
            是否成功
        """
        skip_steps = skip_steps or []
        
        print("\n" + "="*60)
        print("🚀 完整数据处理流水线")
        print("="*60)
        print(f"\n配置:")
        if site_name and category:
            print(f"  网站: {site_name}")
            print(f"  类型: {category}")
            print(f"  数量: {count} 本")
        else:
            print(f"  模式: 数据整理模式（已有数据）")
        print(f"  使用AI: {'是' if use_ai else '否'}")
        print(f"  训练模式: {'增量' if incremental else '基础'}")
        print(f"  训练轮数: {epochs}")
        if organize_data:
            print(f"  数据整理: 是")
        
        # 步骤1: 爬取（仅当提供了site_name和category时）
        if site_name and category and 'scrape' not in skip_steps:
            if not self.step1_scrape(site_name, category, count):
                print("\n⚠️  爬取步骤失败，但继续后续步骤...")
        elif site_name and category:
            print("\n⏭️  跳过爬取步骤")
        
        # 步骤1.5: 结构化数据处理（在爬取后立即执行）
        if 'structure' not in skip_steps and 'scrape' not in skip_steps and site_name and category:
            if not self.step1_5_structure_data(category=category, site=site_name):
                print("\n⚠️  结构化处理失败，继续执行后续步骤")
        else:
            print("\n⏭️  跳过结构化处理步骤")
        
        # 步骤2: 整理数据或分析
        if 'organize' not in skip_steps and 'analyze' not in skip_steps:
            # 如果启用了数据整理，先整理再分析
            if organize_data:
                self.step2_organize(organize_data=True)
            else:
                self.step2_organize(organize_data=False)
        else:
            if 'organize' in skip_steps:
                print("\n⏭️  跳过数据整理步骤")
            if 'analyze' in skip_steps:
                print("\n⏭️  跳过分析步骤")
        
        # 步骤3: 生成训练数据
        if 'generate' not in skip_steps:
            # 优先使用增强版生成器（如果结构化数据存在）
            if self.enhanced_generator and os.path.exists(os.path.join(self.output_dir, 'structured')):
                print("\n" + "="*60)
                print("步骤 3/6: 生成训练数据（增强版）")
                print("="*60)
                
                training_file = self.enhanced_generator.generate_from_structured_data(use_ai=use_ai)
                if training_file and os.path.exists(training_file):
                    with open(training_file, 'r', encoding='utf-8') as f:
                        lines = [line for line in f if line.strip()]
                    print(f"\n✅ 训练数据生成完成: {len(lines)} 条样本")
                else:
                    print("\n⚠️  增强版生成失败，使用传统方法")
                    # 回退到传统方法
                    source_dir = self.processed_dir if organize_data and HAS_DATA_ORGANIZER else None
                    if not self.step3_generate_training_data(use_ai=use_ai, source_dir=source_dir):
                        print("\n❌ 生成训练数据失败，无法继续训练")
                        return False
            else:
                # 使用传统方法
                source_dir = self.processed_dir if organize_data and HAS_DATA_ORGANIZER else None
                if not self.step3_generate_training_data(use_ai=use_ai, source_dir=source_dir):
                    print("\n❌ 生成训练数据失败，无法继续训练")
                    return False
        else:
            print("\n⏭️  跳过生成步骤")
        
        # 步骤4: 训练
        if 'train' not in skip_steps:
            if not self.step4_train(epochs=epochs, batch_size=batch_size, incremental=incremental):
                print("\n❌ 训练失败")
                return False
        else:
            print("\n⏭️  跳过训练步骤")
        
        # 最终验证：检查关键输出
        print("\n" + "="*60)
        print("📋 最终验证")
        print("="*60)
        
        # 检查训练数据
        training_file = os.path.join(self.processed_dir, 'training_data.txt')
        if os.path.exists(training_file):
            with open(training_file, 'r', encoding='utf-8') as f:
                lines = [line for line in f if line.strip()]
            print(f"✅ 训练数据: {len(lines)} 条样本")
        else:
            print(f"⚠️  训练数据文件不存在")
        
        # 检查模型文件
        if 'train' not in skip_steps:
            model_files = [
                os.path.join(self.model_path, 'best_model.h5'),
                os.path.join(self.model_path, 'final_model.h5'),
                os.path.join(self.model_path, 'vocab.json')
            ]
            existing = [f for f in model_files if os.path.exists(f)]
            if existing:
                print(f"✅ 模型文件: {len(existing)}/{len(model_files)} 个文件已生成")
                print(f"   模型路径: {self.model_path}")
            else:
                print(f"❌ 模型文件: 未找到模型文件")
                print(f"   期望路径: {self.model_path}")
        
        print("\n" + "="*60)
        print("✅ 完整流水线执行完成！")
        print("="*60)
        
        return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='统一的数据处理流水线',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 完整流程（爬取 → 分析 → 生成 → 训练）
  python3 scripts/core/pipeline.py --site m.shuhaige.net --category 都市 --count 10
  
  # 数据整理模式（已有数据）
  python3 scripts/core/pipeline.py --organize --skip scrape
  
  # 只训练（已有数据）
  python3 scripts/core/pipeline.py --skip scrape,analyze,generate
  
  # 增量训练
  python3 scripts/core/pipeline.py --incremental --skip scrape,analyze,generate
        """
    )
    
    parser.add_argument('--site', type=str, default=None,
                       help='网站名称（如：m.shuhaige.net），不提供则使用已有数据')
    parser.add_argument('--category', type=str, default=None,
                       help='小说类型（如：都市、玄幻等），不提供则使用已有数据')
    parser.add_argument('--count', type=int, default=10,
                       help='爬取数量（默认：10，仅爬取模式需要）')
    parser.add_argument('--output', '-o', default='data/training',
                       help='输出目录（默认：data/training）')
    parser.add_argument('--use-ai', action='store_true',
                       help='使用AI生成改写样本')
    parser.add_argument('--epochs', type=int, default=20,
                       help='训练轮数（默认：20）')
    parser.add_argument('--batch-size', type=int, default=16,
                       help='批次大小（默认：16）')
    parser.add_argument('--incremental', action='store_true',
                       help='增量训练（默认：基础训练）')
    parser.add_argument('--skip', type=str, default='',
                       help='跳过的步骤，用逗号分隔（如：scrape,analyze,generate）')
    parser.add_argument('--organize', action='store_true',
                       help='整理数据（清理、分类等）')
    parser.add_argument('--filter-completed', action='store_true', default=True,
                       help='只爬取已完结的小说（默认启用，仅爬取模式）')
    parser.add_argument('--no-filter-completed', dest='filter_completed', action='store_false',
                       help='不筛选，爬取所有小说（仅爬取模式）')
    
    args = parser.parse_args()
    
    skip_steps = [s.strip() for s in args.skip.split(',') if s.strip()]
    
    pipeline = DataPipeline(args.output)
    
    # 验证参数
    if args.site and not args.category:
        parser.error("--site 需要配合 --category 使用")
    if args.category and not args.site:
        parser.error("--category 需要配合 --site 使用")
    
    success = pipeline.run_full_pipeline(
        site_name=args.site,
        category=args.category,
        count=args.count,
        use_ai=args.use_ai,
        epochs=args.epochs,
        batch_size=args.batch_size,
        incremental=args.incremental,
        organize_data=args.organize,
        skip_steps=skip_steps
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

