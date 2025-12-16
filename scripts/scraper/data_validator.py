#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据质量验证模块
用于检查爬取的数据是否符合要求
"""

import re
from typing import Dict, List, Tuple


class DataValidator:
    """数据质量验证器"""
    
    # 配置参数
    MIN_CONTENT_LENGTH = 200  # 最小内容长度（字符）
    MIN_CHINESE_CHARS = 100   # 最小中文字符数
    MIN_CHAPTER_COUNT = 1     # 最小章节数
    MIN_NOVEL_LENGTH = 1000   # 最小小说总长度（字符）
    
    # 不相关内容的模式
    IRRELEVANT_PATTERNS = [
        r'\d+\.\d+万字',           # 字数信息
        r'已完结|连载中',          # 状态信息
        r'作者[：:]',              # 作者信息（在内容中）
        r'点击|收藏|推荐|订阅|加入书架',  # 操作按钮
        r'上一页|下一页|目录|返回',  # 导航链接
        r'首页|上一章|下一章',      # 导航
    ]
    
    # 反爬虫检测关键词
    ANTI_CRAWL_KEYWORDS = [
        '正在验证浏览器',
        '验证',
        '安全验证',
        '请稍等',
        'challenge',
    ]
    
    @classmethod
    def validate_chapter_content(cls, content: str) -> Tuple[bool, str]:
        """
        验证章节内容
        
        Args:
            content: 章节内容
        
        Returns:
            (是否有效, 错误信息)
        """
        if not content:
            return False, "内容为空"
        
        # 检查反爬虫页面
        if any(keyword in content for keyword in cls.ANTI_CRAWL_KEYWORDS):
            return False, "检测到反爬虫页面"
        
        # 检查长度
        if len(content) < cls.MIN_CONTENT_LENGTH:
            return False, f"内容过短（{len(content)}字符，要求至少{cls.MIN_CONTENT_LENGTH}字符）"
        
        # 检查中文字符数
        chinese_chars = len(re.findall(r'[\u4e00-\u9fa5]', content))
        if chinese_chars < cls.MIN_CHINESE_CHARS:
            return False, f"中文字符数不足（{chinese_chars}个，要求至少{cls.MIN_CHINESE_CHARS}个）"
        
        # 检查不相关内容比例
        irrelevant_count = sum(1 for pattern in cls.IRRELEVANT_PATTERNS 
                              if re.search(pattern, content))
        if irrelevant_count > 3:  # 如果包含太多不相关内容模式
            return False, "包含过多不相关内容"
        
        return True, ""
    
    @classmethod
    def validate_novel(cls, novel_info: Dict) -> Tuple[bool, str, Dict]:
        """
        验证小说数据
        
        Args:
            novel_info: 小说信息字典
        
        Returns:
            (是否有效, 错误信息, 统计信息)
        """
        stats = {
            'total_chapters': 0,
            'valid_chapters': 0,
            'empty_chapters': 0,
            'total_chars': 0,
            'valid_chars': 0,
        }
        
        # 检查基本信息
        if not novel_info.get('title'):
            return False, "缺少标题", stats
        
        chapters = novel_info.get('chapters', [])
        stats['total_chapters'] = len(chapters)
        
        if len(chapters) < cls.MIN_CHAPTER_COUNT:
            return False, f"章节数不足（{len(chapters)}章，要求至少{cls.MIN_CHAPTER_COUNT}章）", stats
        
        # 验证每个章节
        valid_chapters = []
        for chapter in chapters:
            content = chapter.get('content', '')
            stats['total_chars'] += len(content)
            
            is_valid, error = cls.validate_chapter_content(content)
            if is_valid:
                valid_chapters.append(chapter)
                stats['valid_chapters'] += 1
                stats['valid_chars'] += len(content)
            else:
                stats['empty_chapters'] += 1
        
        # 检查有效章节数
        if stats['valid_chapters'] == 0:
            return False, "没有有效章节", stats
        
        # 检查总长度
        if stats['valid_chars'] < cls.MIN_NOVEL_LENGTH:
            return False, f"总长度不足（{stats['valid_chars']}字符，要求至少{cls.MIN_NOVEL_LENGTH}字符）", stats
        
        # 检查有效章节比例（至少50%的章节有效）
        valid_ratio = stats['valid_chapters'] / stats['total_chapters']
        if valid_ratio < 0.5:
            return False, f"有效章节比例过低（{valid_ratio*100:.1f}%，要求至少50%）", stats
        
        return True, "", stats
    
    @classmethod
    def clean_content(cls, content: str) -> str:
        """
        清理内容，移除不相关的数据
        
        Args:
            content: 原始内容
        
        Returns:
            清理后的内容
        """
        if not content:
            return ""
        
        # 移除多余空白
        content = re.sub(r'\n{3,}', '\n\n', content)
        content = re.sub(r'[ \t]+', ' ', content)
        
        # 移除重复的章节标题
        content = re.sub(r'^\s*第\d+章.*?$', '', content, flags=re.MULTILINE)
        
        # 按行过滤
        lines = content.split('\n')
        filtered_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 跳过明显不相关的行
            skip = False
            for pattern in cls.IRRELEVANT_PATTERNS:
                if re.search(pattern, line):
                    # 如果行很短且包含不相关内容，跳过
                    if len(line) < 100:
                        skip = True
                        break
            
            # 跳过导航链接
            if line in ['首页', '上一页', '下一页', '目录', '返回', '上一章', '下一章']:
                skip = True
            
            if not skip:
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    @classmethod
    def is_anti_crawl_page(cls, soup) -> bool:
        """
        检查是否是反爬虫页面
        
        Args:
            soup: BeautifulSoup对象
        
        Returns:
            是否是反爬虫页面
        """
        if not soup:
            return False
        
        # 检查标题
        title = soup.title.string if soup.title else ''
        if any(keyword in title for keyword in cls.ANTI_CRAWL_KEYWORDS):
            return True
        
        # 检查页面文本
        page_text = soup.get_text()
        if any(keyword in page_text[:500] for keyword in cls.ANTI_CRAWL_KEYWORDS):
            return True
        
        return False

