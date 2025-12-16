#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小说分析器
用于分析爬取的小说，提取特征用于训练
"""

import os
import re
import json
from typing import Dict, List, Optional
from collections import Counter, defaultdict
from pathlib import Path


class NovelAnalyzer:
    """小说分析器"""
    
    def __init__(self):
        self.analysis_results = []
    
    def analyze_novel(self, file_path: str) -> Dict:
        """
        分析单本小说
        
        Args:
            file_path: 小说文件路径
        
        Returns:
            分析结果字典
        """
        if not os.path.exists(file_path):
            return {}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取基本信息
        title_match = re.search(r'标题[：:：]?\s*(.+)', content)
        author_match = re.search(r'作者[：:：]?\s*(.+)', content)
        
        title = title_match.group(1).strip() if title_match else Path(file_path).stem
        author = author_match.group(1).strip() if author_match else '未知'
        
        # 分析文本特征
        analysis = {
            'file': file_path,
            'title': title,
            'author': author,
            'total_chars': len(content),
            'total_words': len(re.findall(r'\w+', content)),
            'total_chapters': len(re.findall(r'第\s*\d+\s*章', content)),
            'avg_chapter_length': 0,
            'dialogue_ratio': 0,
            'description_ratio': 0,
            'common_words': [],
            'writing_style': '未知',
            'genre_features': {}
        }
        
        # 计算平均章节长度
        chapters = re.split(r'第\s*\d+\s*章[：:：]?\s*.+?\n', content)
        if len(chapters) > 1:
            chapter_lengths = [len(ch) for ch in chapters[1:]]
            analysis['avg_chapter_length'] = sum(chapter_lengths) // len(chapter_lengths) if chapter_lengths else 0
        
        # 分析对话比例
        dialogue_pattern = r'["""](.*?)["""]'
        dialogues = re.findall(dialogue_pattern, content)
        dialogue_chars = sum(len(d) for d in dialogues)
        analysis['dialogue_ratio'] = dialogue_chars / len(content) if content else 0
        
        # 分析描写比例（包含"的"、"地"、"得"等描写性词汇）
        description_pattern = r'[的地得]'
        description_matches = len(re.findall(description_pattern, content))
        analysis['description_ratio'] = description_matches / len(content) if content else 0
        
        # 提取常见词汇
        words = re.findall(r'[\u4e00-\u9fa5]{2,}', content)
        word_counter = Counter(words)
        analysis['common_words'] = [word for word, count in word_counter.most_common(20)]
        
        # 判断写作风格
        if analysis['dialogue_ratio'] > 0.3:
            analysis['writing_style'] = '对话型'
        elif analysis['description_ratio'] > 0.15:
            analysis['writing_style'] = '描写型'
        elif analysis['avg_chapter_length'] > 3000:
            analysis['writing_style'] = '详细型'
        else:
            analysis['writing_style'] = '简洁型'
        
        # 类型特征
        genre_keywords = {
            '都市': ['都市', '城市', '公司', '职场', '商业'],
            '玄幻': ['修炼', '境界', '功法', '丹药', '宗门'],
            '言情': ['爱情', '恋爱', '结婚', '分手', '感情'],
            '武侠': ['武功', '江湖', '门派', '剑法', '内力'],
            '科幻': ['科技', '未来', '机器人', '太空', '星际'],
            '悬疑': ['案件', '推理', '线索', '真相', '凶手'],
        }
        
        for genre, keywords in genre_keywords.items():
            count = sum(content.count(kw) for kw in keywords)
            analysis['genre_features'][genre] = count
        
        return analysis
    
    def analyze_batch(self, directory: str) -> List[Dict]:
        """
        批量分析小说
        
        Args:
            directory: 小说目录
        
        Returns:
            分析结果列表
        """
        results = []
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.txt'):
                    file_path = os.path.join(root, file)
                    analysis = self.analyze_novel(file_path)
                    if analysis:
                        results.append(analysis)
        
        self.analysis_results = results
        return results
    
    def generate_summary(self) -> Dict:
        """生成分析摘要"""
        if not self.analysis_results:
            return {}
        
        total_novels = len(self.analysis_results)
        total_chars = sum(r['total_chars'] for r in self.analysis_results)
        total_chapters = sum(r['total_chapters'] for r in self.analysis_results)
        
        # 风格分布
        style_dist = Counter(r['writing_style'] for r in self.analysis_results)
        
        # 平均指标
        avg_chapter_length = sum(r['avg_chapter_length'] for r in self.analysis_results) // total_novels
        avg_dialogue_ratio = sum(r['dialogue_ratio'] for r in self.analysis_results) / total_novels
        
        summary = {
            'total_novels': total_novels,
            'total_chars': total_chars,
            'total_chapters': total_chapters,
            'avg_chapter_length': avg_chapter_length,
            'avg_dialogue_ratio': avg_dialogue_ratio,
            'writing_style_distribution': dict(style_dist),
            'top_authors': self._get_top_authors(),
            'common_words_all': self._get_common_words_all()
        }
        
        return summary
    
    def _get_top_authors(self, top_n: int = 10) -> List[tuple]:
        """获取最活跃的作者"""
        author_counter = Counter(r['author'] for r in self.analysis_results)
        return author_counter.most_common(top_n)
    
    def _get_common_words_all(self, top_n: int = 50) -> List[tuple]:
        """获取所有小说的常见词汇"""
        all_words = []
        for result in self.analysis_results:
            all_words.extend(result.get('common_words', []))
        word_counter = Counter(all_words)
        return word_counter.most_common(top_n)
    
    def save_analysis(self, output_file: str):
        """保存分析结果"""
        summary = self.generate_summary()
        
        output = {
            'summary': summary,
            'detailed_results': self.analysis_results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 分析结果已保存到: {output_file}")

