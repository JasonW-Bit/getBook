#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网站适配器基类
所有网站适配器都应继承此类
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import re


class BaseSiteAdapter(ABC):
    """网站适配器基类"""
    
    def __init__(self, base_url: str):
        """
        初始化适配器
        
        Args:
            base_url: 网站基础URL
        """
        self.base_url = base_url.rstrip('/')
        self.site_name = self._extract_site_name(base_url)
    
    @staticmethod
    def _extract_site_name(url: str) -> str:
        """从URL提取网站名称"""
        import re
        match = re.search(r'://([^/]+)', url)
        if match:
            return match.group(1)
        return 'unknown'
    
    @abstractmethod
    def get_category_url(self, category: str) -> str:
        """
        获取分类页面URL
        
        Args:
            category: 小说类型（如：都市、玄幻等）
        
        Returns:
            分类页面URL
        """
        pass
    
    @abstractmethod
    def parse_category_page(self, soup: BeautifulSoup, category: str) -> List[Dict]:
        """
        解析分类页面，提取小说列表
        
        Args:
            soup: BeautifulSoup对象
            category: 小说类型
        
        Returns:
            小说列表，每个元素包含：title, url, author, completed等
        """
        pass
    
    @abstractmethod
    def extract_novel_info(self, soup: BeautifulSoup) -> Dict:
        """
        提取小说基本信息
        
        Args:
            soup: BeautifulSoup对象
        
        Returns:
            包含title, author, description等的字典
        """
        pass
    
    @abstractmethod
    def extract_chapters(self, soup: BeautifulSoup) -> List[Dict]:
        """
        提取章节列表
        
        Args:
            soup: BeautifulSoup对象
        
        Returns:
            章节列表，每个元素包含：title, url等
        """
        pass
    
    @abstractmethod
    def extract_chapter_content(self, soup: BeautifulSoup) -> str:
        """
        提取章节内容
        
        Args:
            soup: BeautifulSoup对象
        
        Returns:
            章节正文内容
        """
        pass
    
    def check_completed(self, text: str) -> bool:
        """
        检查是否已完结（通用方法，可被子类重写）
        
        Args:
            text: 要检查的文本
        
        Returns:
            是否已完结
        """
        completed_keywords = ['已完结', '完结', '完本', '全本', '已完本', 'completed', 'end']
        return any(keyword in text for keyword in completed_keywords)
    
    def normalize_url(self, url: str) -> str:
        """
        规范化URL（通用方法，可被子类重写）
        
        Args:
            url: 原始URL
        
        Returns:
            规范化后的URL
        """
        if url.startswith('http'):
            return url
        elif url.startswith('/'):
            return f"{self.base_url}{url}"
        else:
            return f"{self.base_url}/{url}"

