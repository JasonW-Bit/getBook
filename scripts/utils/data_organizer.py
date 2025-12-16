#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据整理工具
整理爬取的小说数据，准备用于训练
"""

import os
import re
import json
import shutil
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from collections import defaultdict


class DataOrganizer:
    """数据整理器"""
    
    def __init__(self, source_dir: str, target_dir: str = "data/training/processed"):
        """
        初始化数据整理器
        
        Args:
            source_dir: 源数据目录（爬取的小说文件）
            target_dir: 目标目录（整理后的数据）
        """
        self.source_dir = source_dir
        self.target_dir = target_dir
        os.makedirs(target_dir, exist_ok=True)
        
        # 统计数据
        self.stats = {
            'total_files': 0,
            'processed_files': 0,
            'failed_files': 0,
            'total_chapters': 0,
            'total_chars': 0,
            'by_category': defaultdict(int)
        }
    
    def clean_text(self, text: str) -> str:
        """
        清理文本（增强版）
        
        Args:
            text: 原始文本
        
        Returns:
            清理后的文本
        """
        if not text:
            return ""
        
        # 移除多余的空白（保留段落结构）
        text = re.sub(r'[ \t]+', ' ', text)  # 空格和制表符
        text = re.sub(r'\n{4,}', '\n\n\n', text)  # 过多换行
        
        # 移除广告和无关内容（更全面的模式）
        ad_patterns = [
            r'请收藏.*?网址',
            r'喜欢.*?请收藏',
            r'推荐.*?下载',
            r'【.*?】',  # 方括号内容
            r'\(.*?\)',  # 圆括号内容（但保留对话）
            r'www\.[^\s]+',  # 网址
            r'http[s]?://[^\s]+',  # HTTP链接
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # 邮箱
            r'QQ[：:：]?\d+',  # QQ号
            r'微信[：:：]?[^\s]+',  # 微信号
        ]
        for pattern in ad_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # 移除重复的章节标题
        text = re.sub(r'第\s*\d+\s*章[：:：]?\s*.*?\n.*?第\s*\d+\s*章', 
                     lambda m: m.group(0).split('\n')[-1], text)
        
        # 移除页眉页脚标记
        footer_patterns = [
            r'上一页.*?下一页',
            r'目录.*?返回',
            r'返回.*?目录',
            r'上一章.*?下一章',
        ]
        for pattern in footer_patterns:
            text = re.sub(pattern, '', text, flags=re.DOTALL)
        
        # 标准化标点符号
        text = re.sub(r'[，,]{2,}', '，', text)  # 多个逗号
        text = re.sub(r'[。.]{2,}', '。', text)  # 多个句号
        text = re.sub(r'[！!]{2,}', '！', text)  # 多个感叹号
        text = re.sub(r'[？?]{2,}', '？', text)  # 多个问号
        
        return text.strip()
    
    def extract_metadata(self, file_path: str) -> Dict:
        """
        从文件路径和内容提取元数据
        
        Args:
            file_path: 文件路径
        
        Returns:
            元数据字典
        """
        metadata = {
            'file': file_path,
            'title': '',
            'author': '',
            'category': '',
            'chapters': 0,
            'total_chars': 0,
            'quality_score': 0
        }
        
        # 从路径提取分类
        path_parts = Path(file_path).parts
        for part in path_parts:
            if part in ['都市', '玄幻', '言情', '武侠', '科幻', '悬疑', '历史', '军事']:
                metadata['category'] = part
                break
        
        # 从文件名提取标题
        filename = Path(file_path).stem
        metadata['title'] = filename
        
        # 读取文件内容
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取基本信息
            title_match = re.search(r'标题[：:：]?\s*(.+)', content)
            author_match = re.search(r'作者[：:：]?\s*(.+)', content)
            
            if title_match:
                metadata['title'] = title_match.group(1).strip()
            if author_match:
                metadata['author'] = author_match.group(1).strip()
            
            # 统计章节数
            chapters = re.findall(r'第\s*\d+\s*章', content)
            metadata['chapters'] = len(chapters)
            
            # 统计字符数
            metadata['total_chars'] = len(content)
            
            # 计算质量分数（基于章节数、字符数、完整性）
            quality = 0
            if metadata['chapters'] > 0:
                quality += 30
            if metadata['total_chars'] > 10000:
                quality += 30
            if metadata['total_chars'] > 100000:
                quality += 20
            if metadata['author']:
                quality += 10
            if metadata['title']:
                quality += 10
            
            metadata['quality_score'] = quality
            
        except Exception as e:
            print(f"⚠️  读取文件失败 {file_path}: {e}")
        
        return metadata
    
    def organize_by_category(self) -> Dict[str, List[Dict]]:
        """
        按分类整理数据
        
        Returns:
            按分类组织的数据字典
        """
        print(f"\n📁 开始整理数据...")
        print(f"   源目录: {self.source_dir}")
        print(f"   目标目录: {self.target_dir}")
        
        organized_data = defaultdict(list)
        
        # 遍历源目录
        for root, dirs, files in os.walk(self.source_dir):
            for file in files:
                if not file.endswith('.txt'):
                    continue
                
                file_path = os.path.join(root, file)
                self.stats['total_files'] += 1
                
                try:
                    # 提取元数据
                    metadata = self.extract_metadata(file_path)
                    
                    if not metadata.get('category'):
                        # 尝试从父目录推断
                        parent_dir = os.path.basename(os.path.dirname(file_path))
                        if parent_dir in ['都市', '玄幻', '言情', '武侠', '科幻', '悬疑']:
                            metadata['category'] = parent_dir
                        else:
                            metadata['category'] = '其他'
                    
                    # 读取并清理内容
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    cleaned_content = self.clean_text(content)
                    
                    # 保存到目标目录
                    category = metadata['category']
                    category_dir = os.path.join(self.target_dir, category)
                    os.makedirs(category_dir, exist_ok=True)
                    
                    # 保存清理后的文件
                    safe_title = re.sub(r'[<>:"/\\|?*]', '', metadata['title'] or file)
                    target_file = os.path.join(category_dir, f"{safe_title}.txt")
                    
                    with open(target_file, 'w', encoding='utf-8') as f:
                        f.write(cleaned_content)
                    
                    # 保存元数据
                    metadata_file = os.path.join(category_dir, f"{safe_title}.json")
                    with open(metadata_file, 'w', encoding='utf-8') as f:
                        json.dump(metadata, f, ensure_ascii=False, indent=2)
                    
                    organized_data[category].append(metadata)
                    self.stats['processed_files'] += 1
                    self.stats['total_chapters'] += metadata['chapters']
                    self.stats['total_chars'] += metadata['total_chars']
                    self.stats['by_category'][category] += 1
                    
                except Exception as e:
                    print(f"❌ 处理文件失败 {file_path}: {e}")
                    self.stats['failed_files'] += 1
        
        return dict(organized_data)
    
    def generate_summary(self, organized_data: Dict) -> Dict:
        """生成整理摘要"""
        summary = {
            'stats': dict(self.stats),
            'categories': {},
            'quality_distribution': {
                'high': 0,  # >= 80
                'medium': 0,  # 50-79
                'low': 0  # < 50
            }
        }
        
        for category, novels in organized_data.items():
            category_stats = {
                'count': len(novels),
                'total_chapters': sum(n['chapters'] for n in novels),
                'total_chars': sum(n['total_chars'] for n in novels),
                'avg_quality': sum(n['quality_score'] for n in novels) / len(novels) if novels else 0
            }
            summary['categories'][category] = category_stats
            
            # 质量分布
            for novel in novels:
                score = novel['quality_score']
                if score >= 80:
                    summary['quality_distribution']['high'] += 1
                elif score >= 50:
                    summary['quality_distribution']['medium'] += 1
                else:
                    summary['quality_distribution']['low'] += 1
        
        return summary
    
    def organize(self) -> Dict:
        """
        执行数据整理
        
        Returns:
            整理摘要
        """
        # 按分类整理
        organized_data = self.organize_by_category()
        
        # 生成摘要
        summary = self.generate_summary(organized_data)
        
        # 保存摘要
        summary_file = os.path.join(self.target_dir, 'organization_summary.json')
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        # 打印统计
        print(f"\n{'='*60}")
        print("📊 数据整理统计")
        print(f"{'='*60}")
        print(f"  总文件数: {self.stats['total_files']}")
        print(f"  成功处理: {self.stats['processed_files']}")
        print(f"  失败文件: {self.stats['failed_files']}")
        print(f"  总章节数: {self.stats['total_chapters']}")
        print(f"  总字符数: {self.stats['total_chars']:,}")
        print(f"\n  分类分布:")
        for category, count in self.stats['by_category'].items():
            print(f"    {category}: {count} 本")
        print(f"\n  质量分布:")
        print(f"    高质量 (>=80): {summary['quality_distribution']['high']} 本")
        print(f"    中等质量 (50-79): {summary['quality_distribution']['medium']} 本")
        print(f"    低质量 (<50): {summary['quality_distribution']['low']} 本")
        print(f"\n📁 整理后的数据保存在: {self.target_dir}")
        
        return summary


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='数据整理工具')
    parser.add_argument('source_dir', help='源数据目录')
    parser.add_argument('--target', '-t', default='data/training/processed',
                       help='目标目录（默认: data/training/processed）')
    
    args = parser.parse_args()
    
    organizer = DataOrganizer(args.source_dir, args.target)
    organizer.organize()


if __name__ == '__main__':
    main()

