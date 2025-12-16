#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版训练数据生成器
从结构化数据生成包含人物性格、风格、语气等丰富信息的训练数据
"""

import os
import json
from typing import List, Dict, Optional
from pathlib import Path
from .intelligent_analyzer import IntelligentAnalyzer


class EnhancedTrainingDataGenerator:
    """增强版训练数据生成器 - 使用结构化数据生成丰富的训练样本"""
    
    def __init__(self, output_dir: str = "data/training"):
        """
        初始化生成器
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = output_dir
        self.structured_dir = os.path.join(output_dir, 'structured')
        self.processed_dir = os.path.join(output_dir, 'processed')
        self.analyzer = IntelligentAnalyzer()
        
        os.makedirs(self.processed_dir, exist_ok=True)
    
    def generate_from_structured_data(self, use_ai: bool = False) -> Optional[str]:
        """
        从结构化数据生成训练数据
        
        Args:
            use_ai: 是否使用AI生成改写样本
        
        Returns:
            训练数据文件路径
        """
        print("\n📝 从结构化数据生成训练样本...")
        
        training_samples = []
        
        # 查找所有结构化数据文件
        if not os.path.exists(self.structured_dir):
            print(f"  ❌ 结构化数据目录不存在: {self.structured_dir}")
            return None
        
        structured_files = [
            f for f in os.listdir(self.structured_dir)
            if f.endswith('_structured.json')
        ]
        
        if not structured_files:
            print(f"  ❌ 未找到结构化数据文件")
            return None
        
        print(f"  找到 {len(structured_files)} 个结构化数据文件")
        
        # 处理每个结构化文件
        for struct_file in structured_files:
            struct_path = os.path.join(self.structured_dir, struct_file)
            
            try:
                with open(struct_path, 'r', encoding='utf-8') as f:
                    structured_data = json.load(f)
                
                # 从结构化数据生成训练样本
                samples = self._generate_samples_from_structured(structured_data, use_ai)
                training_samples.extend(samples)
                
                print(f"    ✅ {Path(struct_file).stem}: {len(samples)} 个样本")
                
            except Exception as e:
                print(f"    ⚠️  处理 {struct_file} 失败: {e}")
                continue
        
        if not training_samples:
            print(f"\n❌ 未生成任何训练样本")
            return None
        
        # 数据验证
        print(f"\n🔍 验证训练数据...")
        valid_samples = self._validate_samples(training_samples)
        
        if not valid_samples:
            print(f"❌ 验证失败: 没有有效样本")
            return None
        
        print(f"  有效样本: {len(valid_samples)}/{len(training_samples)}")
        
        # 保存训练数据
        training_file = self._save_training_data(valid_samples)
        
        return training_file
    
    def _generate_samples_from_structured(self, structured_data: Dict, use_ai: bool) -> List[Dict]:
        """
        从结构化数据生成训练样本
        
        Args:
            structured_data: 结构化数据
            use_ai: 是否使用AI
        
        Returns:
            训练样本列表
        """
        samples = []
        
        metadata = structured_data.get('metadata', {})
        analysis = structured_data.get('analysis', {})
        chapters = structured_data.get('chapters', [])
        
        # 提取全局信息
        characters = analysis.get('characters', {})
        writing_style = analysis.get('writing_style', {})
        tone_mood = analysis.get('tone_mood', {})
        
        # 处理每个章节
        for chapter in chapters:
            chapter_samples = self._generate_chapter_samples(
                chapter, 
                metadata,
                characters,
                writing_style,
                tone_mood,
                use_ai
            )
            samples.extend(chapter_samples)
        
        return samples
    
    def _generate_chapter_samples(self, chapter: Dict, metadata: Dict, 
                                 characters: Dict, writing_style: Dict,
                                 tone_mood: Dict, use_ai: bool) -> List[Dict]:
        """从章节生成训练样本"""
        samples = []
        
        paragraphs = chapter.get('paragraphs', [])
        dialogues = chapter.get('dialogues', [])
        chapter_characters = chapter.get('characters', {})
        emotional_flow = chapter.get('emotional_flow', [])
        
        # 为每个段落生成样本
        for para in paragraphs[:20]:  # 每章最多20段
            if len(para) < 100:
                continue
            
            # 提取该段落的相关信息
            para_characters = self._extract_paragraph_characters(para, chapter_characters)
            para_emotion = self._extract_paragraph_emotion(para, emotional_flow)
            
            # 生成原始文本
            original = para[:2000]  # 限制长度
            
            # 生成改写文本（包含风格、语气等信息）
            rewritten = self._generate_rewritten_with_context(
                original,
                para_characters,
                para_emotion,
                writing_style,
                tone_mood,
                use_ai
            )
            
            if not rewritten or rewritten == original:
                continue
            
            # 构建训练样本（包含丰富信息）
            sample = {
                'original': original,
                'rewritten': rewritten,
                'style': self._get_style_id(metadata.get('category', '都市')),
                'source': metadata.get('title', '未知'),
                'site': metadata.get('site', 'm.shuhaige.net'),
                'category': metadata.get('category', '都市'),
                'chapter_num': chapter.get('chapter_num', 0),
                
                # 丰富的上下文信息
                'characters': para_characters,
                'emotion': para_emotion,
                'writing_style': writing_style.get('style_type', '平衡型'),
                'tone': tone_mood.get('dominant_mood', '中性'),
                'dialogue_style': chapter.get('writing_features', {}).get('dialogue_ratio', 0),
                'description_ratio': chapter.get('writing_features', {}).get('description_ratio', 0),
                'action_ratio': chapter.get('writing_features', {}).get('action_ratio', 0),
                
                # 人物性格和特征
                'character_personalities': self._extract_character_personalities(para_characters, characters),
                'character_speaking_styles': self._extract_character_speaking_styles(para_characters, characters)
            }
            
            samples.append(sample)
        
        return samples
    
    def _extract_paragraph_characters(self, paragraph: str, chapter_characters: Dict) -> List[str]:
        """提取段落中出现的人物"""
        characters_in_para = []
        for char_name in chapter_characters.keys():
            if char_name in paragraph:
                characters_in_para.append(char_name)
        return characters_in_para
    
    def _extract_paragraph_emotion(self, paragraph: str, emotional_flow: List[Dict]) -> Optional[str]:
        """提取段落情感"""
        emotion_keywords = {
            '积极': ['开心', '高兴', '快乐', '兴奋', '满足', '满意', '喜欢', '爱'],
            '消极': ['难过', '悲伤', '痛苦', '愤怒', '失望', '沮丧', '讨厌', '恨'],
            '紧张': ['紧张', '焦虑', '担心', '害怕', '恐惧', '不安'],
            '平静': ['平静', '冷静', '淡定', '从容', '镇定']
        }
        
        for emotion, keywords in emotion_keywords.items():
            if any(kw in paragraph for kw in keywords):
                return emotion
        
        return '中性'
    
    def _generate_rewritten_with_context(self, original: str, characters: List[str],
                                        emotion: Optional[str], writing_style: Dict,
                                        tone_mood: Dict, use_ai: bool) -> str:
        """生成包含上下文的改写文本"""
        # 这里可以调用AI或规则改写
        # 暂时使用简单的规则改写
        rewritten = original
        
        # 根据情感调整语气
        if emotion == '积极':
            # 可以添加积极的语气词
            pass
        elif emotion == '消极':
            # 可以调整语气
            pass
        
        # 根据写作风格调整
        style_type = writing_style.get('style_type', '平衡型')
        if style_type == '详细描述型':
            # 可以增加描述
            pass
        elif style_type == '简洁明快型':
            # 可以简化
            pass
        
        return rewritten
    
    def _extract_character_personalities(self, para_characters: List[str], all_characters: Dict) -> Dict:
        """提取人物性格"""
        personalities = {}
        for char_name in para_characters:
            if char_name in all_characters:
                char_info = all_characters[char_name]
                personalities[char_name] = char_info.get('personality', {})
        return personalities
    
    def _extract_character_speaking_styles(self, para_characters: List[str], all_characters: Dict) -> Dict:
        """提取人物说话风格"""
        speaking_styles = {}
        for char_name in para_characters:
            if char_name in all_characters:
                char_info = all_characters[char_name]
                speaking_styles[char_name] = char_info.get('speaking_style', {})
        return speaking_styles
    
    def _get_style_id(self, category: str) -> int:
        """根据分类获取风格ID"""
        style_map = {
            '都市': 11,
            '玄幻': 8,
            '言情': 5,
            '武侠': 9,
            '科幻': 8,
            '悬疑': 4,
            '历史': 1,
            '军事': 7,
            '游戏': 12,
            '竞技': 13,
            '仙侠': 10,
            '其他': 11,
            '未知': 11,
        }
        return style_map.get(category, 11)
    
    def _validate_samples(self, samples: List[Dict]) -> List[Dict]:
        """验证训练样本"""
        valid_samples = []
        
        for sample in samples:
            # 检查必需字段
            if not sample.get('original') or not sample.get('rewritten'):
                continue
            
            orig = sample['original'].strip()
            rew = sample['rewritten'].strip()
            
            # 检查长度
            if len(orig) < 50 or len(rew) < 50:
                continue
            
            # 检查风格ID
            if not isinstance(sample.get('style'), int):
                continue
            
            valid_samples.append(sample)
        
        return valid_samples
    
    def _save_training_data(self, samples: List[Dict]) -> str:
        """保存训练数据"""
        training_file = os.path.join(self.processed_dir, 'training_data_enhanced.txt')
        
        with open(training_file, 'w', encoding='utf-8') as f:
            for sample in samples:
                orig = sample['original'].replace('\t', ' ').replace('\r', '').replace('\n', ' ').strip()
                rew = sample['rewritten'].replace('\t', ' ').replace('\r', '').replace('\n', ' ').strip()
                
                # 限制长度
                if len(orig) > 2000:
                    orig = orig[:2000]
                if len(rew) > 2000:
                    rew = rew[:2000]
                
                # 构建丰富的上下文信息（JSON格式）
                context_info = {
                    'characters': sample.get('characters', []),
                    'emotion': sample.get('emotion', '中性'),
                    'writing_style': sample.get('writing_style', '平衡型'),
                    'tone': sample.get('tone', '中性'),
                    'personalities': sample.get('character_personalities', {}),
                    'speaking_styles': sample.get('character_speaking_styles', {})
                }
                context_str = json.dumps(context_info, ensure_ascii=False)
                
                # TSV格式：原始文本<TAB>改写文本<TAB>风格ID<TAB>上下文JSON
                f.write(f"{orig}\t{rew}\t{sample['style']}\t{context_str}\n")
        
        print(f"\n✅ 训练数据已保存: {training_file}")
        print(f"   样本数: {len(samples)}")
        
        return training_file

