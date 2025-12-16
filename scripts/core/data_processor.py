#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据处理器
在爬取后立即对数据进行结构化处理，拆分成适合学习的格式
"""

import os
import re
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from .intelligent_analyzer import IntelligentAnalyzer
from .config_center import ConfigCenter


class DataProcessor:
    """数据处理器 - 将爬取的数据转换为学习数据结构"""
    
    def __init__(self, output_dir: str = "data/training"):
        """
        初始化数据处理器
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = output_dir
        self.structured_dir = os.path.join(output_dir, 'structured')
        
        # 初始化配置中心和分析器
        self.config = ConfigCenter()
        self.analyzer = IntelligentAnalyzer(config_center=self.config)
        
        os.makedirs(self.structured_dir, exist_ok=True)
    
    def process_novel(self, novel_file: str, category: str, site: str = "m.shuhaige.net") -> Optional[Dict]:
        """
        处理单本小说，转换为结构化数据
        
        Args:
            novel_file: 小说文件路径
            category: 小说类型
            site: 来源网站
        
        Returns:
            结构化数据字典
        """
        if not os.path.exists(novel_file):
            return None
        
        print(f"  📖 处理: {Path(novel_file).name}")
        
        # 读取小说内容
        with open(novel_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 1. 智能分析
        analysis = self.analyzer.analyze_novel_structure(content)
        
        # 1.5. 从分析结果中学习新关键词（自动更新配置）
        self.config.learn_from_analysis(analysis)
        
        # 2. 结构化拆分
        structured_data = self._structure_content(content, analysis, category, site)
        
        # 3. 数据验证
        if not self._validate_structured_data(structured_data):
            print(f"    ⚠️  数据验证失败，跳过")
            return None
        
        # 4. 保存结构化数据
        novel_name = Path(novel_file).stem
        output_file = os.path.join(self.structured_dir, f"{novel_name}_structured.json")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(structured_data, f, ensure_ascii=False, indent=2)
        
        print(f"    ✅ 已保存结构化数据: {len(structured_data['chapters'])} 章")
        
        return structured_data
    
    def _structure_content(self, content: str, analysis: Dict, category: str, site: str) -> Dict:
        """
        将内容拆分为结构化数据
        
        Args:
            content: 小说内容
            analysis: 分析结果
            category: 类型
            site: 来源网站
        
        Returns:
            结构化数据
        """
        # 提取基本信息
        title_match = re.search(r'标题[：:：]?\s*(.+)', content)
        author_match = re.search(r'作者[：:：]?\s*(.+)', content)
        
        title = title_match.group(1).strip() if title_match else Path(content[:100]).stem
        author = author_match.group(1).strip() if author_match else '未知'
        
        # 按章节拆分
        chapters = self._split_into_chapters(content)
        
        # 构建结构化数据
        structured_data = {
            'metadata': {
                'title': title,
                'author': author,
                'category': category,
                'site': site,
                'total_chapters': len(chapters),
                'total_chars': len(content)
            },
            'analysis': analysis,
            'chapters': []
        }
        
        # 处理每个章节
        for i, chapter_content in enumerate(chapters, 1):
            chapter_data = self._process_chapter(
                chapter_content, 
                i, 
                analysis,
                structured_data['chapters'][-1] if structured_data['chapters'] else None
            )
            
            if chapter_data:
                structured_data['chapters'].append(chapter_data)
        
        return structured_data
    
    def _split_into_chapters(self, content: str) -> List[str]:
        """将内容拆分为章节"""
        # 查找章节标记
        chapter_pattern = r'第\s*\d+\s*章[：:：]?\s*.+?\n'
        chapter_matches = list(re.finditer(chapter_pattern, content))
        
        if not chapter_matches:
            # 如果没有章节标记，按段落分割
            paragraphs = re.split(r'\n\s*\n', content)
            return [p.strip() for p in paragraphs if len(p.strip()) > 500]
        
        chapters = []
        for i, match in enumerate(chapter_matches):
            start = match.end()
            end = chapter_matches[i + 1].start() if i + 1 < len(chapter_matches) else len(content)
            chapter_content = content[start:end].strip()
            
            if len(chapter_content) > 100:  # 至少100字符
                chapters.append(chapter_content)
        
        return chapters
    
    def _process_chapter(self, chapter_content: str, chapter_num: int, 
                         novel_analysis: Dict, prev_chapter: Optional[Dict]) -> Optional[Dict]:
        """
        处理单个章节
        
        Args:
            chapter_content: 章节内容
            chapter_num: 章节号
            novel_analysis: 整本小说的分析结果
            prev_chapter: 前一章的数据（用于上下文）
        
        Returns:
            章节结构化数据
        """
        if len(chapter_content) < 200:  # 太短的章节跳过
            return None
        
        # 拆分为段落
        paragraphs = re.split(r'\n\s*\n', chapter_content)
        paragraphs = [p.strip() for p in paragraphs if len(p.strip()) > 50]
        
        # 拆分为句子
        sentences = re.split(r'[。！？]', chapter_content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        # 提取对话
        dialogues = re.findall(r'["""]([^"""]+)["""]', chapter_content)
        
        # 提取场景
        scenes = self._extract_scenes(paragraphs)
        
        # 提取情节要点
        plot_points = self._extract_plot_points(chapter_content)
        
        # 提取人物出场
        characters_in_chapter = self._extract_characters_in_chapter(chapter_content, novel_analysis.get('characters', {}))
        
        # 提取情感变化
        emotional_flow = self._extract_emotional_flow(sentences)
        
        # 构建章节数据
        chapter_data = {
            'chapter_num': chapter_num,
            'length': len(chapter_content),
            'paragraphs': paragraphs,
            'sentences': sentences[:50],  # 最多50句
            'dialogues': dialogues[:20],  # 最多20段对话
            'scenes': scenes,
            'plot_points': plot_points,
            'characters': characters_in_chapter,
            'emotional_flow': emotional_flow,
            'writing_features': {
                'dialogue_ratio': len(dialogues) / len(sentences) if sentences else 0,
                'description_ratio': self._calculate_description_ratio(chapter_content),
                'action_ratio': self._calculate_action_ratio(chapter_content)
            },
            'context': {
                'prev_summary': prev_chapter.get('plot_points', [])[-1] if prev_chapter else None,
                'characters_continuity': self._check_character_continuity(
                    characters_in_chapter,
                    prev_chapter.get('characters', {}) if prev_chapter else {}
                )
            }
        }
        
        return chapter_data
    
    def _extract_scenes(self, paragraphs: List[str]) -> List[Dict]:
        """提取场景（使用配置中心）"""
        scenes = []
        scene_keywords = set(self.config.get_scene_keywords())  # 转换为set提高查找效率
        
        for para in paragraphs:
            # 查找场景关键词
            found = False
            for keyword in scene_keywords:
                if keyword in para:
                    scenes.append({
                        'location': keyword,
                        'description': para[:100]  # 前100字符
                    })
                    found = True
                    break
            
            # 如果没有找到已知场景，尝试提取新场景（简单模式）
            if not found:
                # 可以在这里添加新场景提取逻辑
                pass
        
        return scenes[:10]  # 最多10个场景
    
    def _extract_plot_points(self, content: str) -> List[str]:
        """提取情节要点"""
        # 提取关键动作和事件
        action_patterns = [
            r'([^。！？]+(?:打|杀|救|逃|追|找|发现|遇到|决定|开始|结束)[^。！？]+[。！？])',
            r'([^。！？]+(?:突然|忽然|瞬间|立刻|马上)[^。！？]+[。！？])'
        ]
        
        plot_points = []
        for pattern in action_patterns:
            matches = re.findall(pattern, content)
            plot_points.extend(matches[:5])  # 每章最多5个要点
        
        return plot_points[:5]
    
    def _extract_characters_in_chapter(self, content: str, novel_characters: Dict) -> Dict:
        """提取章节中出现的人物"""
        characters_in_chapter = {}
        
        for char_name, char_info in novel_characters.items():
            # 检查人物是否在本章出现
            if char_name in content:
                # 统计出现次数
                count = content.count(char_name)
                if count > 0:
                    characters_in_chapter[char_name] = {
                        'mention_count': count,
                        'personality': char_info.get('personality', {}),
                        'speaking_style': char_info.get('speaking_style', {}),
                        'key_actions': self._extract_character_actions(content, char_name)
                    }
        
        return characters_in_chapter
    
    def _extract_character_actions(self, content: str, char_name: str) -> List[str]:
        """提取人物的关键动作"""
        # 查找包含该人物的句子
        pattern = f'{char_name}[，,。！？；：:""""]?[^。！？；]*[。！？；]'
        sentences = re.findall(pattern, content)
        
        # 提取动作
        actions = []
        action_keywords = ['说', '道', '看', '笑', '走', '来', '去', '做', '想', '决定', '开始', '结束']
        
        for sent in sentences[:10]:  # 最多10句
            for keyword in action_keywords:
                if keyword in sent:
                    actions.append(sent[:50])  # 前50字符
                    break
        
        return actions[:5]  # 最多5个动作
    
    def _extract_emotional_flow(self, sentences: List[str]) -> List[Dict]:
        """提取情感流动"""
        emotional_flow = []
        
        emotion_keywords = {
            '积极': ['开心', '高兴', '快乐', '兴奋', '满足', '满意', '喜欢', '爱'],
            '消极': ['难过', '悲伤', '痛苦', '愤怒', '失望', '沮丧', '讨厌', '恨'],
            '紧张': ['紧张', '焦虑', '担心', '害怕', '恐惧', '不安'],
            '平静': ['平静', '冷静', '淡定', '从容', '镇定']
        }
        
        for i, sentence in enumerate(sentences[:30]):  # 分析前30句
            for emotion, keywords in emotion_keywords.items():
                score = sum(sentence.count(kw) for kw in keywords)
                if score > 0:
                    emotional_flow.append({
                        'position': i,
                        'emotion': emotion,
                        'intensity': score
                    })
                    break
        
        return emotional_flow[:10]  # 最多10个情感点
    
    def _calculate_description_ratio(self, content: str) -> float:
        """计算描写比例"""
        description_keywords = ['的', '地', '得', '很', '非常', '特别', '十分']
        description_count = sum(content.count(kw) for kw in description_keywords)
        return description_count / len(content) if content else 0
    
    def _calculate_action_ratio(self, content: str) -> float:
        """计算动作比例"""
        action_keywords = ['走', '跑', '跳', '打', '看', '说', '做', '来', '去', '动']
        action_count = sum(content.count(kw) for kw in action_keywords)
        return action_count / len(content) if content else 0
    
    def _check_character_continuity(self, current_chars: Dict, prev_chars: Dict) -> Dict:
        """检查人物连续性"""
        continuity = {
            'continued': [],  # 继续出现的人物
            'new': [],  # 新出现的人物
            'disappeared': []  # 消失的人物
        }
        
        for char_name in current_chars.keys():
            if char_name in prev_chars:
                continuity['continued'].append(char_name)
            else:
                continuity['new'].append(char_name)
        
        for char_name in prev_chars.keys():
            if char_name not in current_chars:
                continuity['disappeared'].append(char_name)
        
        return continuity
    
    def _validate_structured_data(self, data: Dict) -> bool:
        """验证结构化数据"""
        # 检查必需字段
        if 'metadata' not in data:
            return False
        
        if 'chapters' not in data or len(data['chapters']) == 0:
            return False
        
        # 检查章节数据完整性
        for chapter in data['chapters']:
            if 'chapter_num' not in chapter or 'paragraphs' not in chapter:
                return False
            
            if len(chapter['paragraphs']) == 0:
                return False
        
        return True
    
    def process_batch(self, novels_dir: str, category: str, site: str = "m.shuhaige.net") -> Dict:
        """
        批量处理小说
        
        Args:
            novels_dir: 小说目录
            category: 类型
            site: 来源网站
        
        Returns:
            处理统计
        """
        print(f"\n📚 开始批量处理结构化数据...")
        print(f"   目录: {novels_dir}")
        print(f"   类型: {category}")
        
        stats = {
            'total': 0,
            'success': 0,
            'failed': 0
        }
        
        # 查找所有小说文件
        novel_files = []
        for root, dirs, files in os.walk(novels_dir):
            for file in files:
                if file.endswith('.txt'):
                    novel_files.append(os.path.join(root, file))
        
        stats['total'] = len(novel_files)
        
        # 处理每本小说
        for novel_file in novel_files:
            try:
                result = self.process_novel(novel_file, category, site)
                if result:
                    stats['success'] += 1
                else:
                    stats['failed'] += 1
            except Exception as e:
                print(f"    ❌ 处理失败: {e}")
                stats['failed'] += 1
        
        print(f"\n✅ 批量处理完成:")
        print(f"   总计: {stats['total']}")
        print(f"   成功: {stats['success']}")
        print(f"   失败: {stats['failed']}")
        
        return stats

