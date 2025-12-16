#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据增强模块
用于增强训练数据，提高模型性能
"""

import re
import random
from typing import List, Tuple
from collections import Counter


class DataEnhancer:
    """数据增强器"""
    
    # 同义词替换（示例，实际可以使用更完整的词典）
    SYNONYMS = {
        '说': ['说道', '讲', '言道', '开口'],
        '看': ['瞧', '望', '瞅', '观察'],
        '走': ['行', '步', '移动', '前进'],
        '想': ['思考', '考虑', '思索', '琢磨'],
        '好': ['不错', '很好', '棒', '优秀'],
        '大': ['巨大', '庞大', '宏大', '硕大'],
        '小': ['微小', '细小', '迷你', '袖珍'],
    }
    
    # 句式变换模式
    SENTENCE_PATTERNS = [
        # 主动变被动
        (r'(.+?)被(.+?)(.+?)', r'\2被\1\3'),
        # 添加修饰词
        (r'(.+?)([的地得])(.+?)', r'\1非常\2\3'),
    ]
    
    @classmethod
    def synonym_replacement(cls, text: str, ratio: float = 0.1) -> str:
        """
        同义词替换
        
        Args:
            text: 原始文本
            ratio: 替换比例（0-1）
        
        Returns:
            增强后的文本
        """
        words = list(text)
        replace_count = int(len(words) * ratio)
        replace_indices = random.sample(range(len(words)), min(replace_count, len(words)))
        
        result = list(text)
        for idx in replace_indices:
            char = result[idx]
            if char in cls.SYNONYMS:
                synonyms = cls.SYNONYMS[char]
                result[idx] = random.choice(synonyms)[0]  # 取第一个字符
        
        return ''.join(result)
    
    @classmethod
    def back_translation_simulation(cls, text: str) -> str:
        """
        模拟回译（简化版）
        通过同义词替换和句式微调模拟回译效果
        
        Args:
            text: 原始文本
        
        Returns:
            增强后的文本
        """
        # 同义词替换
        result = cls.synonym_replacement(text, ratio=0.15)
        
        # 句式微调
        sentences = re.split(r'[。！？]', result)
        enhanced_sentences = []
        
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            
            # 随机添加或移除修饰词
            if random.random() < 0.3:
                # 添加修饰词
                sent = re.sub(r'([的地得])', r'非常\1', sent, count=1)
            elif random.random() < 0.2:
                # 移除部分修饰词
                sent = re.sub(r'非常([的地得])', r'\1', sent)
            
            enhanced_sentences.append(sent)
        
        return '。'.join(enhanced_sentences) + '。'
    
    @classmethod
    def generate_variations(cls, original: str, rewritten: str, count: int = 3) -> List[Tuple[str, str]]:
        """
        生成文本变体
        
        Args:
            original: 原始文本
            rewritten: 改写文本
            count: 生成变体数量
        
        Returns:
            (原始文本变体, 改写文本变体) 列表
        """
        variations = []
        
        for _ in range(count):
            # 对原始文本进行轻微增强
            orig_var = cls.synonym_replacement(original, ratio=0.05)
            # 对改写文本进行增强
            rew_var = cls.back_translation_simulation(rewritten)
            
            variations.append((orig_var, rew_var))
        
        return variations
    
    @classmethod
    def balance_dataset(cls, samples: List[dict]) -> List[dict]:
        """
        平衡数据集（确保各风格样本数量相对均衡）
        
        Args:
            samples: 原始样本列表
        
        Returns:
            平衡后的样本列表
        """
        # 统计各风格的数量
        style_counts = Counter(s['style'] for s in samples)
        
        if not style_counts:
            return samples
        
        # 计算目标数量（使用中位数）
        target_count = sorted(style_counts.values())[len(style_counts) // 2]
        
        balanced_samples = []
        
        for style, count in style_counts.items():
            style_samples = [s for s in samples if s['style'] == style]
            
            if count < target_count:
                # 如果样本不足，通过增强补充
                needed = target_count - count
                for _ in range(needed):
                    if style_samples:
                        sample = random.choice(style_samples)
                        # 生成变体
                        orig_var, rew_var = cls.generate_variations(
                            sample['original'], 
                            sample['rewritten'], 
                            count=1
                        )[0]
                        balanced_samples.append({
                            **sample,
                            'original': orig_var,
                            'rewritten': rew_var
                        })
            
            # 添加原始样本（不超过目标数量）
            balanced_samples.extend(style_samples[:target_count])
        
        # 打乱顺序
        random.shuffle(balanced_samples)
        
        return balanced_samples

