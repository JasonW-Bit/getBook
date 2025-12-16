#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人物关系图谱构建模块
分析小说中的人物关系，构建关系图谱
"""

import re
from typing import Dict, List, Set, Tuple
from collections import defaultdict, Counter


class RelationshipGraph:
    """人物关系图谱"""
    
    def __init__(self):
        self.characters = set()  # 人物集合
        self.relationships = defaultdict(dict)  # 关系字典 {char1: {char2: weight}}
        self.relationship_types = defaultdict(set)  # 关系类型 {char1: {char2: type}}
    
    def build_graph(self, content: str, characters: List[str]) -> Dict:
        """
        构建人物关系图谱
        
        Args:
            content: 小说内容
            characters: 人物列表
        
        Returns:
            关系图谱字典
        """
        self.characters = set(characters)
        
        print(f"📊 构建人物关系图谱（{len(self.characters)} 个人物）...")
        
        # 分析人物共现
        self._analyze_cooccurrence(content)
        
        # 分析关系类型
        self._analyze_relationship_types(content)
        
        # 计算关系强度
        self._calculate_relationship_strength()
        
        return {
            'characters': list(self.characters),
            'relationships': dict(self.relationships),
            'relationship_types': {k: list(v) for k, v in self.relationship_types.items()},
            'graph': self._build_graph_structure()
        }
    
    def _analyze_cooccurrence(self, content: str):
        """分析人物共现"""
        # 将内容分割成句子
        sentences = re.split(r'[。！？\n]', content)
        
        for sentence in sentences:
            # 查找句子中出现的人物
            chars_in_sentence = []
            for char in self.characters:
                if char in sentence:
                    chars_in_sentence.append(char)
            
            # 如果句子中有多个人物，建立关系
            if len(chars_in_sentence) > 1:
                for i, char1 in enumerate(chars_in_sentence):
                    for char2 in chars_in_sentence[i+1:]:
                        # 增加共现次数
                        if char2 not in self.relationships[char1]:
                            self.relationships[char1][char2] = 0
                        self.relationships[char1][char2] += 1
        
        print(f"   识别到 {sum(len(rels) for rels in self.relationships.values())} 对关系")
    
    def _analyze_relationship_types(self, content: str):
        """分析关系类型"""
        # 关系关键词模式
        relationship_patterns = {
            '朋友': [r'朋友', r'好友', r'伙伴', r'同伴'],
            '恋人': [r'恋人', r'爱人', r'喜欢', r'爱', r'情侣'],
            '敌人': [r'敌人', r'对手', r'仇人', r'恨', r'讨厌'],
            '家人': [r'父亲', r'母亲', r'兄弟', r'姐妹', r'儿子', r'女儿', r'家人'],
            '师徒': [r'师父', r'徒弟', r'老师', r'学生', r'师傅'],
            '上下级': [r'老板', r'上司', r'下属', r'领导', r'员工'],
        }
        
        # 查找包含两个人物的句子
        for char1 in self.characters:
            for char2 in self.characters:
                if char1 == char2:
                    continue
                
                # 查找同时包含两个人物的句子
                pattern = rf'{char1}.*?{char2}|{char2}.*?{char1}'
                matches = re.finditer(pattern, content[:50000])  # 分析前50000字符
                
                for match in matches:
                    sentence = match.group(0)
                    # 检查关系类型
                    for rel_type, patterns in relationship_patterns.items():
                        for p in patterns:
                            if re.search(p, sentence):
                                self.relationship_types[char1].add((char2, rel_type))
                                self.relationship_types[char2].add((char1, rel_type))
                                break
    
    def _calculate_relationship_strength(self):
        """计算关系强度"""
        # 归一化关系权重（0-1）
        max_weight = max(
            (max(rels.values()) if rels else 0)
            for rels in self.relationships.values()
        )
        
        if max_weight > 0:
            for char1 in self.relationships:
                for char2 in self.relationships[char1]:
                    self.relationships[char1][char2] = self.relationships[char1][char2] / max_weight
    
    def _build_graph_structure(self) -> Dict:
        """构建图谱结构（用于可视化）"""
        nodes = [{'id': char, 'label': char} for char in self.characters]
        edges = []
        
        for char1, rels in self.relationships.items():
            for char2, weight in rels.items():
                # 只保留权重较高的关系
                if weight > 0.1:
                    rel_type = None
                    if char1 in self.relationship_types:
                        for char, rtype in self.relationship_types[char1]:
                            if char == char2:
                                rel_type = rtype
                                break
                    
                    edges.append({
                        'source': char1,
                        'target': char2,
                        'weight': weight,
                        'type': rel_type or '未知'
                    })
        
        return {
            'nodes': nodes,
            'edges': edges
        }
    
    def get_related_characters(self, character: str, threshold: float = 0.1) -> List[Tuple[str, float]]:
        """
        获取与指定人物相关的人物列表
        
        Args:
            character: 人物名称
            threshold: 关系强度阈值
        
        Returns:
            [(人物, 关系强度), ...] 列表
        """
        if character not in self.relationships:
            return []
        
        related = [
            (char, weight)
            for char, weight in self.relationships[character].items()
            if weight >= threshold
        ]
        
        # 按关系强度排序
        related.sort(key=lambda x: x[1], reverse=True)
        
        return related
    
    def get_relationship_type(self, char1: str, char2: str) -> Optional[str]:
        """
        获取两个人物的关系类型
        
        Args:
            char1: 人物1
            char2: 人物2
        
        Returns:
            关系类型（如果存在）
        """
        if char1 in self.relationship_types:
            for char, rtype in self.relationship_types[char1]:
                if char == char2:
                    return rtype
        return None

