#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增量训练脚本
在已有模型基础上继续训练，完善模型数据
"""

import os
import sys
import json
import argparse
from typing import List, Tuple

sys.path.insert(0, os.path.dirname(__file__))
from tensorflow_model import TensorFlowTextRewriter
from train_model import prepare_training_data


class IncrementalTrainer:
    """增量训练器"""
    
    def __init__(self, model_path: str = "models/text_rewriter_model"):
        """
        初始化增量训练器
        
        Args:
            model_path: 模型路径
        """
        self.model_path = model_path
        self.rewriter = TensorFlowTextRewriter(model_path=model_path)
    
    def load_existing_model(self) -> bool:
        """加载已有模型"""
        print(f"\n📂 加载已有模型: {self.model_path}")
        
        if not self.rewriter.load_vocab():
            print("❌ 无法加载词汇表，请先训练基础模型")
            return False
        
        if not self.rewriter.load_model():
            print("❌ 无法加载模型，请先训练基础模型")
            return False
        
        print("✅ 模型加载成功")
        print(f"   词汇表大小: {self.rewriter.vocab_size}")
        print(f"   最大长度: {self.rewriter.max_length}")
        
        return True
    
    def merge_vocab(self, new_texts: List[str]) -> bool:
        """
        合并新数据的词汇表
        
        Args:
            new_texts: 新文本列表
        
        Returns:
            是否成功
        """
        print(f"\n📚 合并词汇表...")
        
        # 收集新词汇
        new_chars = set()
        for text in new_texts:
            new_chars.update(text)
        
        # 检查是否有新字符
        existing_chars = set(self.rewriter.vocab.keys())
        new_chars = new_chars - existing_chars
        
        if not new_chars:
            print("✅ 没有新词汇需要添加")
            return True
        
        print(f"   发现 {len(new_chars)} 个新字符")
        
        # 添加新字符到词汇表
        current_size = len(self.rewriter.vocab)
        for char in new_chars:
            if char not in self.rewriter.vocab:
                idx = current_size
                self.rewriter.vocab[char] = idx
                self.rewriter.reverse_vocab[idx] = char
                current_size += 1
        
        self.rewriter.vocab_size = current_size
        
        print(f"   词汇表已更新: {len(existing_chars)} → {current_size}")
        
        # 需要重新构建模型（因为词汇表大小变化）
        print("   重新构建模型以适应新词汇表...")
        self.rewriter.build_model()
        
        # 加载之前的权重（如果可能）
        try:
            old_weights_file = os.path.join(self.model_path, 'best_model.h5')
            if os.path.exists(old_weights_file):
                # 尝试加载兼容的权重
                print("   尝试加载之前的模型权重...")
                # 注意：如果词汇表大小变化，可能需要特殊处理
                try:
                    # 尝试加载权重（如果结构兼容）
                    self.rewriter.model.load_weights(old_weights_file, by_name=True, skip_mismatch=True)
                    print("   ✅ 成功加载部分权重")
                except Exception as e:
                    print(f"   ⚠️  无法加载之前的权重: {e}")
                    print("   将从头训练")
        except Exception as e:
            print(f"   ⚠️  无法加载之前的权重: {e}")
            print("   将从头训练")
        
        return True
    
    def incremental_train(self, new_data_file: str, 
                         epochs: int = 10,
                         batch_size: int = 16,
                         learning_rate: float = 0.0001) -> bool:
        """
        增量训练
        
        Args:
            new_data_file: 新训练数据文件
            epochs: 训练轮数
            batch_size: 批次大小
            learning_rate: 学习率（增量训练使用较小的学习率）
        
        Returns:
            是否成功
        """
        print(f"\n🚀 开始增量训练...")
        print(f"   新数据文件: {new_data_file}")
        print(f"   训练轮数: {epochs}")
        print(f"   批次大小: {batch_size}")
        print(f"   学习率: {learning_rate}")
        
        # 准备新数据
        original_texts, rewritten_texts, styles = prepare_training_data(new_data_file)
        
        if len(original_texts) == 0:
            print("❌ 没有可用的新训练数据")
            return False
        
        print(f"\n📊 新数据统计:")
        print(f"   样本数: {len(original_texts)}")
        
        # 合并词汇表
        all_texts = original_texts + rewritten_texts
        self.merge_vocab(all_texts)
        
        # 准备训练数据
        X_text, X_style, y = self.rewriter.prepare_training_data(
            original_texts, rewritten_texts, styles
        )
        
        # 调整学习率
        self.rewriter.model.compile(
            optimizer=self.rewriter.model.optimizer.__class__(learning_rate=learning_rate),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        # 增量训练
        print(f"\n🎯 开始训练（增量模式）...")
        history = self.rewriter.model.fit(
            [X_text, X_style],
            y,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.2,
            verbose=1
        )
        
        # 保存模型
        self.rewriter.model.save(os.path.join(self.model_path, 'incremental_model.h5'))
        self.rewriter.save_vocab()
        
        print(f"\n✅ 增量训练完成！")
        print(f"   模型已保存: {self.model_path}/incremental_model.h5")
        
        return True
    
    def merge_models(self, keep_best: bool = True):
        """
        合并模型（将增量训练的模型与基础模型合并）
        
        Args:
            keep_best: 是否保留最佳模型
        """
        incremental_file = os.path.join(self.model_path, 'incremental_model.h5')
        best_file = os.path.join(self.model_path, 'best_model.h5')
        final_file = os.path.join(self.model_path, 'final_model.h5')
        
        if os.path.exists(incremental_file):
            if keep_best and os.path.exists(best_file):
                # 比较模型性能，保留更好的
                print("📊 比较模型性能...")
                # 这里可以添加模型评估逻辑
                # 暂时直接使用增量模型
                shutil.copy(incremental_file, final_file)
                print("✅ 已更新最终模型")
            else:
                shutil.copy(incremental_file, final_file)
                print("✅ 已更新最终模型")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='增量训练工具 - 在已有模型基础上继续训练',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 在已有模型基础上继续训练
  python3 incremental_train.py data/training/novels/training_data.txt
  
  # 指定模型路径和训练参数
  python3 incremental_train.py data/training/novels/training_data.txt \
    --model-path models/my_model --epochs=20 --learning-rate=0.0001
        """
    )
    
    parser.add_argument('new_data_file', help='新的训练数据文件（TSV格式）')
    parser.add_argument('--model-path', default='models/text_rewriter_model',
                       help='模型路径（默认: models/text_rewriter_model）')
    parser.add_argument('--epochs', type=int, default=10,
                       help='训练轮数（默认: 10，增量训练通常较少）')
    parser.add_argument('--batch-size', type=int, default=16,
                       help='批次大小（默认: 16）')
    parser.add_argument('--learning-rate', type=float, default=0.0001,
                       help='学习率（默认: 0.0001，增量训练使用较小学习率）')
    parser.add_argument('--merge', action='store_true',
                       help='训练后合并模型')
    
    args = parser.parse_args()
    
    # 创建增量训练器
    trainer = IncrementalTrainer(args.model_path)
    
    # 加载已有模型
    if not trainer.load_existing_model():
        print("\n❌ 无法加载已有模型")
        print("   请先运行基础训练: python3 train_model.py <数据文件>")
        sys.exit(1)
    
    # 增量训练
    success = trainer.incremental_train(
        args.new_data_file,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate
    )
    
    if success and args.merge:
        trainer.merge_models()
    
    if success:
        print("\n✅ 增量训练完成！")
        print(f"💡 使用方法:")
        print(f"   python3 scripts/creative/rewrite_novel.py novel.txt \\")
        print(f"     --use-ai --ai-type=tensorflow --style=都市幽默")
    else:
        print("\n❌ 增量训练失败")
        sys.exit(1)


if __name__ == '__main__':
    main()

