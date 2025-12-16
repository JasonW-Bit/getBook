#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫配置模块
统一管理爬虫的配置参数
"""

from typing import Dict, List


class ScraperConfig:
    """爬虫配置类"""
    
    # 请求配置
    DEFAULT_DELAY = 1.0  # 默认请求间隔（秒）
    MAX_DELAY = 5.0      # 最大请求间隔（秒）
    MIN_DELAY = 0.5      # 最小请求间隔（秒）
    REQUEST_TIMEOUT = 20  # 请求超时时间（秒）
    MAX_RETRY = 5        # 最大重试次数
    
    # 自适应延迟配置
    ADAPTIVE_DELAY_ENABLED = True  # 是否启用自适应延迟
    ERROR_THRESHOLD = 3            # 触发延迟增加的连续错误次数
    DELAY_INCREMENT = 0.5          # 每次增加的延迟（秒）
    
    # 内容验证配置
    MIN_CHAPTER_LENGTH = 200       # 最小章节长度（字符）
    MIN_CHINESE_CHARS = 100        # 最小中文字符数
    MAX_CONTENT_LENGTH = 50000     # 最大内容长度（字符，防止异常数据）
    
    # 进度保存配置
    PROGRESS_SAVE_INTERVAL = 10    # 每N章保存一次进度
    
    # 用户代理配置
    USER_AGENTS = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ]
    
    # 请求头配置
    DEFAULT_HEADERS = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',  # 移除br（Brotli），避免解压问题
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }
    
    # 错误处理配置
    RETRY_WAIT_BASE = 2           # 基础等待时间（秒）
    RETRY_WAIT_MAX = 30           # 最大等待时间（秒）
    EXPONENTIAL_BACKOFF = True    # 是否使用指数退避
    
    # 内容提取配置
    CONTENT_SELECTORS = [
        '#content', '.content',
        '#chaptercontent', '.chaptercontent',
        '#novelcontent', '.novelcontent',
        '#text', '.text',
        '#article', '.article',
        '#read', '.read',
        '#booktext', '.booktext',
        '#bookcontent', '.bookcontent',
    ]
    
    # 章节提取配置
    CHAPTER_PATTERNS = [
        r'第\s*\d+\s*章',
        r'第\s*[一二三四五六七八九十百千万]+\s*章',
        r'Chapter\s*\d+',
        r'CHAPTER\s*\d+',
    ]
    
    @classmethod
    def get_headers(cls, user_agent: str = None) -> Dict[str, str]:
        """
        获取请求头
        
        Args:
            user_agent: 自定义User-Agent，如果为None则使用默认
        
        Returns:
            请求头字典
        """
        headers = cls.DEFAULT_HEADERS.copy()
        if user_agent:
            headers['User-Agent'] = user_agent
        else:
            import random
            headers['User-Agent'] = random.choice(cls.USER_AGENTS)
        return headers
    
    @classmethod
    def calculate_retry_wait(cls, attempt: int) -> float:
        """
        计算重试等待时间
        
        Args:
            attempt: 重试次数（从0开始）
        
        Returns:
            等待时间（秒）
        """
        if cls.EXPONENTIAL_BACKOFF:
            wait_time = min(cls.RETRY_WAIT_BASE * (2 ** attempt), cls.RETRY_WAIT_MAX)
        else:
            wait_time = cls.RETRY_WAIT_BASE * (attempt + 1)
        return wait_time

