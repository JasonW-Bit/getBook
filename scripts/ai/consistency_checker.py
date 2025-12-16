#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
逻辑一致性检查器
用于检查改写和生成的内容是否保持逻辑一致性
"""

import re
from typing import Dict, List, Tuple, Set, Optional
from collections import defaultdict, Counter


class ConsistencyChecker:
    """逻辑一致性检查器（增强版，支持可配置严格程度）"""
    
    def __init__(self, strictness: float = 0.7):
        """
        初始化一致性检查器
        
        Args:
            strictness: 严格程度（0.0-1.0），越高越严格
        """
        self.strictness = max(0.0, min(1.0, strictness))
        self.characters = {}  # 人物信息字典
        self.plot_points = []  # 情节关键点
        self.settings = {}  # 设定信息
        self.timeline = []  # 时间线
        
        # 根据严格程度设置阈值
        self.character_threshold = 0.3 + 0.4 * self.strictness  # 0.3-0.7
        self.plot_threshold = 0.4 + 0.4 * self.strictness  # 0.4-0.8
        self.setting_threshold = 0.5 + 0.4 * self.strictness  # 0.5-0.9
    
    def analyze_novel(self, content: str) -> Dict:
        """
        分析整本小说，提取关键信息
        
        Args:
            content: 小说内容
        
        Returns:
            分析结果字典
        """
        # 提取人物信息
        self.characters = self._extract_characters(content)
        
        # 提取情节关键点
        self.plot_points = self._extract_plot_points(content)
        
        # 提取设定信息
        self.settings = self._extract_settings(content)
        
        # 提取时间线
        self.timeline = self._extract_timeline(content)
        
        return {
            'characters': self.characters,
            'plot_points': self.plot_points,
            'settings': self.settings,
            'timeline': self.timeline
        }
    
    def check_consistency(self, 
                         original_text: str,
                         rewritten_text: str,
                         context: Optional[Dict] = None) -> Tuple[bool, List[str]]:
        """
        检查改写文本的逻辑一致性
        
        Args:
            original_text: 原始文本
            rewritten_text: 改写文本
            context: 上下文信息（可选）
        
        Returns:
            (是否一致, 问题列表)
        """
        issues = []
        
        # 检查人物一致性
        char_issues = self._check_character_consistency(original_text, rewritten_text)
        issues.extend(char_issues)
        
        # 检查情节一致性
        plot_issues = self._check_plot_consistency(original_text, rewritten_text)
        issues.extend(plot_issues)
        
        # 检查设定一致性
        setting_issues = self._check_setting_consistency(original_text, rewritten_text)
        issues.extend(setting_issues)
        
        # 检查时间线一致性
        timeline_issues = self._check_timeline_consistency(original_text, rewritten_text)
        issues.extend(timeline_issues)
        
        # 检查前后文连贯性
        coherence_issues = self._check_coherence(rewritten_text, context)
        issues.extend(coherence_issues)
        
        return len(issues) == 0, issues
    
    def _extract_characters(self, content: str) -> Dict[str, Dict]:
        """提取人物信息"""
        characters = {}
        
        # 提取可能的姓名（2-3个中文字符）
        name_pattern = r'([\u4e00-\u9fa5]{2,3})(?:说|道|想|看|走|来|去|是|有|在)'
        matches = re.finditer(name_pattern, content[:20000])  # 分析前20000字符
        
        name_counter = Counter()
        for match in matches:
            name = match.group(1)
            # 排除常见词
            if name not in ['大家', '自己', '他们', '我们', '你们', '她们', '它们']:
                name_counter[name] += 1
        
        # 获取主要人物（出现5次以上）
        for name, count in name_counter.most_common(20):
            if count >= 5:
                characters[name] = {
                    'name': name,
                    'count': count,
                    'first_appearance': content.find(name),
                    'attributes': self._extract_character_attributes(content, name)
                }
        
        return characters
    
    def _extract_character_attributes(self, content: str, name: str) -> Dict:
        """提取人物属性"""
        attributes = {
            'gender': None,
            'age': None,
            'role': None,
            'relationships': []
        }
        
        # 查找包含该人物的句子
        pattern = rf'{name}[^。！？]*[。！？]'
        sentences = re.findall(pattern, content[:10000])
        
        # 分析性别
        for sent in sentences[:10]:
            if '他' in sent or '男' in sent:
                attributes['gender'] = 'male'
                break
            elif '她' in sent or '女' in sent:
                attributes['gender'] = 'female'
                break
        
        # 分析角色（主角/配角）
        if len(sentences) > 20:
            attributes['role'] = '主角'
        elif len(sentences) > 5:
            attributes['role'] = '配角'
        else:
            attributes['role'] = '次要角色'
        
        return attributes
    
    def _extract_plot_points(self, content: str) -> List[Dict]:
        """提取情节关键点"""
        plot_points = []
        
        # 查找关键情节标记
        key_patterns = [
            r'(突然|忽然|终于|最后|然后|接着|但是|然而)[^。！？]{10,50}[。！？]',
            r'(发现|知道|明白|决定|开始|结束)[^。！？]{10,50}[。！？]',
        ]
        
        for pattern in key_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                plot_points.append({
                    'text': match.group(0),
                    'position': match.start(),
                    'type': '转折' if any(kw in match.group(0) for kw in ['突然', '忽然', '但是', '然而']) else '发展'
                })
        
        return plot_points[:50]  # 最多50个关键点
    
    def _extract_settings(self, content: str) -> Dict:
        """提取设定信息"""
        settings = {
            'time': None,
            'place': None,
            'world': None
        }
        
        # 提取时间设定
        time_patterns = [
            r'(古代|现代|未来|过去|现在|今天|明天|昨天)',
            r'(\d+年|\d+月|\d+日)',
        ]
        for pattern in time_patterns:
            match = re.search(pattern, content[:5000])
            if match:
                settings['time'] = match.group(0)
                break
        
        # 提取地点设定
        place_patterns = [
            r'(都市|城市|乡村|小镇|学校|公司|医院|咖啡厅|餐厅)',
        ]
        for pattern in place_patterns:
            match = re.search(pattern, content[:5000])
            if match:
                settings['place'] = match.group(0)
                break
        
        return settings
    
    def _extract_timeline(self, content: str) -> List[Dict]:
        """提取时间线"""
        timeline = []
        
        # 查找时间标记
        time_patterns = [
            r'(第\d+天|第\d+章|第\d+次|后来|然后|接着|之后|之前)',
        ]
        
        for pattern in time_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                timeline.append({
                    'marker': match.group(0),
                    'position': match.start()
                })
        
        return timeline[:100]  # 最多100个时间点
    
    def _check_character_consistency(self, original: str, rewritten: str) -> List[str]:
        """检查人物一致性"""
        issues = []
        
        # 提取原始文本中的人物
        orig_chars = set(re.findall(r'([\u4e00-\u9fa5]{2,3})(?:说|道|想)', original))
        rew_chars = set(re.findall(r'([\u4e00-\u9fa5]{2,3})(?:说|道|想)', rewritten))
        
        # 检查主要人物是否一致
        if self.characters:
            main_chars = set(self.characters.keys())
            orig_main = orig_chars & main_chars
            rew_main = rew_chars & main_chars
            
            # 如果主要人物消失，可能是问题（基于严格程度）
            if orig_main:
                missing_ratio = len(orig_main - rew_main) / len(orig_main)
                if missing_ratio > self.character_threshold:
                    missing = orig_main - rew_main
                    issues.append(f"主要人物缺失: {', '.join(missing)} (缺失率: {missing_ratio*100:.1f}%)")
            
            # 如果出现新人物，需要检查
            new_chars = rew_chars - orig_chars
            if new_chars and len(new_chars) > 2:
                issues.append(f"出现新人物: {', '.join(new_chars)}")
        
        return issues
    
    def _check_plot_consistency(self, original: str, rewritten: str) -> List[str]:
        """检查情节一致性"""
        issues = []
        
        # 检查关键情节是否保留
        key_events = ['发现', '知道', '决定', '开始', '结束', '突然', '终于']
        
        orig_events = [kw for kw in key_events if kw in original]
        rew_events = [kw for kw in key_events if kw in rewritten]
        
        # 如果关键事件消失太多，可能是问题（基于严格程度）
        if len(orig_events) > 0:
            missing_ratio = 1 - len(rew_events) / len(orig_events)
            if missing_ratio > self.plot_threshold:
                issues.append(f"关键情节丢失过多: {missing_ratio*100:.1f}% (阈值: {self.plot_threshold*100:.1f}%)")
        
        return issues
    
    def _check_setting_consistency(self, original: str, rewritten: str) -> List[str]:
        """检查设定一致性"""
        issues = []
        
        # 检查时间设定
        if self.settings.get('time'):
            if self.settings['time'] in original and self.settings['time'] not in rewritten:
                issues.append(f"时间设定丢失: {self.settings['time']}")
        
        # 检查地点设定
        if self.settings.get('place'):
            if self.settings['place'] in original and self.settings['place'] not in rewritten:
                issues.append(f"地点设定丢失: {self.settings['place']}")
        
        return issues
    
    def _check_timeline_consistency(self, original: str, rewritten: str) -> List[str]:
        """检查时间线一致性"""
        issues = []
        
        # 检查时间标记的顺序
        orig_times = re.findall(r'(第\d+天|第\d+章|后来|然后|接着)', original)
        rew_times = re.findall(r'(第\d+天|第\d+章|后来|然后|接着)', rewritten)
        
        # 如果时间标记顺序改变，可能是问题
        if len(orig_times) > 0 and len(rew_times) > 0:
            if orig_times[0] != rew_times[0]:
                issues.append("时间线顺序可能改变")
        
        return issues
    
    def _check_coherence(self, text: str, context: Optional[Dict] = None) -> List[str]:
        """检查前后文连贯性"""
        issues = []
        
        if not context:
            return issues
        
        # 检查人物提及是否与上下文一致
        if 'characters' in context:
            mentioned_chars = set(re.findall(r'([\u4e00-\u9fa5]{2,3})(?:说|道|想)', text))
            context_chars = set(context.get('characters', []))
            
            # 如果出现上下文中没有的人物，可能是问题
            new_chars = mentioned_chars - context_chars
            if new_chars and len(new_chars) > 1:
                issues.append(f"出现上下文中未提及的人物: {', '.join(new_chars)}")
        
        return issues
    
    def validate_rewritten_novel(self, 
                                 original_chapters: List[str],
                                 rewritten_chapters: List[str]) -> Dict:
        """
        验证整本改写小说的逻辑一致性
        
        Args:
            original_chapters: 原始章节列表
            rewritten_chapters: 改写章节列表
        
        Returns:
            验证结果字典
        """
        results = {
            'total_chapters': len(rewritten_chapters),
            'consistent_chapters': 0,
            'issues': [],
            'character_consistency': {},
            'plot_consistency': {},
        }
        
        # 分析原始小说
        full_original = '\n\n'.join(original_chapters)
        self.analyze_novel(full_original)
        
        # 检查每个章节
        for i, (orig_ch, rew_ch) in enumerate(zip(original_chapters, rewritten_chapters)):
            is_consistent, issues = self.check_consistency(orig_ch, rew_ch)
            
            if is_consistent:
                results['consistent_chapters'] += 1
            else:
                results['issues'].append({
                    'chapter': i + 1,
                    'issues': issues
                })
        
        # 检查整本书的人物一致性
        full_rewritten = '\n\n'.join(rewritten_chapters)
        rew_characters = self._extract_characters(full_rewritten)
        
        # 比较人物
        orig_char_names = set(self.characters.keys())
        rew_char_names = set(rew_characters.keys())
        
        results['character_consistency'] = {
            'original_count': len(orig_char_names),
            'rewritten_count': len(rew_char_names),
            'missing': list(orig_char_names - rew_char_names),
            'new': list(rew_char_names - orig_char_names),
            'consistent': list(orig_char_names & rew_char_names)
        }
        
        return results

