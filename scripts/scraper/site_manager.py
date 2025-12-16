#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网站管理器
负责管理多个网站的适配器，支持自动发现和解析
"""

import os
import json
import re
from typing import Dict, List, Optional
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests

from adapters import get_adapter, list_adapters, ADAPTERS
from adapters.base_adapter import BaseSiteAdapter


class SiteManager:
    """网站管理器"""
    
    def __init__(self, config_dir: str = "data/sites"):
        """
        初始化网站管理器
        
        Args:
            config_dir: 网站配置目录
        """
        self.config_dir = config_dir
        self.config_file = os.path.join(config_dir, 'sites.json')
        self.sites_config = self._load_config()
        
        # 创建配置目录
        os.makedirs(config_dir, exist_ok=True)
    
    def _load_config(self) -> Dict:
        """加载网站配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_config(self):
        """保存网站配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.sites_config, f, ensure_ascii=False, indent=2)
    
    def get_site_name(self, url: str) -> str:
        """从URL提取网站名称"""
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path.split('/')[0]
        # 移除www.前缀
        domain = re.sub(r'^www\.', '', domain)
        return domain
    
    def register_site(self, url: str, adapter_name: Optional[str] = None) -> Dict:
        """
        注册网站（如果已有适配器则直接使用，否则尝试自动解析）
        
        Args:
            url: 网站URL
            adapter_name: 适配器名称（可选）
        
        Returns:
            网站配置信息
        """
        site_name = self.get_site_name(url)
        
        # 检查是否已注册
        if site_name in self.sites_config:
            print(f"✅ 网站 {site_name} 已注册")
            return self.sites_config[site_name]
        
        # 检查是否有现成的适配器
        adapter_class = get_adapter(site_name)
        if adapter_class:
            print(f"✅ 找到适配器: {site_name}")
            config = {
                'url': url,
                'adapter': site_name,
                'status': 'ready',
                'categories': []
            }
            self.sites_config[site_name] = config
            self._save_config()
            return config
        
        # 如果没有适配器，尝试自动解析
        print(f"🔍 未找到适配器，尝试自动解析网站: {site_name}")
        config = self._auto_discover_site(url, site_name)
        
        if config:
            self.sites_config[site_name] = config
            self._save_config()
            return config
        else:
            print(f"⚠️  无法自动解析网站，请手动创建适配器")
            return None
    
    def _auto_discover_site(self, url: str, site_name: str) -> Optional[Dict]:
        """
        自动发现网站结构
        
        Args:
            url: 网站URL
            site_name: 网站名称
        
        Returns:
            网站配置信息
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = response.apparent_encoding or 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 尝试查找分类链接
            categories = self._discover_categories(soup, url)
            
            # 尝试查找小说链接格式
            novel_pattern = self._discover_novel_pattern(soup)
            
            config = {
                'url': url,
                'adapter': None,  # 需要手动创建适配器
                'status': 'discovered',
                'categories': categories,
                'novel_pattern': novel_pattern,
                'discovery_info': {
                    'title': soup.title.string if soup.title else None,
                    'links_count': len(soup.find_all('a')),
                }
            }
            
            print(f"✅ 自动发现完成:")
            print(f"   找到 {len(categories)} 个可能的分类")
            print(f"   小说链接模式: {novel_pattern}")
            
            return config
            
        except Exception as e:
            print(f"❌ 自动发现失败: {e}")
            return None
    
    def _discover_categories(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """发现网站的分类"""
        categories = []
        
        # 查找可能包含分类的链接
        links = soup.find_all('a', href=True)
        category_keywords = ['都市', '玄幻', '言情', '武侠', '科幻', '悬疑', '历史', '军事']
        
        for link in links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # 检查链接文本或URL中是否包含分类关键词
            for keyword in category_keywords:
                if keyword in text or keyword in href:
                    if href not in categories:
                        categories.append(keyword)
                        break
        
        return list(set(categories))  # 去重
    
    def _discover_novel_pattern(self, soup: BeautifulSoup) -> str:
        """发现小说链接的模式"""
        links = soup.find_all('a', href=True)
        
        # 查找包含数字的链接（可能是小说链接）
        patterns = []
        for link in links[:50]:  # 只检查前50个链接
            href = link.get('href', '')
            if re.search(r'/\d{4,}/', href):
                patterns.append('数字ID格式: /数字ID/')
                break
            elif re.search(r'/novel/', href):
                patterns.append('novel格式: /novel/...')
                break
            elif re.search(r'/book/', href):
                patterns.append('book格式: /book/...')
                break
        
        return patterns[0] if patterns else '未知'
    
    def get_adapter_for_site(self, site_name: str) -> Optional[BaseSiteAdapter]:
        """
        获取网站的适配器实例
        
        Args:
            site_name: 网站名称
        
        Returns:
            适配器实例
        """
        config = self.sites_config.get(site_name)
        if not config:
            return None
        
        adapter_name = config.get('adapter')
        if not adapter_name:
            return None
        
        adapter_class = get_adapter(adapter_name)
        if not adapter_class:
            return None
        
        base_url = config.get('url')
        return adapter_class(base_url)
    
    def list_sites(self) -> List[Dict]:
        """列出所有已注册的网站"""
        return [
            {
                'name': name,
                'url': config.get('url'),
                'status': config.get('status', 'unknown'),
                'adapter': config.get('adapter'),
                'categories': config.get('categories', [])
            }
            for name, config in self.sites_config.items()
        ]

