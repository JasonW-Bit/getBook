#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动修复模块
检测到逻辑一致性问题后，自动修复或提供修复建议
"""

import re
from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict


class AutoFixer:
    """自动修复器"""
    
    def __init__(self, context_manager=None):
        """
        初始化自动修复器
        
        Args:
            context_manager: 上下文管理器（可选）
        """
        self.context_manager = context_manager
    
    def fix_character_consistency(self, 
                                 original: str,
                                 rewritten: str,
                                 missing_characters: Set[str],
                                 context: Optional[Dict] = None) -> str:
        """
        修复人物一致性问题
        
        Args:
            original: 原始文本
            rewritten: 改写文本
            missing_characters: 缺失的人物集合
            context: 上下文信息
        
        Returns:
            修复后的文本
        """
        if not missing_characters:
            return rewritten
        
        fixed_text = rewritten
        
        # 在原始文本中查找这些人物出现的上下文
        for char in missing_characters:
            # 查找人物在原文中的出现位置
            pattern = rf'{char}[^。！？]*[。！？]'
            matches = list(re.finditer(pattern, original))
            
            if matches:
                # 获取第一个匹配的上下文
                match = matches[0]
                context_sentence = match.group(0)
                
                # 检查改写文本中是否缺少这个人物
                if char not in fixed_text:
                    # 尝试在合适的位置插入
                    # 查找相似的句子结构
                    sentences = re.split(r'[。！？]', fixed_text)
                    for i, sent in enumerate(sentences):
                        # 如果句子结构相似，尝试插入人物
                        if len(sent) > 10 and len(sent) < 100:
                            # 在句子开头插入人物
                            fixed_sentence = f"{char}{sent}"
                            sentences[i] = fixed_sentence
                            break
                    
                    fixed_text = '。'.join(sentences) + '。'
        
        return fixed_text
    
    def fix_plot_consistency(self,
                            original: str,
                            rewritten: str,
                            missing_events: List[str],
                            context: Optional[Dict] = None) -> str:
        """
        修复情节一致性问题
        
        Args:
            original: 原始文本
            rewritten: 改写文本
            missing_events: 缺失的关键事件列表
            context: 上下文信息
        
        Returns:
            修复后的文本
        """
        if not missing_events:
            return rewritten
        
        fixed_text = rewritten
        
        # 对于每个缺失的事件，尝试在改写文本中找到合适的位置插入
        for event_keyword in missing_events[:3]:  # 最多修复3个
            # 在原文中查找包含该关键词的句子
            pattern = rf'[^。！？]*{re.escape(event_keyword)}[^。！？]*[。！？]'
            matches = list(re.finditer(pattern, original))
            
            if matches:
                event_sentence = matches[0].group(0)
                
                # 检查改写文本中是否缺少这个事件
                if event_keyword not in fixed_text:
                    # 在改写文本的适当位置插入
                    # 查找段落结尾
                    paragraphs = re.split(r'\n\s*\n', fixed_text)
                    if paragraphs:
                        # 在最后一个段落末尾添加
                        paragraphs[-1] += f"\n\n{event_sentence}"
                        fixed_text = '\n\n'.join(paragraphs)
        
        return fixed_text
    
    def fix_setting_consistency(self,
                               original: str,
                               rewritten: str,
                               missing_settings: Dict,
                               context: Optional[Dict] = None) -> str:
        """
        修复设定一致性问题
        
        Args:
            original: 原始文本
            rewritten: 改写文本
            missing_settings: 缺失的设定字典
            context: 上下文信息
        
        Returns:
            修复后的文本
        """
        if not missing_settings:
            return rewritten
        
        fixed_text = rewritten
        
        # 修复时间设定
        if 'time' in missing_settings and missing_settings['time']:
            time_value = missing_settings['time']
            if time_value not in fixed_text:
                # 在开头添加时间设定
                fixed_text = f"【{time_value}】\n\n{fixed_text}"
        
        # 修复地点设定
        if 'place' in missing_settings and missing_settings['place']:
            place_value = missing_settings['place']
            if place_value not in fixed_text:
                # 在开头添加地点设定
                if fixed_text.startswith('【'):
                    fixed_text = fixed_text.replace('【', f"【{place_value}，", 1)
                else:
                    fixed_text = f"【{place_value}】\n\n{fixed_text}"
        
        return fixed_text
    
    def auto_fix(self,
                original: str,
                rewritten: str,
                issues: List[str],
                context: Optional[Dict] = None) -> Tuple[str, List[str]]:
        """
        自动修复所有检测到的问题
        
        Args:
            original: 原始文本
            rewritten: 改写文本
            issues: 问题列表
            context: 上下文信息
        
        Returns:
            (修复后的文本, 修复报告列表)
        """
        fixed_text = rewritten
        fix_report = []
        
        # 解析问题
        missing_chars = set()
        missing_events = []
        missing_settings = {}
        
        for issue in issues:
            if '主要人物缺失' in issue:
                # 提取缺失的人物
                match = re.search(r'主要人物缺失: ([^（]+)', issue)
                if match:
                    chars_str = match.group(1)
                    missing_chars.update([c.strip() for c in chars_str.split(',')])
            elif '关键情节丢失' in issue:
                # 提取缺失的事件关键词
                missing_events.append('关键')
            elif '时间设定丢失' in issue:
                match = re.search(r'时间设定丢失: (.+)', issue)
                if match:
                    missing_settings['time'] = match.group(1)
            elif '地点设定丢失' in issue:
                match = re.search(r'地点设定丢失: (.+)', issue)
                if match:
                    missing_settings['place'] = match.group(1)
        
        # 修复人物一致性问题
        if missing_chars:
            fixed_text = self.fix_character_consistency(
                original, fixed_text, missing_chars, context
            )
            fix_report.append(f"修复了 {len(missing_chars)} 个人物一致性问题")
        
        # 修复情节一致性问题
        if missing_events:
            fixed_text = self.fix_plot_consistency(
                original, fixed_text, missing_events, context
            )
            fix_report.append(f"修复了 {len(missing_events)} 个情节一致性问题")
        
        # 修复设定一致性问题
        if missing_settings:
            fixed_text = self.fix_setting_consistency(
                original, fixed_text, missing_settings, context
            )
            fix_report.append(f"修复了 {len(missing_settings)} 个设定一致性问题")
        
        return fixed_text, fix_report
    
    def suggest_fixes(self,
                     issues: List[str],
                     context: Optional[Dict] = None) -> List[str]:
        """
        提供修复建议（不实际修复）
        
        Args:
            issues: 问题列表
            context: 上下文信息
        
        Returns:
            修复建议列表
        """
        suggestions = []
        
        for issue in issues:
            if '主要人物缺失' in issue:
                suggestions.append(f"建议：在改写文本中保留原文中出现的主要人物")
            elif '关键情节丢失' in issue:
                suggestions.append(f"建议：保留原文中的关键情节和转折点")
            elif '时间设定丢失' in issue:
                suggestions.append(f"建议：在改写文本中保留时间设定信息")
            elif '地点设定丢失' in issue:
                suggestions.append(f"建议：在改写文本中保留地点设定信息")
            elif '时间线顺序' in issue:
                suggestions.append(f"建议：保持时间线的逻辑顺序")
        
        return suggestions

