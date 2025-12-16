#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小说爬取脚本
支持爬取小说的简介、章节列表和章节内容
"""

import requests
from bs4 import BeautifulSoup
import os
import time
import re
from urllib.parse import urljoin, urlparse
import json
from typing import List, Dict, Optional

# 导入配置模块
try:
    from .scraper_config import ScraperConfig
except ImportError:
    from scraper_config import ScraperConfig


class NovelScraper:
    """小说爬取类"""
    
    # 常量定义（使用配置模块的值）
    PROGRESS_SAVE_INTERVAL = ScraperConfig.PROGRESS_SAVE_INTERVAL
    MIN_CONTENT_LENGTH = ScraperConfig.MIN_CHAPTER_LENGTH
    
    def __init__(self, base_url: str, delay: float = 1.0, adaptive_delay: bool = True, output_dir: str = 'novels'):
        """
        初始化爬虫
        
        Args:
            base_url: 小说主页URL
            delay: 请求间隔时间（秒），避免请求过快
            adaptive_delay: 是否启用自适应延迟（遇到502等错误时自动增加延迟）
            output_dir: 输出文件夹名称，默认为'novels'
        """
        self.base_url = base_url
        self.delay = delay
        self.base_delay = delay  # 保存基础延迟
        self.adaptive_delay = adaptive_delay
        self.consecutive_errors = 0  # 连续错误计数
        self.base_output_dir = output_dir  # 基础输出文件夹
        self.novel_output_dir = None  # 小说专用文件夹（在获取标题后创建）
        
        # 创建基础输出文件夹
        if not os.path.exists(self.base_output_dir):
            os.makedirs(self.base_output_dir)
            print(f"📁 创建输出文件夹: {self.base_output_dir}/")
        
        self.session = requests.Session()
        # 使用配置模块的请求头
        self.session.headers.update(ScraperConfig.get_headers())
        
        self.novel_info = {
            'title': '',
            'author': '',
            'description': '',
            'chapters': []
        }
    
    def get_page(self, url: str, retry: int = 5, silent: bool = False) -> Optional[BeautifulSoup]:
        """
        获取网页内容
        
        Args:
            url: 网页URL
            retry: 重试次数（默认5次，对502等服务器错误更有效）
            silent: 是否静默模式（不打印错误信息）
            
        Returns:
            BeautifulSoup对象或None
        """
        for i in range(retry):
            try:
                time.sleep(self.delay)
                response = self.session.get(url, timeout=ScraperConfig.REQUEST_TIMEOUT)
                
                if response.status_code == 200:
                    # 设置编码
                    response.encoding = response.apparent_encoding or 'utf-8'
                    
                    # 检查响应内容是否有效
                    if len(response.text) < 100:
                        # 响应内容太短，可能是压缩问题，尝试重新获取
                        if not silent:
                            print(f"⚠️  响应内容异常，尝试重新获取...")
                        # 移除Accept-Encoding中的br（Brotli），某些服务器不支持
                        original_encoding = self.session.headers.get('Accept-Encoding', '')
                        self.session.headers['Accept-Encoding'] = 'gzip, deflate'
                        response = self.session.get(url, timeout=20)
                        response.encoding = response.apparent_encoding or 'utf-8'
                        # 恢复原始编码设置
                        self.session.headers['Accept-Encoding'] = original_encoding
                    
                    # 成功请求，重置连续错误计数
                    if self.consecutive_errors > 0:
                        self.consecutive_errors = 0
                        # 如果延迟被增加，逐渐恢复
                        if self.delay > self.base_delay:
                            self.delay = max(self.base_delay, self.delay - 0.1)
                    return BeautifulSoup(response.text, 'html.parser')
                elif response.status_code >= 500:
                    # 5xx服务器错误（如502 Bad Gateway, 503 Service Unavailable）
                    # 使用配置的退避策略
                    wait_time = ScraperConfig.calculate_retry_wait(i)
                    if not silent:
                        print(f"\n⚠️  服务器错误 {response.status_code}，等待 {wait_time} 秒后重试... ({i+1}/{retry})")
                    
                    # 如果启用自适应延迟，遇到服务器错误时增加基础延迟
                    if self.adaptive_delay and ScraperConfig.ADAPTIVE_DELAY_ENABLED and i == 0:
                        self.consecutive_errors += 1
                        # 根据配置调整延迟
                        if self.consecutive_errors >= ScraperConfig.ERROR_THRESHOLD:
                            increment = (self.consecutive_errors // ScraperConfig.ERROR_THRESHOLD) * ScraperConfig.DELAY_INCREMENT
                            self.delay = min(self.base_delay + increment, ScraperConfig.MAX_DELAY)
                            if not silent:
                                print(f"   自动调整延迟至 {self.delay:.1f} 秒（连续错误 {self.consecutive_errors} 次）")
                    
                    if i < retry - 1:
                        time.sleep(wait_time)
                        continue
                elif response.status_code == 404:
                    # 404错误通常不会恢复，直接返回
                    if not silent:
                        print(f"\n❌ 页面不存在 (404): {url}")
                    return None
                else:
                    # 其他HTTP错误
                    if not silent:
                        print(f"\n⚠️  请求失败，状态码: {response.status_code} - {url}")
                    if i < retry - 1:
                        time.sleep(2 * (i + 1))
                        
            except requests.exceptions.Timeout:
                wait_time = ScraperConfig.calculate_retry_wait(i)
                if not silent:
                    print(f"\n⏱️  请求超时，等待 {wait_time} 秒后重试... ({i+1}/{retry})")
                if i < retry - 1:
                    time.sleep(wait_time)
            except requests.exceptions.ConnectionError as e:
                wait_time = ScraperConfig.calculate_retry_wait(i)
                if not silent:
                    print(f"\n🔌 连接错误，等待 {wait_time} 秒后重试... ({i+1}/{retry})")
                if i < retry - 1:
                    time.sleep(wait_time)
            except Exception as e:
                wait_time = ScraperConfig.calculate_retry_wait(i)
                if not silent and i == retry - 1:
                    print(f"\n❌ 请求出错: {e} - {url}")
                if i < retry - 1:
                    time.sleep(wait_time)
        
        if not silent:
            print(f"\n❌ 经过 {retry} 次重试后仍然失败: {url}")
        return None
    
    def extract_novel_info(self, soup: BeautifulSoup) -> Dict:
        """
        提取小说基本信息（标题、作者、简介）
        需要根据具体网站结构调整选择器
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            包含小说信息的字典
        """
        info = {}
        
        # 针对书海阁网站的特殊处理
        if 'shuhaige.net' in self.base_url:
            # 提取标题（通常在h1中，但可能包含其他文本）
            title_elem = soup.select_one('h1')
            if title_elem:
                title_text = title_elem.get_text(strip=True)
                # 清理标题，移除"列表"等后缀
                title_text = re.sub(r'\s*列表\s*$', '', title_text)
                info['title'] = title_text
            
            # 提取作者（更精确的匹配）
            page_text = soup.get_text()
            
            # 方法1: 从HTML结构中提取（更准确）
            author_elem = soup.find(string=re.compile(r'作者[：:]'))
            if author_elem:
                parent = author_elem.parent
                if parent:
                    author_text = parent.get_text(strip=True)
                    # 提取"作者：xxx"中的xxx部分，在遇到"都市"、"已完结"等词之前停止
                    author_match = re.search(r'作者[：:]\s*([^\s\n]+?)(?=\s*(?:都市|已完结|最新章节|万字|最后更新|\d+章))', author_text)
                    if author_match:
                        author_name = author_match.group(1).strip()
                        # 清理可能的额外字符
                        author_name = re.sub(r'[：:\s]+$', '', author_name)
                        if author_name and len(author_name) < 30:  # 作者名不应该太长
                            info['author'] = author_name
            
            # 方法2: 如果上面没找到，从页面文本中精确提取
            if not info.get('author'):
                # 尝试匹配"作者：xxx"格式，在遇到特定关键词之前停止
                author_match = re.search(r'作者[：:]\s*([^\s\n]+?)(?=\s*(?:都市|已完结|最新章节|万字|最后更新|\d+章))', page_text)
                if not author_match:
                    # 更宽松的匹配，但限制长度
                    author_match = re.search(r'作者[：:]\s*([^\n]{1,20}?)(?=\s|$)', page_text)
                if author_match:
                    author_text = author_match.group(1).strip()
                    # 清理可能的额外字符
                    author_text = re.sub(r'[：:\s]+$', '', author_text)
                    if author_text and len(author_text) < 30:  # 作者名不应该太长
                        info['author'] = author_text
            
            # 提取其他信息（类型、状态、字数等）
            type_match = re.search(r'([^已完结]+)\s*已完结', page_text)
            if type_match:
                info['category'] = type_match.group(1).strip()
            
            word_match = re.search(r'(\d+)\s*万字', page_text)
            if word_match:
                info['word_count'] = word_match.group(1) + '万字'
            
            chapter_match = re.search(r'共\s*(\d+)\s*章', page_text)
            if chapter_match:
                info['total_chapters'] = int(chapter_match.group(1))
        
        # 通用选择器（适用于其他网站）
        if not info.get('title'):
            title_selectors = [
                'h1',
                '.book-title',
                '#book-title',
                'title',
                '.novel-title',
                'h2.title'
            ]
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    info['title'] = title_elem.get_text(strip=True)
                    break
        
        if not info.get('author'):
            author_selectors = [
                '.author',
                '#author',
                '.book-author',
                'span.author',
                'a[href*="author"]'
            ]
            for selector in author_selectors:
                author_elem = soup.select_one(selector)
                if author_elem:
                    info['author'] = author_elem.get_text(strip=True)
                    break
        
        if not info.get('description'):
            desc_selectors = [
                '.description',
                '#description',
                '.book-intro',
                '.intro',
                '.summary',
                'div[class*="intro"]',
                'div[class*="desc"]'
            ]
            for selector in desc_selectors:
                desc_elem = soup.select_one(selector)
                if desc_elem:
                    info['description'] = desc_elem.get_text(strip=True)
                    break
        
        return info
    
    def extract_chapters(self, soup: BeautifulSoup) -> List[Dict]:
        """
        提取章节列表
        需要根据具体网站结构调整选择器
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            章节列表，每个章节包含标题和链接
        """
        chapters = []
        
        # 针对书海阁网站的特殊处理
        if 'shuhaige.net' in self.base_url:
            # 书海阁的章节链接格式通常是 /350415/章节号
            # 查找所有章节链接
            all_links = soup.select('a[href]')
            base_path = urlparse(self.base_url).path.rstrip('/')
            base_id = base_path.split('/')[-1] if base_path else ''
            
            for link in all_links:
                href = link.get('href', '')
                title = link.get_text(strip=True)
                
                # 匹配章节链接
                if href and title:
                    # 检查是否是章节链接（包含"第X章"格式）
                    if re.search(r'第\d+章', title):
                        full_url = urljoin(self.base_url, href)
                        # 确保URL包含书籍ID（如350415）
                        if base_id in href or base_path in href or href.startswith('/'):
                            chapters.append({
                                'title': title.strip(),
                                'url': full_url
                            })
                    # 也匹配数字开头的链接（如 "1. 章节名"）
                    elif re.match(r'^\d+[\.、]', title) and base_id in href:
                        full_url = urljoin(self.base_url, href)
                        chapters.append({
                            'title': title.strip(),
                            'url': full_url
                        })
            
            # 如果找到了章节，去重并排序
            if chapters:
                # 去重（基于URL）
                seen_urls = set()
                unique_chapters = []
                for ch in chapters:
                    if ch['url'] not in seen_urls:
                        seen_urls.add(ch['url'])
                        unique_chapters.append(ch)
                
                # 尝试按章节号排序
                def get_chapter_num(title):
                    match = re.search(r'第(\d+)章', title)
                    if match:
                        return int(match.group(1))
                    match = re.search(r'^(\d+)\.', title)
                    if match:
                        return int(match.group(1))
                    return 0
                
                unique_chapters.sort(key=lambda x: get_chapter_num(x['title']))
                return unique_chapters
        
        # 通用选择器（适用于其他网站）
        chapter_selectors = [
            'a[href*="chapter"]',
            'a[href*="book"]',
            '.chapter-list a',
            '#chapter-list a',
            '.chapter a',
            'dd a',
            'li a[href*="/"]'
        ]
        
        for selector in chapter_selectors:
            chapter_links = soup.select(selector)
            if chapter_links and len(chapter_links) > 5:  # 至少要有几个章节链接
                for link in chapter_links:
                    href = link.get('href', '')
                    title = link.get_text(strip=True)
                    if href and title:
                        full_url = urljoin(self.base_url, href)
                        chapters.append({
                            'title': title,
                            'url': full_url
                        })
                if chapters:
                    break
        
        return chapters
    
    def extract_all_chapters_with_pagination(self, soup: BeautifulSoup) -> List[Dict]:
        """
        提取所有章节（包括分页）
        针对书海阁等有分页的网站
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            所有章节列表
        """
        all_chapters = []
        
        # 针对书海阁网站
        if 'shuhaige.net' in self.base_url:
            # 先提取当前页的章节
            current_chapters = self.extract_chapters(soup)
            all_chapters.extend(current_chapters)
            
            # 查找分页链接（如：第51-100章、第101-150章等）
            pagination_links = soup.select('a[href]')
            base_path = urlparse(self.base_url).path.rstrip('/')
            base_id = base_path.split('/')[-1] if base_path else ''
            
            # 提取所有分页URL
            page_urls = set()
            page_text = soup.get_text()
            
            # 首先尝试从页面文本中提取总章节数
            total_match = re.search(r'共\s*(\d+)\s*章', page_text)
            total_chapters = 0
            if total_match:
                total_chapters = int(total_match.group(1))
            
            # 方法1: 从链接中提取所有分页链接
            for link in pagination_links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                # 匹配分页链接（如：第51-100章、第51 - 100章等）
                page_match = re.search(r'第(\d+)\s*-\s*(\d+)章', text)
                if page_match or re.match(r'^\d+\s*-\s*\d+$', text):
                    full_url = urljoin(self.base_url, href)
                    # 确保是同一本书的分页
                    if base_id in full_url or base_path in full_url or base_id in href or href.startswith('/'):
                        page_urls.add(full_url)
            
            # 方法2: 如果找到了总章节数但分页链接不够，尝试生成
            if total_chapters > 0 and len(page_urls) < 5:
                # 假设每页50章（根据实际观察）
                pages = (total_chapters + 49) // 50
                base_url_no_slash = self.base_url.rstrip('/')
                
                print(f"检测到共 {total_chapters} 章，预计 {pages} 页，尝试生成分页URL...")
                
                # 先测试一个分页URL格式（只测试一次，避免浪费请求）
                test_page = 2
                test_urls = [
                    f"{base_url_no_slash}?page={test_page}",
                    f"{base_url_no_slash}/page/{test_page}",
                    f"{base_url_no_slash}?p={test_page}",
                ]
                
                valid_format = None
                for test_url in test_urls:
                    test_soup = self.get_page(test_url)
                    if test_soup:
                        test_chapters = self.extract_chapters(test_soup)
                        if test_chapters and len(test_chapters) > 0:
                            # 找到有效格式
                            if '?page=' in test_url:
                                valid_format = f"{base_url_no_slash}?page={{}}"
                            elif '/page/' in test_url:
                                valid_format = f"{base_url_no_slash}/page/{{}}"
                            elif '?p=' in test_url:
                                valid_format = f"{base_url_no_slash}?p={{}}"
                            break
                    # 如果这个格式无效，立即尝试下一个，不等待
                
                # 如果找到有效格式，生成所有分页（包括第一页）
                if valid_format:
                    for p in range(1, pages + 1):
                        page_urls.add(valid_format.format(p))
                    print(f"✅ 成功生成 {len(page_urls)} 个分页URL")
                else:
                    print("⚠️  警告: 无法确定分页URL格式，将只爬取当前页的章节")
            
            # 访问每个分页
            print(f"发现 {len(page_urls)} 个分页，开始提取...")
            for i, page_url in enumerate(sorted(page_urls), 1):
                print(f"  正在提取第 {i}/{len(page_urls)} 页...")
                page_soup = self.get_page(page_url)
                if page_soup:
                    page_chapters = self.extract_chapters(page_soup)
                    all_chapters.extend(page_chapters)
            
            # 去重并排序
            if all_chapters:
                seen_urls = set()
                unique_chapters = []
                for ch in all_chapters:
                    if ch['url'] not in seen_urls:
                        seen_urls.add(ch['url'])
                        unique_chapters.append(ch)
                
                def get_chapter_num(title):
                    match = re.search(r'第(\d+)章', title)
                    if match:
                        return int(match.group(1))
                    match = re.search(r'^(\d+)\.', title)
                    if match:
                        return int(match.group(1))
                    return 0
                
                unique_chapters.sort(key=lambda x: get_chapter_num(x['title']))
                return unique_chapters
        
        return all_chapters
    
    def extract_chapter_content(self, soup: BeautifulSoup) -> str:
        """
        提取章节正文内容
        需要根据具体网站结构调整选择器
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            章节正文内容
        """
        # 针对书海阁网站的特殊处理
        if 'shuhaige.net' in self.base_url:
            # 尝试多种可能的内容选择器
            content_selectors = [
                '#content',
                '.content',
                '#chaptercontent',
                '.chaptercontent',
                '#chapterContent',
                '.chapterContent',
                'div[id*="content"]',
                'div[class*="content"]',
                'div[class*="text"]',
                'div[id*="text"]'
            ]
            
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # 移除脚本、样式和广告
                    for tag in content_elem(["script", "style", "noscript"]):
                        tag.decompose()
                    
                    # 移除可能的广告和导航元素
                    for ad in content_elem.select('.ad, .advertisement, .ads, [class*="ad"]'):
                        ad.decompose()
                    
                    text = content_elem.get_text(separator='\n', strip=True)
                    # 清理多余空行和特殊字符
                    text = re.sub(r'\n{3,}', '\n\n', text)
                    text = re.sub(r'^\s*', '', text, flags=re.MULTILINE)
                    
                    # 移除可能的网站标识文本和无关内容
                    text = re.sub(r'书海阁.*?$', '', text, flags=re.MULTILINE)
                    text = re.sub(r'www\.shuhaige\.net.*?$', '', text, flags=re.MULTILINE)
                    text = re.sub(r'手机阅读.*?$', '', text, flags=re.MULTILINE)
                    text = re.sub(r'返回书页.*?$', '', text, flags=re.MULTILINE)
                    text = re.sub(r'上一章.*?下一章.*?$', '', text, flags=re.MULTILINE)
                    text = re.sub(r'^\s*第\d+章.*?$', '', text, flags=re.MULTILINE)  # 移除重复的章节标题
                    
                    # 移除常见的广告和导航文本
                    text = re.sub(r'(点击|收藏|推荐|订阅|加入书架).*?$', '', text, flags=re.MULTILINE)
                    
                    # 移除可能的章节导航链接文本
                    text = re.sub(r'上一页.*?下一页.*?$', '', text, flags=re.MULTILINE)
                    text = re.sub(r'目录.*?返回.*?$', '', text, flags=re.MULTILINE)
                    
                    if len(text) > 50:  # 内容应该有一定长度
                        return text.strip()
            
            # 如果上述选择器都不行，尝试提取body中的主要文本
            body = soup.select_one('body')
            if body:
                # 移除导航、页眉、页脚等
                for tag in body.select('header, footer, nav, .header, .footer, .nav'):
                    tag.decompose()
                
                text = body.get_text(separator='\n', strip=True)
                text = re.sub(r'\n{3,}', '\n\n', text)
                if len(text) > 100:
                    return text.strip()
        
        # 通用选择器（适用于其他网站）
        content_selectors = [
            '#content',
            '.content',
            '.chapter-content',
            '#chapter-content',
            '.text-content',
            '#text-content',
            '.novel-content',
            'div[class*="content"]',
            'div[class*="text"]',
            'div[id*="content"]'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # 移除脚本和样式标签
                for script in content_elem(["script", "style"]):
                    script.decompose()
                
                text = content_elem.get_text(separator='\n', strip=True)
                # 清理多余空行
                text = re.sub(r'\n{3,}', '\n\n', text)
                if len(text) > 100:  # 内容应该有一定长度
                    return text
        
        return ""
    
    def scrape_novel(self) -> Dict:
        """
        爬取完整小说
        
        Returns:
            包含小说完整信息的字典
        """
        print(f"开始爬取小说: {self.base_url}")
        
        # 获取主页
        soup = self.get_page(self.base_url)
        if not soup:
            print("无法获取小说主页")
            return self.novel_info
        
        # 提取基本信息
        print("提取小说基本信息...")
        info = self.extract_novel_info(soup)
        self.novel_info.update(info)
        print(f"标题: {self.novel_info.get('title', '未知')}")
        print(f"作者: {self.novel_info.get('author', '未知')}")
        
        # 提取章节列表（包括分页）
        print("提取章节列表...")
        if 'shuhaige.net' in self.base_url:
            # 对于书海阁，使用支持分页的方法
            chapters = self.extract_all_chapters_with_pagination(soup)
        else:
            chapters = self.extract_chapters(soup)
        
        if not chapters:
            # 如果主页没有章节列表，可能需要访问目录页
            # 尝试查找目录页链接
            catalog_links = soup.select('a[href*="catalog"], a[href*="index"], a[href*="list"], a[href*="chapter"]')
            for link in catalog_links:
                href = link.get('href', '')
                if 'catalog' in href.lower() or 'index' in href.lower() or 'list' in href.lower():
                    catalog_url = urljoin(self.base_url, href)
                    print(f"尝试访问目录页: {catalog_url}")
                    catalog_soup = self.get_page(catalog_url)
                    if catalog_soup:
                        if 'shuhaige.net' in self.base_url:
                            chapters = self.extract_all_chapters_with_pagination(catalog_soup)
                        else:
                            chapters = self.extract_chapters(catalog_soup)
                        if chapters:
                            break
        
        if not chapters:
            print("警告: 未找到章节列表，请检查网站结构或手动指定章节选择器")
            return self.novel_info
        
        print(f"找到 {len(chapters)} 个章节")
        
        # 检查是否有保存的进度文件（保存在小说文件夹中）
        # 如果novel_output_dir还未创建（可能是从进度文件恢复），使用title_safe
        if not self.novel_output_dir:
            title_safe = re.sub(r'[<>:"/\\|?*]', '', self.novel_info.get('title', 'novel'))
            self.novel_output_dir = os.path.join(self.base_output_dir, title_safe)
            # 确保文件夹存在
            if not os.path.exists(self.novel_output_dir):
                os.makedirs(self.novel_output_dir)
        
        progress_file = os.path.join(self.novel_output_dir, f".{os.path.basename(self.novel_output_dir)}_progress.json")
        saved_progress = None
        start_index = 0
        
        if os.path.exists(progress_file):
            try:
                with open(progress_file, 'r', encoding='utf-8') as f:
                    saved_progress = json.load(f)
                saved_count = len(saved_progress.get('chapters', []))
                if saved_count > 0:
                    print(f"发现进度文件，已爬取 {saved_count} 章")
                    # 检查是否在交互式环境
                    try:
                        import sys
                        if sys.stdin.isatty():
                            resume = input("是否继续之前的进度？(y/n，默认y): ").strip().lower()
                        else:
                            resume = 'y'  # 非交互环境默认继续
                    except (EOFError, KeyboardInterrupt):
                        resume = 'y'  # 出错时默认继续
                    
                    if resume != 'n':
                        self.novel_info['chapters'] = saved_progress.get('chapters', [])
                        start_index = len(self.novel_info['chapters'])
                        print(f"从第 {start_index + 1} 章开始继续爬取...")
                    else:
                        self.novel_info['chapters'] = []
                        start_index = 0
                        # 删除旧的进度文件
                        try:
                            os.remove(progress_file)
                        except (OSError, FileNotFoundError):
                            pass  # 文件不存在或无法删除，继续执行
                else:
                    self.novel_info['chapters'] = []
                    start_index = 0
            except Exception as e:
                print(f"读取进度文件失败: {e}，将重新开始")
                self.novel_info['chapters'] = []
                start_index = 0
        else:
            self.novel_info['chapters'] = []
            start_index = 0
        
        # 爬取每个章节的内容
        total = len(chapters)
        failed_chapters = []  # 完全失败的章节
        empty_chapters = []   # 内容为空的章节
        error_stats = {}      # 错误统计（按错误类型）
        start_time = time.time()
        
        for i, chapter in enumerate(chapters[start_index:], start_index + 1):
            # 显示进度（带时间估算）
            progress = (i / total) * 100
            bar_length = 40
            filled = int(bar_length * i / total)
            bar = '=' * filled + '-' * (bar_length - filled)
            
            # 计算剩余时间
            elapsed = time.time() - start_time
            if i > start_index + 1:
                avg_time = elapsed / (i - start_index)
                remaining = avg_time * (total - i)
                eta_str = f"剩余: {int(remaining//60)}分{int(remaining%60)}秒"
            else:
                eta_str = "计算中..."
            
            chapter_title = chapter['title'][:25] + '...' if len(chapter['title']) > 25 else chapter['title']
            print(f"\r[{bar}] {i}/{total} ({progress:.1f}%) | {eta_str} | {chapter_title}", end='', flush=True)
            
            # 尝试爬取章节内容（get_page内部已有重试机制，这里只做内容验证）
            content = ''
            error_type = None
            
            # 先尝试获取页面（静默模式，避免正常情况下的噪音）
            # 如果失败，会在统计信息中显示
            chapter_soup = self.get_page(chapter['url'], retry=5, silent=True)
            
            if chapter_soup:
                # 检查是否是反爬虫页面（延迟导入避免循环依赖）
                try:
                    from .data_validator import DataValidator
                except ImportError:
                    from data_validator import DataValidator
                
                if DataValidator.is_anti_crawl_page(chapter_soup):
                    error_type = '反爬虫页面'
                    empty_chapters.append(chapter['title'])
                    content = ''
                else:
                    content = self.extract_chapter_content(chapter_soup)
                    # 验证内容质量
                    is_valid, error_msg = DataValidator.validate_chapter_content(content)
                    if is_valid:
                        # 清理内容
                        content = DataValidator.clean_content(content)
                    else:
                        error_type = error_msg
                        empty_chapters.append(chapter['title'])
                        content = ''  # 无效内容不保存
            else:
                # 页面获取失败（可能是502、503等服务器错误）
                error_type = '页面获取失败'
                failed_chapters.append(chapter['title'])
            
            # 统计错误类型
            if error_type:
                error_stats[error_type] = error_stats.get(error_type, 0) + 1
            
            # 保存章节（无论成功与否都保存，方便后续处理）
            self.novel_info['chapters'].append({
                'title': chapter['title'],
                'url': chapter['url'],
                'content': content if content else '',
                'error': error_type if error_type else None
            })
            
            # 每N章保存一次进度（静默保存，不显示错误）
            if i % self.PROGRESS_SAVE_INTERVAL == 0:
                try:
                    with open(progress_file, 'w', encoding='utf-8') as f:
                        json.dump(self.novel_info, f, ensure_ascii=False, indent=2)
                except (OSError, IOError, PermissionError):
                    pass  # 静默失败，不影响主流程
        
        print()  # 换行
        
        # 显示统计信息
        total_time = time.time() - start_time
        success_count = len([c for c in self.novel_info['chapters'] if c.get('content')])
        print(f"\n✅ 爬取完成！")
        print(f"   成功: {success_count}/{total} 章 ({success_count/total*100:.1f}%)")
        
        # 显示详细错误统计
        if failed_chapters or empty_chapters or error_stats:
            print(f"\n⚠️  错误统计:")
            if failed_chapters:
                print(f"   页面获取失败: {len(failed_chapters)} 章")
                if len(failed_chapters) <= 5:
                    for ch in failed_chapters:
                        print(f"     - {ch}")
                else:
                    for ch in failed_chapters[:5]:
                        print(f"     - {ch}")
                    print(f"     ... 还有 {len(failed_chapters) - 5} 章失败")
            
            if empty_chapters:
                print(f"   内容为空/过短: {len(empty_chapters)} 章")
                if len(empty_chapters) <= 3:
                    for ch in empty_chapters:
                        print(f"     - {ch}")
                else:
                    for ch in empty_chapters[:3]:
                        print(f"     - {ch}")
                    print(f"     ... 还有 {len(empty_chapters) - 3} 章")
            
            if error_stats:
                print(f"   错误类型分布:")
                for err_type, count in error_stats.items():
                    print(f"     - {err_type}: {count} 次")
        
        # 计算总字数
        total_content_length = sum(len(ch.get('content', '')) for ch in self.novel_info['chapters'])
        
        print(f"\n   总耗时: {int(total_time//60)}分{int(total_time%60)}秒")
        print(f"   平均速度: {total/(total_time/60):.1f} 章/分钟")
        if total_content_length > 0:
            word_count_mb = total_content_length / (1024 * 1024)
            print(f"   总字数: {total_content_length:,} 字 ({word_count_mb:.2f} MB)")
        
        # 清理进度文件（爬取成功后删除）
        if os.path.exists(progress_file):
            try:
                os.remove(progress_file)
                print(f"   已清理进度文件")
            except (OSError, FileNotFoundError, PermissionError):
                pass  # 文件不存在或无法删除，静默失败
        
        return self.novel_info
    
    def save_to_txt(self, filename: Optional[str] = None):
        """
        保存为TXT文件到输出文件夹
        
        Args:
            filename: 输出文件名，默认为小说标题.txt（会自动保存到输出文件夹）
        """
        if not filename:
            title = self.novel_info.get('title', 'novel')
            # 清理文件名中的非法字符
            filename = re.sub(r'[<>:"/\\|?*]', '', title) + '.txt'
        
        # 确保文件名在小说文件夹中
        if not self.novel_output_dir:
            # 如果文件夹还未创建，使用标题创建
            title = self.novel_info.get('title', 'novel')
            title_safe = re.sub(r'[<>:"/\\|?*]', '', title)
            self.novel_output_dir = os.path.join(self.base_output_dir, title_safe)
            if not os.path.exists(self.novel_output_dir):
                os.makedirs(self.novel_output_dir)
        
        if not os.path.dirname(filename):
            filepath = os.path.join(self.novel_output_dir, filename)
        else:
            filepath = filename
        
        print(f"\n💾 正在保存TXT文件...")
        with open(filepath, 'w', encoding='utf-8') as f:
            # 写入基本信息
            f.write(f"标题: {self.novel_info.get('title', '未知')}\n")
            f.write(f"作者: {self.novel_info.get('author', '未知')}\n")
            f.write(f"\n简介:\n{self.novel_info.get('description', '无')}\n")
            f.write("\n" + "="*50 + "\n\n")
            
            # 写入章节内容
            total_chapters = len(self.novel_info['chapters'])
            for i, chapter in enumerate(self.novel_info['chapters'], 1):
                f.write(f"\n第 {i} 章: {chapter['title']}\n")
                f.write("="*50 + "\n\n")
                content = chapter.get('content', '')
                if content:
                    f.write(content + "\n\n")
                else:
                    f.write(f"[内容获取失败: {chapter.get('error', '未知错误')}]\n\n")
                
                # 每100章显示一次保存进度
                if i % 100 == 0:
                    print(f"  已保存 {i}/{total_chapters} 章...", end='\r', flush=True)
        
        # 获取文件大小
        file_size = os.path.getsize(filepath)
        size_mb = file_size / (1024 * 1024)
        print(f"\n✅ 小说已保存到: {filepath}")
        print(f"   文件大小: {size_mb:.2f} MB")
    
    def save_to_json(self, filename: Optional[str] = None):
        """
        保存为JSON文件到小说文件夹
        
        Args:
            filename: 输出文件名，默认为小说标题.json（会自动保存到小说文件夹）
        """
        if not filename:
            title = self.novel_info.get('title', 'novel')
            filename = re.sub(r'[<>:"/\\|?*]', '', title) + '.json'
        
        # 确保文件名在小说文件夹中
        if not self.novel_output_dir:
            # 如果文件夹还未创建，使用标题创建
            title = self.novel_info.get('title', 'novel')
            title_safe = re.sub(r'[<>:"/\\|?*]', '', title)
            self.novel_output_dir = os.path.join(self.base_output_dir, title_safe)
            if not os.path.exists(self.novel_output_dir):
                os.makedirs(self.novel_output_dir)
        
        if not os.path.dirname(filename):
            filepath = os.path.join(self.novel_output_dir, filename)
        else:
            filepath = filename
        
        print(f"\n💾 正在保存JSON文件...")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.novel_info, f, ensure_ascii=False, indent=2)
        
        # 获取文件大小
        file_size = os.path.getsize(filepath)
        size_mb = file_size / (1024 * 1024)
        print(f"✅ 小说数据已保存到: {filepath}")
        print(f"   文件大小: {size_mb:.2f} MB")


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法: python3 novel_scraper.py <小说URL>")
        print("示例: python3 novel_scraper.py https://m.shuhaige.net/350415/")
        print("\n说明: 默认保存为TXT格式，如需JSON格式可在URL后添加 'json'")
        print("示例: python3 novel_scraper.py https://m.shuhaige.net/350415/ json")
        sys.exit(1)
    
    url = sys.argv[1]
    # 检查第二个参数是否是输出格式，否则默认为txt
    output_format = 'txt'
    if len(sys.argv) > 2:
        if sys.argv[2].lower() in ['json', 'txt']:
            output_format = sys.argv[2].lower()
        else:
            print(f"警告: 未知的输出格式 '{sys.argv[2]}'，将使用默认的TXT格式")
    
    # 创建爬虫实例
    scraper = NovelScraper(url, delay=1.0)
    
    # 爬取小说
    novel_info = scraper.scrape_novel()
    
    # 保存结果
    if output_format == 'json':
        scraper.save_to_json()
    else:
        scraper.save_to_txt()
    
    print("\n✅ 全部完成！")


if __name__ == '__main__':
    main()

