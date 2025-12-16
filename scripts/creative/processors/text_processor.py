#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能文本处理器
提供更自然、流畅的文本改写功能
"""

import re
from typing import List, Tuple, Dict
from collections import defaultdict


class ContextualTextProcessor:
    """基于上下文的文本处理器"""
    
    def __init__(self):
        self.sentence_pattern = re.compile(r'[^。！？]+[。！？]')
        self.dialogue_pattern = re.compile(r'["""](.*?)["""]')
    
    def split_into_sentences(self, text: str) -> List[str]:
        """将文本分割成句子"""
        sentences = []
        for match in self.sentence_pattern.finditer(text):
            sentences.append(match.group(0))
        return sentences
    
    def extract_context(self, text: str, position: int, window: int = 100) -> str:
        """提取上下文"""
        start = max(0, position - window)
        end = min(len(text), position + window)
        return text[start:end]
    
    def analyze_sentence_type(self, sentence: str) -> str:
        """分析句子类型"""
        if self.dialogue_pattern.search(sentence):
            return 'dialogue'
        elif re.search(r'[想思]', sentence):
            return 'thought'
        elif re.search(r'[看观察]', sentence):
            return 'observation'
        elif re.search(r'[走跑来去]', sentence):
            return 'action'
        else:
            return 'narration'
    
    def should_apply_style(self, sentence: str, style: str, context: str) -> bool:
        """判断是否应该应用风格（基于上下文）"""
        # 避免在重要对话中过度修改
        if self.dialogue_pattern.search(sentence):
            return False
        
        # 避免在关键情节中过度修改
        if any(keyword in context for keyword in ['重要', '关键', '突然', '终于']):
            return False
        
        return True


class NaturalStyleRewriter:
    """自然风格改写器"""
    
    def __init__(self):
        self.processor = ContextualTextProcessor()
        self.style_rules = self._init_style_rules()
    
    def _init_style_rules(self) -> Dict:
        """初始化风格规则"""
        return {
            '都市': {
                'keywords': ['都市', '城市', '街道', '咖啡厅', '霓虹灯', '繁华'],
                'replacements': {
                    '城市': '都市',
                    '地方': '都市',
                },
                'additions': {
                    'dialogue': lambda s: self._add_urban_dialogue_context(s),
                    'action': lambda s: self._add_urban_action_context(s),
                },
                'frequency': 0.08  # 8%的概率添加都市元素
            },
            '幽默': {
                'keywords': ['有趣', '好笑', '幽默', '轻松'],
                'replacements': {
                    '很': '超级',
                    '非常': '超级',
                    '好': '棒极了',
                },
                'additions': {
                    'dialogue': lambda s: self._add_humor_to_dialogue(s),
                    'narration': lambda s: self._add_humor_to_narration(s),
                },
                'frequency': 0.12  # 12%的概率添加幽默元素
            },
            '都市幽默': {
                'keywords': ['都市', '幽默', '有趣', '繁华'],
                'replacements': {
                    '城市': '都市',
                    '很': '超级',
                    '非常': '超级',
                },
                'additions': {
                    'dialogue': lambda s: self._add_urban_humor_dialogue(s),
                    'action': lambda s: self._add_urban_humor_action(s),
                },
                'frequency': 0.10
            }
        }
    
    def _add_urban_dialogue_context(self, sentence: str) -> str:
        """为对话添加都市语境"""
        # 只在适当的地方添加，不要过度
        if '说' in sentence or '道' in sentence:
            # 检查是否已经有场景描述
            if '咖啡厅' not in sentence and '都市' not in sentence:
                if random.random() < 0.1:  # 10%的概率
                    sentence = sentence.replace('说', '在都市的咖啡厅里说', 1)
                    sentence = sentence.replace('道', '在都市的咖啡厅里道', 1)
        return sentence
    
    def _add_urban_action_context(self, sentence: str) -> str:
        """为动作添加都市语境"""
        if '走' in sentence or '来' in sentence or '去' in sentence:
            if '都市' not in sentence and '街道' not in sentence:
                if random.random() < 0.05:  # 5%的概率
                    sentence = sentence.replace('走', '穿梭在都市街道上走', 1)
        return sentence
    
    def _add_humor_to_dialogue(self, sentence: str) -> str:
        """为对话添加幽默元素"""
        # 在对话后适度添加幽默
        if '"' in sentence:
            if '哈哈' not in sentence and '有趣' not in sentence:
                if random.random() < 0.15:  # 15%的概率
                    sentence = re.sub(r'(".*?")([，。！？])', r'\1，哈哈\2', sentence, count=1)
        return sentence
    
    def _add_humor_to_narration(self, sentence: str) -> str:
        """为叙述添加幽默元素"""
        # 适度添加轻松幽默的词汇
        if len(sentence) > 30 and '有趣' not in sentence:
            if random.random() < 0.05:  # 5%的概率
                # 在句末添加，但要自然
                if sentence.endswith('。') or sentence.endswith('！'):
                    sentence = sentence[:-1] + '，有趣的是。'
        return sentence
    
    def _add_urban_humor_dialogue(self, sentence: str) -> str:
        """为对话添加都市+幽默元素"""
        sentence = self._add_urban_dialogue_context(sentence)
        sentence = self._add_humor_to_dialogue(sentence)
        return sentence
    
    def _add_urban_humor_action(self, sentence: str) -> str:
        """为动作添加都市+幽默元素"""
        sentence = self._add_urban_action_context(sentence)
        return sentence
    
    def rewrite_naturally(self, text: str, style: str) -> str:
        """自然流畅地改写文本"""
        if style not in self.style_rules:
            return text
        
        rules = self.style_rules[style]
        sentences = self.processor.split_into_sentences(text)
        rewritten_sentences = []
        
        for i, sentence in enumerate(sentences):
            # 分析句子类型
            sentence_type = self.processor.analyze_sentence_type(sentence)
            
            # 提取上下文
            position = sum(len(s) for s in sentences[:i])
            context = self.processor.extract_context(text, position)
            
            # 判断是否应该应用风格
            if not self.processor.should_apply_style(sentence, style, context):
                rewritten_sentences.append(sentence)
                continue
            
            # 应用替换规则（适度）
            for old, new in rules.get('replacements', {}).items():
                if old in sentence:
                    # 使用单词边界，避免部分匹配
                    pattern = r'\b' + re.escape(old) + r'\b'
                    sentence = re.sub(pattern, new, sentence, count=1)  # 每次只替换一次
            
            # 根据句子类型添加风格元素（基于概率）
            if random.random() < rules['frequency']:
                additions = rules.get('additions', {})
                if sentence_type in additions:
                    sentence = additions[sentence_type](sentence)
            
            rewritten_sentences.append(sentence)
        
        return ''.join(rewritten_sentences)


# 为了兼容性，添加random导入
import random

