#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上下文管理器
管理整本小说的上下文信息，确保改写和生成时保持逻辑一致性
"""

import re
from typing import Dict, List, Optional, Set
from collections import defaultdict, Counter


class NovelContextManager:
    """小说上下文管理器"""
    
    def __init__(self):
        self.characters = {}  # 人物信息 {name: {attributes, relationships, etc.}}
        self.plot_summary = []  # 情节摘要
        self.settings = {}  # 设定信息
        self.timeline = []  # 时间线
        self.key_events = []  # 关键事件
        self.chapter_summaries = []  # 章节摘要
    
    def build_context(self, novel_content: str, chapters: Optional[List[str]] = None) -> Dict:
        """
        构建整本小说的上下文
        
        Args:
            novel_content: 小说完整内容
            chapters: 章节列表（可选）
        
        Returns:
            上下文信息字典
        """
        print("📚 构建小说上下文...")
        
        # 提取人物信息
        self.characters = self._extract_characters(novel_content)
        print(f"   识别到 {len(self.characters)} 个主要人物")
        
        # 构建人物关系图谱（如果可用）
        try:
            from .relationship_graph import RelationshipGraph
            graph_builder = RelationshipGraph()
            character_names = list(self.characters.keys())
            if character_names:
                self.relationship_graph = graph_builder.build_graph(novel_content, character_names)
                print(f"   构建了人物关系图谱（{len(self.relationship_graph.get('edges', []))} 条关系）")
            else:
                self.relationship_graph = None
        except ImportError:
            self.relationship_graph = None
        except Exception as e:
            print(f"   ⚠️  关系图谱构建失败: {e}")
            self.relationship_graph = None
        
        # 提取情节摘要
        self.plot_summary = self._extract_plot_summary(novel_content)
        print(f"   提取到 {len(self.plot_summary)} 个情节要点")
        
        # 提取设定信息
        self.settings = self._extract_settings(novel_content)
        
        # 提取时间线
        self.timeline = self._extract_timeline(novel_content)
        
        # 提取关键事件
        self.key_events = self._extract_key_events(novel_content)
        
        # 如果提供了章节列表，提取章节摘要
        if chapters:
            self.chapter_summaries = self._extract_chapter_summaries(chapters)
        
        return {
            'characters': self.characters,
            'plot_summary': self.plot_summary,
            'settings': self.settings,
            'timeline': self.timeline,
            'key_events': self.key_events,
            'chapter_summaries': self.chapter_summaries
        }
    
    def get_context_for_rewrite(self, 
                                current_text: str,
                                position: int = 0,
                                chapter_num: int = 0) -> str:
        """
        获取用于改写的上下文信息
        
        Args:
            current_text: 当前要改写的文本
            position: 在整本小说中的位置
            chapter_num: 章节号
        
        Returns:
            上下文信息字符串
        """
        context_parts = []
        
        # 添加主要人物信息
        if self.characters:
            main_chars = list(self.characters.keys())[:5]
            context_parts.append(f"主要人物: {', '.join(main_chars)}")
        
        # 添加当前章节的相关人物
        current_chars = self._extract_characters_from_text(current_text)
        if current_chars:
            context_parts.append(f"当前人物: {', '.join(list(current_chars)[:3])}")
        
        # 添加前文情节摘要
        if chapter_num > 0 and self.chapter_summaries:
            prev_summaries = self.chapter_summaries[max(0, chapter_num-3):chapter_num]
            if prev_summaries:
                context_parts.append(f"前文摘要: {'; '.join(prev_summaries[:2])}")
        
        # 添加设定信息
        if self.settings:
            setting_info = []
            if self.settings.get('time'):
                setting_info.append(f"时间: {self.settings['time']}")
            if self.settings.get('place'):
                setting_info.append(f"地点: {self.settings['place']}")
            if setting_info:
                context_parts.append(' | '.join(setting_info))
        
        # 添加相关情节要点
        relevant_plots = self._get_relevant_plots(current_text)
        if relevant_plots:
            context_parts.append(f"相关情节: {'; '.join(relevant_plots[:2])}")
        
        return " | ".join(context_parts)
    
    def validate_rewrite(self, 
                        original: str,
                        rewritten: str,
                        context: Optional[str] = None) -> Tuple[bool, List[str]]:
        """
        验证改写是否保持逻辑一致性
        
        Args:
            original: 原始文本
            rewritten: 改写文本
            context: 上下文信息
        
        Returns:
            (是否一致, 问题列表)
        """
        issues = []
        
        # 检查人物一致性
        orig_chars = self._extract_characters_from_text(original)
        rew_chars = self._extract_characters_from_text(rewritten)
        
        # 检查主要人物是否保留
        main_chars_in_orig = orig_chars & set(self.characters.keys())
        main_chars_in_rew = rew_chars & set(self.characters.keys())
        
        missing = main_chars_in_orig - main_chars_in_rew
        if missing:
            issues.append(f"主要人物缺失: {', '.join(missing)}")
        
        # 检查关键事件是否保留
        key_events_in_orig = [ev for ev in self.key_events if ev in original]
        key_events_in_rew = [ev for ev in self.key_events if ev in rewritten]
        
        if len(key_events_in_orig) > 0:
            missing_events = set(key_events_in_orig) - set(key_events_in_rew)
            if missing_events:
                issues.append(f"关键事件缺失: {len(missing_events)}个")
        
        return len(issues) == 0, issues
    
    def _extract_characters(self, content: str) -> Dict[str, Dict]:
        """提取人物信息（增强版，支持NER风格提取）"""
        characters = {}
        
        # 方法1: 查找"XX说"、"XX道"等模式（改进版，更精确）
        speech_pattern = r'([\u4e00-\u9fa5]{2,3})(?:说|道|问|答|喊|叫|想|看|听|走|来|去|是|有|在|笑|哭|怒|喜)(?=[，。！？：；\s]|$)'
        matches = re.finditer(speech_pattern, content[:50000])  # 分析前50000字符
        
        name_counter = Counter()
        name_positions = defaultdict(list)
        
        for match in matches:
            name = match.group(1)
            # 排除常见词
            exclude_words = {
                '大家', '自己', '他们', '我们', '你们', '她们', '它们',
                '什么', '怎么', '这样', '那样', '这个', '那个',
                '今天', '明天', '昨天', '现在', '以后', '之前', '之后',
            }
            if name not in exclude_words:
                name_counter[name] += 1
                name_positions[name].append(match.start())
        
        # 获取主要人物（出现10次以上，且分布在不同位置）
        for name, count in name_counter.most_common(30):
            if count >= 10:
                positions = name_positions[name]
                # 检查分布（如果都在前1000字符，可能是误识别）
                if len(positions) > 5 and max(positions) - min(positions) > 1000:
                    characters[name] = {
                        'name': name,
                        'count': count,
                        'first_appearance': min(positions),
                        'last_appearance': max(positions),
                        'distribution': len(set(p // 5000 for p in positions)),  # 分布在多少个5000字符块中
                        'attributes': self._extract_character_attributes(content, name)
                    }
        
        return characters
    
    def _extract_character_attributes(self, content: str, name: str) -> Dict:
        """提取人物属性（增强版）"""
        attributes = {
            'gender': None,
            'age': None,
            'role': None,
            'relationships': [],
            'description': ''
        }
        
        # 查找包含该人物的句子
        pattern = rf'{name}[^。！？]{0,50}[。！？]'
        sentences = re.findall(pattern, content[:20000])
        
        if not sentences:
            return attributes
        
        # 分析性别
        for sent in sentences[:20]:
            if '他' in sent or '男' in sent or '先生' in sent:
                attributes['gender'] = 'male'
                break
            elif '她' in sent or '女' in sent or '小姐' in sent or '女士' in sent:
                attributes['gender'] = 'female'
                break
        
        # 分析角色（基于出现频率和分布）
        if len(sentences) > 50:
            attributes['role'] = '主角'
        elif len(sentences) > 15:
            attributes['role'] = '重要配角'
        elif len(sentences) > 5:
            attributes['role'] = '配角'
        else:
            attributes['role'] = '次要角色'
        
        # 提取描述（前几个包含该人物的句子）
        if sentences:
            attributes['description'] = ' '.join(sentences[:3])
        
        return attributes
    
    def _extract_plot_summary(self, content: str) -> List[str]:
        """提取情节摘要"""
        plot_points = []
        
        # 查找关键情节标记
        key_patterns = [
            r'(突然|忽然|终于|最后|然后|接着|但是|然而)[^。！？]{10,100}[。！？]',
            r'(发现|知道|明白|决定|开始|结束|完成)[^。！？]{10,100}[。！？]',
            r'(重要|关键|转折|变化)[^。！？]{10,100}[。！？]',
        ]
        
        for pattern in key_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                plot_text = match.group(0).strip()
                if len(plot_text) > 20 and len(plot_text) < 150:  # 合理长度
                    plot_points.append(plot_text)
                    if len(plot_points) >= 50:
                        break
            if len(plot_points) >= 50:
                break
        
        return plot_points
    
    def _extract_settings(self, content: str) -> Dict:
        """提取设定信息（增强版）"""
        settings = {
            'time': None,
            'place': None,
            'world': None,
            'genre': None
        }
        
        # 提取时间设定
        time_patterns = [
            r'(古代|现代|未来|过去|现在|当代|近代|古代)',
            r'(\d{4}年|\d+世纪)',
            r'(今天|明天|昨天|现在|将来|过去)',
        ]
        for pattern in time_patterns:
            match = re.search(pattern, content[:10000])
            if match:
                settings['time'] = match.group(0)
                break
        
        # 提取地点设定
        place_patterns = [
            r'(都市|城市|乡村|小镇|学校|公司|医院|咖啡厅|餐厅|办公室|家里|家中)',
            r'(北京|上海|广州|深圳|杭州|成都|武汉|西安|南京|重庆)',
        ]
        for pattern in place_patterns:
            match = re.search(pattern, content[:10000])
            if match:
                settings['place'] = match.group(0)
                break
        
        # 提取世界观设定
        world_patterns = [
            r'(玄幻|武侠|科幻|都市|言情|历史|军事|游戏|竞技|仙侠)',
        ]
        for pattern in world_patterns:
            match = re.search(pattern, content[:5000])
            if match:
                settings['world'] = match.group(0)
                settings['genre'] = match.group(0)
                break
        
        return settings
    
    def _extract_timeline(self, content: str) -> List[Dict]:
        """提取时间线（增强版）"""
        timeline = []
        
        # 查找时间标记
        time_patterns = [
            r'(第\d+天|第\d+章|第\d+次|后来|然后|接着|之后|之前|第二天|第三天)',
            r'(早上|中午|下午|晚上|深夜|凌晨)',
            r'(\d+月\d+日|\d+年\d+月)',
        ]
        
        for pattern in time_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                timeline.append({
                    'marker': match.group(0),
                    'position': match.start(),
                    'type': '时间标记'
                })
                if len(timeline) >= 200:
                    break
            if len(timeline) >= 200:
                break
        
        return timeline
    
    def _extract_key_events(self, content: str) -> List[str]:
        """提取关键事件"""
        events = []
        
        # 查找关键事件标记
        event_patterns = [
            r'(发生|出现|遇到|遇到|发现|知道|决定|开始|结束|完成)[^。！？]{10,80}[。！？]',
            r'(重要|关键|转折|变化|突然|忽然)[^。！？]{10,80}[。！？]',
        ]
        
        for pattern in event_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                event_text = match.group(0).strip()
                if 20 < len(event_text) < 120:
                    events.append(event_text)
                    if len(events) >= 100:
                        break
            if len(events) >= 100:
                break
        
        return events
    
    def _extract_chapter_summaries(self, chapters: List[str]) -> List[str]:
        """提取章节摘要"""
        summaries = []
        
        for chapter in chapters:
            # 提取章节的关键信息（前200字符 + 关键句）
            summary = chapter[:200] if len(chapter) > 200 else chapter
            
            # 查找关键句
            key_sentences = re.findall(r'[^。！？]*(重要|关键|突然|终于|决定|发现)[^。！？]*[。！？]', chapter)
            if key_sentences:
                summary += " | " + key_sentences[0]
            
            summaries.append(summary[:300])  # 限制长度
        
        return summaries
    
    def _extract_characters_from_text(self, text: str) -> Set[str]:
        """从文本中提取人物"""
        pattern = r'([\u4e00-\u9fa5]{2,3})(?:说|道|想|看|走|来|去)'
        matches = re.findall(pattern, text)
        return set(matches)
    
    def _get_relevant_plots(self, text: str) -> List[str]:
        """获取相关的情节要点"""
        relevant = []
        
        # 查找文本中的关键词
        keywords = re.findall(r'[\u4e00-\u9fa5]{2,4}', text[:500])
        keyword_set = set(keywords)
        
        # 匹配情节要点
        for plot in self.plot_summary:
            plot_keywords = set(re.findall(r'[\u4e00-\u9fa5]{2,4}', plot))
            # 如果有共同关键词，认为是相关的
            if keyword_set & plot_keywords:
                relevant.append(plot)
                if len(relevant) >= 3:
                    break
        
        return relevant

