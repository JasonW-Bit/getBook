#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能分析器
用于深度分析小说内容，提取人物性格、风格、语气、故事结构等丰富信息
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from collections import Counter, defaultdict
import jieba
import jieba.analyse

# 导入配置中心
try:
    from .config_center import ConfigCenter
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    from config_center import ConfigCenter


class IntelligentAnalyzer:
    """智能分析器 - 深度提取小说特征"""
    
    def __init__(self, config_center: Optional[ConfigCenter] = None):
        """
        初始化分析器
        
        Args:
            config_center: 配置中心实例（可选）
        """
        # 初始化jieba
        try:
            jieba.initialize()
        except:
            pass
        
        # 使用配置中心
        self.config = config_center or ConfigCenter()
    
    def analyze_novel_structure(self, content: str) -> Dict:
        """
        分析小说结构（智能版）
        
        Args:
            content: 小说内容
        
        Returns:
            结构化分析结果
        """
        result = {
            'characters': self._extract_characters_intelligent(content),
            'plot_structure': self._extract_plot_structure(content),
            'writing_style': self._analyze_writing_style(content),
            'tone_mood': self._analyze_tone_mood(content),
            'narrative_techniques': self._analyze_narrative_techniques(content),
            'story_richness': self._analyze_story_richness(content),
            'character_development': self._analyze_character_development(content),
            'dialogue_style': self._analyze_dialogue_style(content),
            'scene_transitions': self._extract_scene_transitions(content),
            'emotional_arcs': self._extract_emotional_arcs(content)
        }
        
        return result
    
    def _extract_characters_intelligent(self, content: str) -> Dict[str, Dict]:
        """
        智能提取人物信息（包含性格、特征、关系等）
        
        Args:
            content: 小说内容
        
        Returns:
            人物信息字典 {name: {personality, traits, relationships, etc.}}
        """
        characters = {}
        
        # 提取人物名称（通过对话、动作等）
        # 1. 从对话中提取
        dialogue_pattern = r'["""]([^"""]+)["""]'
        dialogues = re.findall(dialogue_pattern, content)
        
        # 2. 从动作描述中提取（"XX说"、"XX道"等）
        action_pattern = r'([\u4e00-\u9fa5]{2,4})(?:说|道|想|看|笑|哭|走|来|去|站|坐)'
        actions = re.findall(action_pattern, content)
        
        # 3. 从人称代词前后提取
        pronoun_pattern = r'(?:他|她|它|他们|她们)(?:的|是|在|有|说|道|想|看|笑|哭|走|来|去|站|坐)'
        
        # 合并所有可能的人物名称
        all_names = set()
        for dialogue in dialogues[:100]:  # 分析前100段对话
            # 提取对话前的说话人
            name_match = re.search(r'([\u4e00-\u9fa5]{2,4})(?:说|道|：|:)\s*["""]', dialogue)
            if name_match:
                all_names.add(name_match.group(1))
        
        for action in actions[:200]:
            if len(action) >= 2 and len(action) <= 4:
                all_names.add(action)
        
        # 分析每个人物的特征
        for name in list(all_names)[:20]:  # 限制最多20个人物
            if self._is_valid_character_name(name):
                char_info = self._analyze_character_details(content, name)
                if char_info:
                    characters[name] = char_info
        
        return characters
    
    def _is_valid_character_name(self, name: str) -> bool:
        """判断是否是有效的人物名称"""
        # 排除常见非人名词汇
        invalid_words = {'这个', '那个', '什么', '怎么', '为什么', '哪里', '时候', 
                        '今天', '明天', '昨天', '现在', '以后', '之前', '之后',
                        '这里', '那里', '哪里', '这样', '那样', '怎么', '如何'}
        return name not in invalid_words and len(name) >= 2
    
    def _analyze_character_details(self, content: str, name: str) -> Optional[Dict]:
        """
        分析单个人物的详细信息
        
        Args:
            content: 小说内容
            name: 人物名称
        
        Returns:
            人物详细信息
        """
        # 提取包含该人物的所有句子
        pattern = f'{name}[，,。！？；：:""""]?[^。！？；]*[。！？；]'
        sentences = re.findall(pattern, content)
        
        if len(sentences) < 3:  # 至少需要3个句子
            return None
        
        # 分析性格特征
        personality = self._extract_personality(sentences, name)
        
        # 分析外貌特征
        appearance = self._extract_appearance(sentences, name)
        
        # 分析说话风格
        speaking_style = self._analyze_speaking_style(sentences, name)
        
        # 分析行为模式
        behavior_patterns = self._analyze_behavior_patterns(sentences, name)
        
        # 分析情感倾向
        emotional_tendency = self._analyze_emotional_tendency(sentences, name)
        
        return {
            'name': name,
            'personality': personality,
            'appearance': appearance,
            'speaking_style': speaking_style,
            'behavior_patterns': behavior_patterns,
            'emotional_tendency': emotional_tendency,
            'mention_count': len(sentences),
            'key_phrases': self._extract_key_phrases(sentences, name)
        }
    
    def _extract_personality(self, sentences: List[str], name: str) -> Dict:
        """提取人物性格"""
        personality_keywords = {
            '开朗': ['笑', '开心', '快乐', '高兴', '愉快', '活泼'],
            '内向': ['沉默', '安静', '少言', '内向', '害羞', '腼腆'],
            '勇敢': ['勇敢', '无畏', '大胆', '果断', '坚决', '坚定'],
            '谨慎': ['小心', '谨慎', '仔细', '慎重', '警惕', '防备'],
            '聪明': ['聪明', '智慧', '机智', '敏锐', '精明', '睿智'],
            '善良': ['善良', '仁慈', '温和', '友好', '和善', '温柔'],
            '冷酷': ['冷酷', '冷漠', '无情', '冷血', '冰冷', '淡漠'],
            '幽默': ['幽默', '风趣', '搞笑', '逗', '有趣', '诙谐']
        }
        
        personality_scores = {}
        text = ' '.join(sentences)
        
        for trait, keywords in personality_keywords.items():
            score = sum(text.count(kw) for kw in keywords)
            if score > 0:
                personality_scores[trait] = score
        
        # 返回得分最高的3个性格特征
        sorted_traits = sorted(personality_scores.items(), key=lambda x: x[1], reverse=True)
        return {trait: score for trait, score in sorted_traits[:3]}
    
    def _extract_appearance(self, sentences: List[str], name: str) -> Dict:
        """提取外貌特征（使用配置中心）"""
        appearance_keywords = self.config.get_appearance_keywords()
        
        appearance = {}
        text = ' '.join(sentences)
        
        for category, keywords in appearance_keywords.items():
            matches = [kw for kw in keywords if kw in text]
            if matches:
                appearance[category] = matches[:2]  # 最多2个特征
        
        return appearance
    
    def _analyze_speaking_style(self, sentences: List[str], name: str) -> Dict:
        """分析说话风格"""
        # 提取该人物的对话
        dialogues = []
        for sent in sentences:
            # 查找 "XX说：" 或 "XX道：" 后的对话
            match = re.search(rf'{name}(?:说|道|：|:)\s*["""]([^"""]+)["""]', sent)
            if match:
                dialogues.append(match.group(1))
        
        if not dialogues:
            return {}
        
        # 分析对话特征
        avg_length = sum(len(d) for d in dialogues) / len(dialogues) if dialogues else 0
        question_ratio = sum(1 for d in dialogues if '？' in d or '?' in d) / len(dialogues) if dialogues else 0
        exclamation_ratio = sum(1 for d in dialogues if '！' in d or '!' in d) / len(dialogues) if dialogues else 0
        
        # 分析语气词使用（使用配置中心）
        tone_words = self.config.get_tone_words()
        tone_usage = {}
        for word in tone_words:
            count = sum(d.count(word) for d in dialogues)
            if count > 0:
                tone_usage[word] = count
        
        return {
            'avg_length': round(avg_length, 1),
            'question_ratio': round(question_ratio, 2),
            'exclamation_ratio': round(exclamation_ratio, 2),
            'tone_words': tone_usage,
            'style': self._classify_speaking_style(dialogues)
        }
    
    def _classify_speaking_style(self, dialogues: List[str]) -> str:
        """分类说话风格"""
        if not dialogues:
            return '未知'
        
        text = ' '.join(dialogues)
        
        # 分析特征
        if any(word in text for word in ['哈哈', '呵呵', '嘿嘿', '嘻嘻']):
            return '幽默轻松'
        elif any(word in text for word in ['哼', '切', '呸', '滚']):
            return '强势直接'
        elif any(word in text for word in ['嗯', '啊', '哦', '呃']):
            return '犹豫不决'
        elif len(text) / len(dialogues) > 30:
            return '详细描述'
        elif len(text) / len(dialogues) < 10:
            return '简洁明了'
        else:
            return '正常'
    
    def _analyze_behavior_patterns(self, sentences: List[str], name: str) -> List[str]:
        """分析行为模式（使用配置中心）"""
        behavior_keywords = self.config.get_action_keywords()
        
        text = ' '.join(sentences)
        patterns = []
        
        for pattern, keywords in behavior_keywords.items():
            count = sum(text.count(kw) for kw in keywords)
            if count > 2:
                patterns.append(pattern)
        
        return patterns[:3]  # 最多3个模式
    
    def _analyze_emotional_tendency(self, sentences: List[str], name: str) -> Dict:
        """分析情感倾向（使用配置中心）"""
        emotion_keywords = self.config.get_emotion_keywords()
        
        text = ' '.join(sentences)
        emotions = {}
        
        for emotion, keywords in emotion_keywords.items():
            score = sum(text.count(kw) for kw in keywords)
            if score > 0:
                emotions[emotion] = score
        
        return emotions
    
    def _extract_key_phrases(self, sentences: List[str], name: str) -> List[str]:
        """提取关键短语"""
        # 提取包含该人物的关键短语
        phrases = []
        for sent in sentences[:20]:  # 只分析前20句
            # 提取 "XX的XX" 或 "XX很XX" 等模式
            patterns = [
                rf'{name}的([\u4e00-\u9fa5]+)',
                rf'{name}很([\u4e00-\u9fa5]+)',
                rf'{name}非常([\u4e00-\u9fa5]+)',
                rf'{name}特别([\u4e00-\u9fa5]+)'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, sent)
                phrases.extend(matches)
        
        # 返回最常见的短语
        counter = Counter(phrases)
        return [phrase for phrase, count in counter.most_common(5)]
    
    def _extract_plot_structure(self, content: str) -> Dict:
        """提取情节结构"""
        # 按章节分割
        chapters = re.split(r'第\s*\d+\s*章[：:：]?\s*.+?\n', content)
        
        plot_structure = {
            'total_chapters': len(chapters) - 1,  # 减去第一个空章节
            'chapter_summaries': [],
            'key_events': [],
            'plot_points': []
        }
        
        # 分析每个章节
        for i, chapter in enumerate(chapters[1:11], 1):  # 分析前10章
            if len(chapter) < 100:
                continue
            
            # 提取章节关键事件
            events = self._extract_chapter_events(chapter)
            plot_structure['chapter_summaries'].append({
                'chapter_num': i,
                'length': len(chapter),
                'key_events': events[:3]  # 每章最多3个关键事件
            })
        
        return plot_structure
    
    def _extract_chapter_events(self, chapter: str) -> List[str]:
        """提取章节关键事件"""
        # 提取动作性强的句子
        action_patterns = [
            r'([^。！？]+(?:打|杀|救|逃|追|找|发现|遇到|决定|开始|结束)[^。！？]+[。！？])',
            r'([^。！？]+(?:突然|忽然|瞬间|立刻|马上)[^。！？]+[。！？])'
        ]
        
        events = []
        for pattern in action_patterns:
            matches = re.findall(pattern, chapter)
            events.extend(matches[:5])  # 每章最多5个事件
        
        return events[:5]
    
    def _analyze_writing_style(self, content: str) -> Dict:
        """分析写作风格"""
        # 句子长度分析
        sentences = re.split(r'[。！？]', content)
        sentence_lengths = [len(s) for s in sentences if s.strip()]
        avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
        
        # 段落长度分析
        paragraphs = re.split(r'\n\s*\n', content)
        paragraph_lengths = [len(p) for p in paragraphs if p.strip()]
        avg_paragraph_length = sum(paragraph_lengths) / len(paragraph_lengths) if paragraph_lengths else 0
        
        # 修辞手法分析
        rhetorical_devices = {
            '比喻': len(re.findall(r'(?:像|如|似|仿佛|犹如|好比)', content)),
            '排比': len(re.findall(r'([^，,。！？]+，){2,}[^，,。！？]+', content)),
            '对比': len(re.findall(r'(?:但是|然而|不过|可是|却)', content)),
            '设问': len(re.findall(r'[？?]', content))
        }
        
        # 词汇丰富度
        words = re.findall(r'[\u4e00-\u9fa5]+', content)
        unique_words = len(set(words))
        vocab_richness = unique_words / len(words) if words else 0
        
        return {
            'avg_sentence_length': round(avg_sentence_length, 1),
            'avg_paragraph_length': round(avg_paragraph_length, 1),
            'rhetorical_devices': rhetorical_devices,
            'vocab_richness': round(vocab_richness, 3),
            'style_type': self._classify_writing_style(avg_sentence_length, vocab_richness)
        }
    
    def _classify_writing_style(self, avg_sentence_length: float, vocab_richness: float) -> str:
        """分类写作风格"""
        if avg_sentence_length > 50 and vocab_richness > 0.3:
            return '详细描述型'
        elif avg_sentence_length < 20 and vocab_richness < 0.2:
            return '简洁明快型'
        elif vocab_richness > 0.35:
            return '文采丰富型'
        else:
            return '平衡型'
    
    def _analyze_tone_mood(self, content: str) -> Dict:
        """分析语气和氛围（使用配置中心）"""
        # 情感词汇分析（使用配置中心）
        emotion_words = self.config.get_emotion_keywords()
        
        mood_scores = {}
        for mood, words in emotion_words.items():
            score = sum(content.count(word) for word in words)
            if score > 0:
                mood_scores[mood] = score
        
        # 标点符号分析
        punctuation = {
            'exclamation': content.count('！') + content.count('!'),
            'question': content.count('？') + content.count('?'),
            'ellipsis': content.count('…') + content.count('...')
        }
        
        return {
            'mood_scores': mood_scores,
            'punctuation': punctuation,
            'dominant_mood': max(mood_scores.items(), key=lambda x: x[1])[0] if mood_scores else '中性'
        }
    
    def _analyze_narrative_techniques(self, content: str) -> Dict:
        """分析叙事技巧"""
        techniques = {
            '第一人称': content.count('我'),
            '第三人称': content.count('他') + content.count('她'),
            '倒叙': len(re.findall(r'(?:回忆|想起|记得|那时|当时|以前)', content)),
            '插叙': len(re.findall(r'(?:突然|忽然|这时|此时|此刻)', content)),
            '心理描写': len(re.findall(r'(?:想|思考|觉得|认为|感觉|感受)', content)),
            '环境描写': len(re.findall(r'(?:看到|看见|发现|注意到)', content))
        }
        
        return techniques
    
    def _analyze_story_richness(self, content: str) -> Dict:
        """分析故事丰富性（使用配置中心）"""
        # 场景多样性（使用配置中心）
        scene_keywords = self.config.get_scene_keywords()
        scene_diversity = sum(1 for kw in scene_keywords if kw in content)
        
        # 情节复杂度（通过转折词）
        plot_complexity = len(re.findall(r'(?:但是|然而|不过|可是|却|突然|忽然)', content))
        
        # 人物互动
        interaction_keywords = ['说', '道', '看', '笑', '走', '来', '去', '做', '想']
        interaction_density = sum(content.count(kw) for kw in interaction_keywords) / len(content) if content else 0
        
        return {
            'scene_diversity': scene_diversity,
            'plot_complexity': plot_complexity,
            'interaction_density': round(interaction_density, 4),
            'richness_score': round((scene_diversity * 0.3 + plot_complexity * 0.4 + interaction_density * 100 * 0.3), 2)
        }
    
    def _analyze_character_development(self, content: str) -> Dict:
        """分析人物塑造"""
        # 人物出现频率
        character_pattern = r'([\u4e00-\u9fa5]{2,4})(?:说|道|想|看|笑|哭|走|来|去)'
        characters = re.findall(character_pattern, content)
        character_frequency = Counter(characters)
        
        # 主要人物
        main_characters = [name for name, count in character_frequency.most_common(5)]
        
        # 人物描写深度（通过形容词、副词等）
        description_keywords = ['的', '地', '得', '很', '非常', '特别', '十分', '极其']
        description_density = sum(content.count(kw) for kw in description_keywords) / len(content) if content else 0
        
        return {
            'main_characters': main_characters,
            'character_count': len(character_frequency),
            'description_density': round(description_density, 4),
            'development_score': round(len(main_characters) * description_density * 100, 2)
        }
    
    def _analyze_dialogue_style(self, content: str) -> Dict:
        """分析对话风格"""
        dialogues = re.findall(r'["""]([^"""]+)["""]', content)
        
        if not dialogues:
            return {}
        
        # 对话长度分布
        dialogue_lengths = [len(d) for d in dialogues]
        avg_dialogue_length = sum(dialogue_lengths) / len(dialogue_lengths) if dialogue_lengths else 0
        
        # 对话类型
        question_ratio = sum(1 for d in dialogues if '？' in d or '?' in d) / len(dialogues) if dialogues else 0
        exclamation_ratio = sum(1 for d in dialogues if '！' in d or '!' in d) / len(dialogues) if dialogues else 0
        
        return {
            'total_dialogues': len(dialogues),
            'avg_length': round(avg_dialogue_length, 1),
            'question_ratio': round(question_ratio, 2),
            'exclamation_ratio': round(exclamation_ratio, 2),
            'dialogue_density': round(len(dialogues) / len(content.split('。')) if content.split('。') else 0, 3)
        }
    
    def _extract_scene_transitions(self, content: str) -> List[Dict]:
        """提取场景转换"""
        transition_keywords = ['突然', '忽然', '这时', '此时', '此刻', '然后', '接着', '随后', '之后', '后来']
        
        transitions = []
        sentences = re.split(r'[。！？]', content)
        
        for i, sentence in enumerate(sentences):
            for keyword in transition_keywords:
                if keyword in sentence:
                    transitions.append({
                        'position': i,
                        'keyword': keyword,
                        'context': sentence[:50]  # 前50字符
                    })
                    break
        
        return transitions[:20]  # 最多20个转换
    
    def _extract_emotional_arcs(self, content: str) -> List[Dict]:
        """提取情感弧线"""
        # 将内容分成多个段落
        paragraphs = re.split(r'\n\s*\n', content)
        
        emotional_arcs = []
        for i, para in enumerate(paragraphs[:50]):  # 分析前50段
            if len(para) < 50:
                continue
            
            # 分析段落情感
            positive_words = ['开心', '高兴', '快乐', '兴奋', '满足', '满意', '喜欢', '爱']
            negative_words = ['难过', '悲伤', '痛苦', '愤怒', '失望', '沮丧', '讨厌', '恨']
            
            positive_score = sum(para.count(word) for word in positive_words)
            negative_score = sum(para.count(word) for word in negative_words)
            
            if positive_score > negative_score:
                emotion = '积极'
                intensity = positive_score
            elif negative_score > positive_score:
                emotion = '消极'
                intensity = negative_score
            else:
                emotion = '中性'
                intensity = 0
            
            if intensity > 0:
                emotional_arcs.append({
                    'position': i,
                    'emotion': emotion,
                    'intensity': intensity
                })
        
        return emotional_arcs[:30]  # 最多30个情感点

