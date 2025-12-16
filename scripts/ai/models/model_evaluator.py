#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型评估模块
用于评估训练好的模型性能
"""

import os
import json
import numpy as np
from typing import List, Dict, Tuple
from collections import Counter

try:
    from .tensorflow_model import TensorFlowTextRewriter
except ImportError:
    from tensorflow_model import TensorFlowTextRewriter


class ModelEvaluator:
    """模型评估器"""
    
    def __init__(self, model_path: str = "models/text_rewriter_model"):
        """
        初始化评估器
        
        Args:
            model_path: 模型路径
        """
        self.model_path = model_path
        self.rewriter = TensorFlowTextRewriter(model_path=model_path)
        self.model_loaded = False
    
    def load_model(self) -> bool:
        """加载模型"""
        if self.rewriter.load_vocab() and self.rewriter.load_model():
            self.model_loaded = True
            return True
        return False
    
    def evaluate_accuracy(self, test_data: List[Tuple[str, str, int]]) -> Dict:
        """
        评估模型准确率
        
        Args:
            test_data: 测试数据列表，每个元素为 (原始文本, 目标文本, 风格ID)
        
        Returns:
            评估结果字典
        """
        if not self.model_loaded:
            if not self.load_model():
                return {'error': '模型未加载'}
        
        print(f"\n📊 开始评估模型...")
        print(f"   测试样本数: {len(test_data)}")
        
        results = {
            'total': len(test_data),
            'correct': 0,
            'partial_correct': 0,
            'failed': 0,
            'avg_length_ratio': 0.0,
            'style_accuracy': {},
        }
        
        length_ratios = []
        
        for i, (original, target, style) in enumerate(test_data):
            try:
                # 使用模型改写
                rewritten = self.rewriter.rewrite(original, style, temperature=0.7)
                
                # 计算长度比例
                if len(original) > 0:
                    length_ratio = len(rewritten) / len(original)
                    length_ratios.append(length_ratio)
                
                # 简单的准确率评估（基于字符重叠）
                overlap = self._calculate_overlap(rewritten, target)
                
                if overlap > 0.8:
                    results['correct'] += 1
                elif overlap > 0.5:
                    results['partial_correct'] += 1
                else:
                    results['failed'] += 1
                
                # 按风格统计
                if style not in results['style_accuracy']:
                    results['style_accuracy'][style] = {'total': 0, 'correct': 0}
                results['style_accuracy'][style]['total'] += 1
                if overlap > 0.8:
                    results['style_accuracy'][style]['correct'] += 1
                
                if (i + 1) % 100 == 0:
                    print(f"   进度: {i+1}/{len(test_data)}")
            
            except Exception as e:
                results['failed'] += 1
                if results['failed'] <= 5:
                    print(f"   ⚠️  评估样本 {i+1} 时出错: {e}")
        
        # 计算平均长度比例
        if length_ratios:
            results['avg_length_ratio'] = sum(length_ratios) / len(length_ratios)
        
        # 计算总体准确率
        results['accuracy'] = results['correct'] / results['total'] if results['total'] > 0 else 0
        results['partial_accuracy'] = (results['correct'] + results['partial_correct']) / results['total'] if results['total'] > 0 else 0
        
        # 计算各风格准确率
        for style in results['style_accuracy']:
            stats = results['style_accuracy'][style]
            stats['accuracy'] = stats['correct'] / stats['total'] if stats['total'] > 0 else 0
        
        return results
    
    def _calculate_overlap(self, text1: str, text2: str) -> float:
        """
        计算两个文本的重叠度
        
        Args:
            text1: 文本1
            text2: 文本2
        
        Returns:
            重叠度（0-1）
        """
        if not text1 or not text2:
            return 0.0
        
        # 使用字符级别的重叠
        chars1 = set(text1)
        chars2 = set(text2)
        
        if not chars1 or not chars2:
            return 0.0
        
        intersection = chars1 & chars2
        union = chars1 | chars2
        
        return len(intersection) / len(union) if union else 0.0
    
    def generate_report(self, results: Dict, output_file: str = None):
        """
        生成评估报告
        
        Args:
            results: 评估结果
            output_file: 输出文件路径
        """
        print(f"\n{'='*60}")
        print("📊 模型评估报告")
        print(f"{'='*60}")
        print(f"\n总体统计:")
        print(f"  总样本数: {results.get('total', 0)}")
        print(f"  完全正确: {results.get('correct', 0)} ({results.get('accuracy', 0)*100:.1f}%)")
        print(f"  部分正确: {results.get('partial_correct', 0)}")
        print(f"  失败: {results.get('failed', 0)}")
        print(f"  总体准确率: {results.get('accuracy', 0)*100:.2f}%")
        print(f"  部分准确率: {results.get('partial_accuracy', 0)*100:.2f}%")
        print(f"  平均长度比例: {results.get('avg_length_ratio', 0):.2f}")
        
        if results.get('style_accuracy'):
            print(f"\n各风格准确率:")
            for style, stats in sorted(results['style_accuracy'].items()):
                accuracy = stats.get('accuracy', 0)
                print(f"  风格 {style}: {stats['correct']}/{stats['total']} ({accuracy*100:.1f}%)")
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n📄 报告已保存: {output_file}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='模型评估工具')
    parser.add_argument('test_data_file', help='测试数据文件（TSV格式）')
    parser.add_argument('--model-path', default='models/text_rewriter_model',
                       help='模型路径')
    parser.add_argument('--output', '-o', help='输出报告文件')
    
    args = parser.parse_args()
    
    # 加载测试数据
    test_data = []
    with open(args.test_data_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split('\t')
            if len(parts) >= 3:
                test_data.append((parts[0], parts[1], int(parts[2])))
    
    if not test_data:
        print("❌ 没有测试数据")
        return
    
    # 评估模型
    evaluator = ModelEvaluator(args.model_path)
    results = evaluator.evaluate_accuracy(test_data)
    
    # 生成报告
    evaluator.generate_report(results, args.output)


if __name__ == '__main__':
    main()

