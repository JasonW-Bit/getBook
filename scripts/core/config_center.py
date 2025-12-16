#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置中心
管理所有关键词、特征、规则等配置，支持动态学习和更新
"""

import os
import json
from typing import Dict, List, Set, Optional
from collections import Counter, defaultdict
from pathlib import Path


class ConfigCenter:
    """配置中心 - 统一管理所有配置，支持动态学习"""
    
    def __init__(self, config_dir: str = "data/config"):
        """
        初始化配置中心
        
        Args:
            config_dir: 配置目录
        """
        self.config_dir = config_dir
        os.makedirs(self.config_dir, exist_ok=True)
        
        # 配置文件路径
        self.personality_keywords_file = os.path.join(config_dir, 'personality_keywords.json')
        self.emotion_keywords_file = os.path.join(config_dir, 'emotion_keywords.json')
        self.genre_keywords_file = os.path.join(config_dir, 'genre_keywords.json')
        self.appearance_keywords_file = os.path.join(config_dir, 'appearance_keywords.json')
        self.action_keywords_file = os.path.join(config_dir, 'action_keywords.json')
        self.scene_keywords_file = os.path.join(config_dir, 'scene_keywords.json')
        self.rhetorical_devices_file = os.path.join(config_dir, 'rhetorical_devices.json')
        self.speaking_style_keywords_file = os.path.join(config_dir, 'speaking_style_keywords.json')
        self.behavior_patterns_file = os.path.join(config_dir, 'behavior_patterns.json')
        self.tone_words_file = os.path.join(config_dir, 'tone_words.json')
        
        # 加载配置
        self._load_all_configs()
    
    def _load_all_configs(self):
        """加载所有配置"""
        # 如果配置文件不存在，创建默认配置
        if not os.path.exists(self.personality_keywords_file):
            self._create_default_configs()
        
        # 加载配置
        self.personality_keywords = self._load_json(self.personality_keywords_file, {})
        self.emotion_keywords = self._load_json(self.emotion_keywords_file, {})
        self.genre_keywords = self._load_json(self.genre_keywords_file, {})
        self.appearance_keywords = self._load_json(self.appearance_keywords_file, {})
        self.action_keywords = self._load_json(self.action_keywords_file, {})
        self.scene_keywords = self._load_json(self.scene_keywords_file, [])
        self.rhetorical_devices = self._load_json(self.rhetorical_devices_file, {})
        self.speaking_style_keywords = self._load_json(self.speaking_style_keywords_file, {})
        self.behavior_patterns = self._load_json(self.behavior_patterns_file, {})
        self.tone_words = self._load_json(self.tone_words_file, [])
    
    def _load_json(self, file_path: str, default: any) -> any:
        """加载JSON文件"""
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  加载配置失败 {file_path}: {e}")
                return default
        return default
    
    def _save_json(self, file_path: str, data: any):
        """保存JSON文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️  保存配置失败 {file_path}: {e}")
    
    def _create_default_configs(self):
        """创建默认配置"""
        # 性格关键词
        self.personality_keywords = {
            '开朗': ['笑', '开心', '快乐', '高兴', '愉快', '活泼', '乐观', '阳光'],
            '内向': ['沉默', '安静', '少言', '内向', '害羞', '腼腆', '孤僻', '不善言辞'],
            '勇敢': ['勇敢', '无畏', '大胆', '果断', '坚决', '坚定', '英勇', '果敢'],
            '谨慎': ['小心', '谨慎', '仔细', '慎重', '警惕', '防备', '审慎', '周密'],
            '聪明': ['聪明', '智慧', '机智', '敏锐', '精明', '睿智', '聪慧', '机灵'],
            '善良': ['善良', '仁慈', '温和', '友好', '和善', '温柔', '慈祥', '仁爱'],
            '冷酷': ['冷酷', '冷漠', '无情', '冷血', '冰冷', '淡漠', '冷峻', '冷硬'],
            '幽默': ['幽默', '风趣', '搞笑', '逗', '有趣', '诙谐', '滑稽', '俏皮']
        }
        self._save_json(self.personality_keywords_file, self.personality_keywords)
        
        # 情感关键词
        self.emotion_keywords = {
            '积极': ['开心', '高兴', '快乐', '兴奋', '满足', '满意', '喜欢', '爱', '美好', '幸福', '愉悦', '欣喜'],
            '消极': ['难过', '悲伤', '痛苦', '愤怒', '失望', '沮丧', '讨厌', '恨', '痛苦', '绝望', '沮丧', '郁闷'],
            '紧张': ['紧张', '焦虑', '担心', '害怕', '恐惧', '不安', '担忧', '惊慌', '惶恐', '忐忑'],
            '平静': ['平静', '冷静', '淡定', '从容', '镇定', '安宁', '宁静', '平和', '沉稳']
        }
        self._save_json(self.emotion_keywords_file, self.emotion_keywords)
        
        # 类型关键词
        self.genre_keywords = {
            '都市': ['都市', '城市', '公司', '职场', '商业', '白领', '办公室', '企业', '商场', '咖啡厅'],
            '玄幻': ['修炼', '境界', '功法', '丹药', '宗门', '灵气', '真气', '法术', '仙术', '神通'],
            '言情': ['爱情', '恋爱', '结婚', '分手', '感情', '恋人', '情侣', '约会', '求婚', '婚礼'],
            '武侠': ['武功', '江湖', '门派', '剑法', '内力', '轻功', '刀法', '拳法', '武林', '侠客'],
            '科幻': ['科技', '未来', '机器人', '太空', '星际', '飞船', '人工智能', '虚拟', '量子', '激光'],
            '悬疑': ['案件', '推理', '线索', '真相', '凶手', '侦探', '证据', '调查', '谜团', '破案']
        }
        self._save_json(self.genre_keywords_file, self.genre_keywords)
        
        # 外貌关键词
        self.appearance_keywords = {
            '身高': ['高', '矮', '中等', '修长', '魁梧', '娇小', '挺拔', '高大'],
            '体型': ['瘦', '胖', '健壮', '苗条', '丰满', '匀称', '纤细', '魁梧'],
            '容貌': ['美', '帅', '漂亮', '英俊', '清秀', '普通', '平凡', '精致', '俊朗', '美丽'],
            '气质': ['优雅', '高贵', '冷艳', '清纯', '成熟', '青春', '端庄', '妩媚']
        }
        self._save_json(self.appearance_keywords_file, self.appearance_keywords)
        
        # 动作关键词
        self.action_keywords = {
            '行动派': ['走', '跑', '冲', '跳', '动', '做', '执行', '行动', '移动', '前进'],
            '思考派': ['想', '思考', '考虑', '琢磨', '思索', '分析', '沉思', '深思', '思考', '琢磨'],
            '观察派': ['看', '观察', '注视', '打量', '审视', '瞧', '望', '凝视', '注视', '观察'],
            '情感派': ['笑', '哭', '怒', '喜', '悲', '惊', '乐', '哀', '愁', '忧']
        }
        self._save_json(self.action_keywords_file, self.action_keywords)
        
        # 场景关键词
        self.scene_keywords = [
            '房间', '街道', '学校', '公司', '餐厅', '公园', '医院', '商场', '家', '办公室',
            '门口', '窗前', '客厅', '卧室', '厨房', '书房', '教室', '图书馆', '咖啡厅', '酒吧'
        ]
        self._save_json(self.scene_keywords_file, self.scene_keywords)
        
        # 修辞手法
        self.rhetorical_devices = {
            '比喻': ['像', '如', '似', '仿佛', '犹如', '好比', '宛如', '如同'],
            '排比': ['pattern'],  # 模式匹配
            '对比': ['但是', '然而', '不过', '可是', '却', '而', '但', '然而'],
            '设问': ['pattern']  # 模式匹配
        }
        self._save_json(self.rhetorical_devices_file, self.rhetorical_devices)
        
        # 说话风格关键词
        self.speaking_style_keywords = {
            '幽默轻松': ['哈哈', '呵呵', '嘿嘿', '嘻嘻', '搞笑', '逗', '有趣'],
            '强势直接': ['哼', '切', '呸', '滚', '闭嘴', '少废话', '别废话'],
            '犹豫不决': ['嗯', '啊', '哦', '呃', '那个', '这个', '也许', '可能'],
            '详细描述': ['pattern'],  # 长句子模式
            '简洁明了': ['pattern']  # 短句子模式
        }
        self._save_json(self.speaking_style_keywords_file, self.speaking_style_keywords)
        
        # 行为模式
        self.behavior_patterns = {
            '行动派': ['走', '跑', '冲', '跳', '动', '做'],
            '思考派': ['想', '思考', '考虑', '琢磨', '思索', '分析'],
            '观察派': ['看', '观察', '注视', '打量', '审视', '瞧'],
            '情感派': ['笑', '哭', '怒', '喜', '悲', '惊']
        }
        self._save_json(self.behavior_patterns_file, self.behavior_patterns)
        
        # 语气词
        self.tone_words = ['啊', '呀', '呢', '吧', '嘛', '哦', '嗯', '哼', '哈', '唉', '哎', '哟']
        self._save_json(self.tone_words_file, self.tone_words)
    
    def get_personality_keywords(self, trait: Optional[str] = None) -> Dict[str, List[str]]:
        """获取性格关键词"""
        if trait:
            return self.personality_keywords.get(trait, [])
        return self.personality_keywords
    
    def get_emotion_keywords(self, emotion: Optional[str] = None) -> Dict[str, List[str]]:
        """获取情感关键词"""
        if emotion:
            return self.emotion_keywords.get(emotion, [])
        return self.emotion_keywords
    
    def get_genre_keywords(self, genre: Optional[str] = None) -> Dict[str, List[str]]:
        """获取类型关键词"""
        if genre:
            return self.genre_keywords.get(genre, [])
        return self.genre_keywords
    
    def get_appearance_keywords(self, category: Optional[str] = None) -> Dict[str, List[str]]:
        """获取外貌关键词"""
        if category:
            return self.appearance_keywords.get(category, [])
        return self.appearance_keywords
    
    def get_action_keywords(self, pattern: Optional[str] = None) -> Dict[str, List[str]]:
        """获取动作关键词"""
        if pattern:
            return self.action_keywords.get(pattern, [])
        return self.action_keywords
    
    def get_scene_keywords(self) -> List[str]:
        """获取场景关键词"""
        return self.scene_keywords
    
    def get_tone_words(self) -> List[str]:
        """获取语气词"""
        return self.tone_words
    
    def learn_from_analysis(self, analysis_results: Dict):
        """
        从分析结果中学习新关键词
        
        Args:
            analysis_results: 分析结果字典
        """
        print("\n📚 从分析结果中学习新关键词...")
        
        learned_count = 0
        
        # 从人物分析中学习
        characters = analysis_results.get('characters', {})
        for char_name, char_info in characters.items():
            # 学习性格关键词
            personality = char_info.get('personality', {})
            for trait, score in personality.items():
                if trait not in self.personality_keywords:
                    self.personality_keywords[trait] = []
                # 从关键短语中提取新关键词
                key_phrases = char_info.get('key_phrases', [])
                for phrase in key_phrases:
                    if phrase not in self.personality_keywords[trait]:
                        self.personality_keywords[trait].append(phrase)
                        learned_count += 1
            
            # 学习说话风格关键词
            speaking_style = char_info.get('speaking_style', {})
            style_type = speaking_style.get('style', '')
            if style_type and style_type not in self.speaking_style_keywords:
                self.speaking_style_keywords[style_type] = []
                learned_count += 1
            
            # 学习语气词
            tone_words = speaking_style.get('tone_words', {})
            for word, count in tone_words.items():
                if word not in self.tone_words:
                    self.tone_words.append(word)
                    learned_count += 1
        
        # 从情感分析中学习
        tone_mood = analysis_results.get('tone_mood', {})
        mood_scores = tone_mood.get('mood_scores', {})
        for mood, score in mood_scores.items():
            if mood not in self.emotion_keywords:
                self.emotion_keywords[mood] = []
                learned_count += 1
        
        # 从场景分析中学习
        scenes = analysis_results.get('scenes', [])
        for scene in scenes:
            location = scene.get('location', '')
            if location and location not in self.scene_keywords:
                self.scene_keywords.append(location)
                learned_count += 1
        
        # 保存更新的配置
        if learned_count > 0:
            self._save_all_configs()
            print(f"   ✅ 学习了 {learned_count} 个新关键词/特征")
        else:
            print(f"   ℹ️  未发现新关键词")
    
    def learn_from_text(self, text: str, category: str = 'general'):
        """
        从文本中自动提取和学习关键词
        
        Args:
            text: 文本内容
            category: 类别（用于分类学习）
        """
        import jieba
        import jieba.analyse
        
        # 提取关键词
        keywords = jieba.analyse.extract_tags(text, topK=20, withWeight=False)
        
        # 根据类别学习
        if category in self.genre_keywords:
            for keyword in keywords:
                if keyword not in self.genre_keywords[category]:
                    self.genre_keywords[category].append(keyword)
        
        # 保存配置
        self._save_all_configs()
    
    def add_keyword(self, category: str, keyword: str, subcategory: Optional[str] = None):
        """
        手动添加关键词
        
        Args:
            category: 类别（personality, emotion, genre等）
            keyword: 关键词
            subcategory: 子类别（如性格类型、情感类型等）
        """
        if category == 'personality':
            if subcategory:
                if subcategory not in self.personality_keywords:
                    self.personality_keywords[subcategory] = []
                if keyword not in self.personality_keywords[subcategory]:
                    self.personality_keywords[subcategory].append(keyword)
                    self._save_json(self.personality_keywords_file, self.personality_keywords)
                    return True
        elif category == 'emotion':
            if subcategory:
                if subcategory not in self.emotion_keywords:
                    self.emotion_keywords[subcategory] = []
                if keyword not in self.emotion_keywords[subcategory]:
                    self.emotion_keywords[subcategory].append(keyword)
                    self._save_json(self.emotion_keywords_file, self.emotion_keywords)
                    return True
        elif category == 'genre':
            if subcategory:
                if subcategory not in self.genre_keywords:
                    self.genre_keywords[subcategory] = []
                if keyword not in self.genre_keywords[subcategory]:
                    self.genre_keywords[subcategory].append(keyword)
                    self._save_json(self.genre_keywords_file, self.genre_keywords)
                    return True
        elif category == 'scene':
            if keyword not in self.scene_keywords:
                self.scene_keywords.append(keyword)
                self._save_json(self.scene_keywords_file, self.scene_keywords)
                return True
        elif category == 'tone':
            if keyword not in self.tone_words:
                self.tone_words.append(keyword)
                self._save_json(self.tone_words_file, self.tone_words)
                return True
        
        return False
    
    def remove_keyword(self, category: str, keyword: str, subcategory: Optional[str] = None):
        """
        移除关键词
        
        Args:
            category: 类别
            keyword: 关键词
            subcategory: 子类别
        """
        if category == 'personality' and subcategory:
            if subcategory in self.personality_keywords:
                if keyword in self.personality_keywords[subcategory]:
                    self.personality_keywords[subcategory].remove(keyword)
                    self._save_json(self.personality_keywords_file, self.personality_keywords)
                    return True
        elif category == 'emotion' and subcategory:
            if subcategory in self.emotion_keywords:
                if keyword in self.emotion_keywords[subcategory]:
                    self.emotion_keywords[subcategory].remove(keyword)
                    self._save_json(self.emotion_keywords_file, self.emotion_keywords)
                    return True
        elif category == 'scene':
            if keyword in self.scene_keywords:
                self.scene_keywords.remove(keyword)
                self._save_json(self.scene_keywords_file, self.scene_keywords)
                return True
        elif category == 'tone':
            if keyword in self.tone_words:
                self.tone_words.remove(keyword)
                self._save_json(self.tone_words_file, self.tone_words)
                return True
        
        return False
    
    def _save_all_configs(self):
        """保存所有配置"""
        self._save_json(self.personality_keywords_file, self.personality_keywords)
        self._save_json(self.emotion_keywords_file, self.emotion_keywords)
        self._save_json(self.genre_keywords_file, self.genre_keywords)
        self._save_json(self.appearance_keywords_file, self.appearance_keywords)
        self._save_json(self.action_keywords_file, self.action_keywords)
        self._save_json(self.scene_keywords_file, self.scene_keywords)
        self._save_json(self.rhetorical_devices_file, self.rhetorical_devices)
        self._save_json(self.speaking_style_keywords_file, self.speaking_style_keywords)
        self._save_json(self.behavior_patterns_file, self.behavior_patterns)
        self._save_json(self.tone_words_file, self.tone_words)
    
    def get_statistics(self) -> Dict:
        """获取配置统计信息"""
        return {
            'personality_traits': len(self.personality_keywords),
            'personality_keywords_total': sum(len(v) for v in self.personality_keywords.values()),
            'emotion_types': len(self.emotion_keywords),
            'emotion_keywords_total': sum(len(v) for v in self.emotion_keywords.values()),
            'genres': len(self.genre_keywords),
            'genre_keywords_total': sum(len(v) for v in self.genre_keywords.values()),
            'scene_keywords': len(self.scene_keywords),
            'tone_words': len(self.tone_words)
        }
    
    def export_config(self, output_file: str):
        """导出所有配置"""
        config = {
            'personality_keywords': self.personality_keywords,
            'emotion_keywords': self.emotion_keywords,
            'genre_keywords': self.genre_keywords,
            'appearance_keywords': self.appearance_keywords,
            'action_keywords': self.action_keywords,
            'scene_keywords': self.scene_keywords,
            'rhetorical_devices': self.rhetorical_devices,
            'speaking_style_keywords': self.speaking_style_keywords,
            'behavior_patterns': self.behavior_patterns,
            'tone_words': self.tone_words
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def import_config(self, input_file: str):
        """导入配置"""
        if os.path.exists(input_file):
            with open(input_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.personality_keywords = config.get('personality_keywords', self.personality_keywords)
            self.emotion_keywords = config.get('emotion_keywords', self.emotion_keywords)
            self.genre_keywords = config.get('genre_keywords', self.genre_keywords)
            self.appearance_keywords = config.get('appearance_keywords', self.appearance_keywords)
            self.action_keywords = config.get('action_keywords', self.action_keywords)
            self.scene_keywords = config.get('scene_keywords', self.scene_keywords)
            self.rhetorical_devices = config.get('rhetorical_devices', self.rhetorical_devices)
            self.speaking_style_keywords = config.get('speaking_style_keywords', self.speaking_style_keywords)
            self.behavior_patterns = config.get('behavior_patterns', self.behavior_patterns)
            self.tone_words = config.get('tone_words', self.tone_words)
            
            self._save_all_configs()

