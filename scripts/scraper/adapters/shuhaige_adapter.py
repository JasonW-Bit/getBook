#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
书海阁网站适配器
"""

from typing import List, Dict
from bs4 import BeautifulSoup
import re
from .base_adapter import BaseSiteAdapter


class ShuhaigeAdapter(BaseSiteAdapter):
    """书海阁网站适配器"""
    
    # 分类映射（首字母大写格式）
    CATEGORY_MAP = {
        '都市': 'DuShi',
        '玄幻': 'XuanHuan',
        '言情': 'YanQing',
        '武侠': 'WuXia',
        '科幻': 'KeHuan',
        '悬疑': 'XuanYi',
        '历史': 'LiShi',
        '军事': 'JunShi',
        '游戏': 'YouXi',
        '竞技': 'JingJi',
        '仙侠': 'XianXia',
    }
    
    def get_category_url(self, category: str) -> str:
        """获取分类页面URL"""
        category_code = self.CATEGORY_MAP.get(category)
        if not category_code:
            # 如果没有映射，尝试首字母大写格式
            category_code = ''.join(word.capitalize() for word in category)
        return f"{self.base_url}/{category_code}/"
    
    def parse_category_page(self, soup: BeautifulSoup, category: str) -> List[Dict]:
        """解析分类页面"""
        novels = []
        
        # 查找小说列表容器
        novel_items = []
        
        # 方法1: 查找包含小说信息的列表项
        list_containers = soup.find_all(['ul', 'ol', 'div'], class_=re.compile(r'list|book|novel|item'))
        for container in list_containers:
            items = container.find_all(['li', 'div'], recursive=False)
            if items:
                novel_items.extend(items)
        
        # 方法2: 如果没找到，查找所有包含链接的列表项
        if not novel_items:
            all_lis = soup.find_all('li')
            for li in all_lis:
                links = li.find_all('a', href=True)
                if links:
                    for link in links:
                        href = link.get('href', '')
                        if re.search(r'/\d{4,}/', href) or 'novel' in href.lower() or 'book' in href.lower():
                            novel_items.append(li)
                            break
        
        # 方法3: 直接查找所有可能的小说链接
        if not novel_items:
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link.get('href', '')
                if re.search(r'/\d{4,}/$', href) and link.get_text(strip=True):
                    novel_items.append(link)
        
        # 提取小说信息
        seen_novel_ids = set()
        
        for item in novel_items:
            # 如果item本身就是链接，直接使用
            if item.name == 'a' and item.get('href'):
                link = item
                container = item.parent
            else:
                link = item.find('a', href=True)
                if not link:
                    continue
                container = item
            
            href = link.get('href', '')
            title = link.get_text(strip=True)
            
            # 如果链接文本为空，尝试从容器中提取标题
            if not title or len(title) < 2:
                if container:
                    container_text = container.get_text(strip=True)
                    title = container_text.split('\n')[0].strip()[:100]
                    if not title:
                        text_elem = container.find(string=True, recursive=False)
                        if text_elem:
                            title = str(text_elem).strip()[:100]
            
            # 处理特殊链接格式：/shu_数字.html -> /数字/
            if '/shu_' in href and href.endswith('.html'):
                id_match = re.search(r'/shu_(\d+)\.html', href)
                if id_match:
                    novel_id = id_match.group(1)
                    href = f'/{novel_id}/'
            
            if not href or not title or len(title) < 2:
                continue
            
            # 构建完整URL
            url = self.normalize_url(href)
            
            # 提取小说ID
            novel_id_match = re.search(r'/(\d{4,})/', url)
            if not novel_id_match:
                continue
            
            novel_id = novel_id_match.group(1)
            
            # 过滤掉章节链接
            if '.html' in url:
                continue
            
            # 去重
            if novel_id in seen_novel_ids:
                continue
            seen_novel_ids.add(novel_id)
            
            # 确保URL格式正确
            if not url.endswith('/'):
                url = url.rstrip('/') + '/'
            
            # 过滤掉明显不是小说的链接
            if any(skip in url.lower() for skip in ['login', 'register', 'search', 'category', 'list', 'sort', 'tag']):
                continue
            
            # 检查是否已完结
            is_completed = False
            item_text = item.get_text()
            
            # 查找父元素和兄弟元素
            parent = item.parent
            if parent:
                parent_text = parent.get_text()
                item_text += ' ' + parent_text
                for sibling in list(parent.next_siblings)[:3] + list(parent.previous_siblings)[:3]:
                    if hasattr(sibling, 'get_text'):
                        item_text += ' ' + sibling.get_text()
            
            is_completed = self.check_completed(item_text)
            
            # 提取作者
            author = '未知'
            author_elem = item.find(string=re.compile(r'作者[：:]'))
            if author_elem:
                author_text = author_elem.parent.get_text() if author_elem.parent else ''
                author_match = re.search(r'作者[：:]\s*([^\s\n]+)', author_text)
                if author_match:
                    author = author_match.group(1).strip()
            
            novels.append({
                'title': title,
                'url': url,
                'category': category,
                'author': author,
                'completed': is_completed,
                'novel_id': novel_id
            })
            
            if len(novels) >= 200:
                break
        
        return novels
    
    def extract_novel_info(self, soup: BeautifulSoup) -> Dict:
        """提取小说基本信息"""
        info = {}
        
        # 提取标题
        title_elem = soup.select_one('h1')
        if title_elem:
            title_text = title_elem.get_text(strip=True)
            title_text = re.sub(r'\s*列表\s*$', '', title_text)
            info['title'] = title_text
        
        # 提取作者
        page_text = soup.get_text()
        author_elem = soup.find(string=re.compile(r'作者[：:]'))
        if author_elem:
            parent = author_elem.parent
            if parent:
                author_text = parent.get_text(strip=True)
                author_match = re.search(r'作者[：:]\s*([^\s\n]+?)(?=\s*(?:都市|已完结|最新章节|万字|最后更新|\d+章))', author_text)
                if author_match:
                    author_name = author_match.group(1).strip()
                    author_name = re.sub(r'[：:\s]+$', '', author_name)
                    if author_name and len(author_name) < 30:
                        info['author'] = author_name
        
        # 提取简介
        desc_elem = soup.find(string=re.compile(r'简介[：:]|内容简介[：:]'))
        if desc_elem:
            parent = desc_elem.parent
            if parent:
                desc_text = parent.get_text()
                desc_match = re.search(r'(?:简介|内容简介)[：:]\s*(.+?)(?=\n\n|\n第|$)', desc_text, re.DOTALL)
                if desc_match:
                    info['description'] = desc_match.group(1).strip()
        
        return info
    
    def extract_chapters(self, soup: BeautifulSoup) -> List[Dict]:
        """提取章节列表"""
        chapters = []
        
        # 书海阁的章节链接格式通常是 /数字ID/章节号
        all_links = soup.select('a[href]')
        base_path = self.base_url.split('/')[-1] if '/' in self.base_url else ''
        
        for link in all_links:
            href = link.get('href', '')
            title = link.get_text(strip=True)
            
            if href and title:
                # 检查是否是章节链接
                if re.search(r'第\d+章', title):
                    full_url = self.normalize_url(href)
                    if base_path in href or href.startswith('/'):
                        chapters.append({
                            'title': title.strip(),
                            'url': full_url
                        })
                # 也匹配数字开头的链接
                elif re.match(r'^\d+[\.、]', title) and base_path in href:
                    full_url = self.normalize_url(href)
                    chapters.append({
                        'title': title.strip(),
                        'url': full_url
                    })
        
        return chapters
    
    def extract_chapter_content(self, soup: BeautifulSoup) -> str:
        """提取章节内容"""
        # 查找内容容器（常见的类名）
        content_selectors = [
            '#content', '.content', '#chaptercontent', '.chaptercontent',
            '#novelcontent', '.novelcontent', '#text', '.text'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                content = content_elem.get_text(separator='\n', strip=True)
                if len(content) > 100:  # 确保内容足够长
                    return content
        
        # 如果没找到，尝试查找包含大量文本的div
        divs = soup.find_all('div')
        for div in divs:
            text = div.get_text(strip=True)
            # 如果文本长度超过500字符，且包含中文，可能是正文
            if len(text) > 500 and re.search(r'[\u4e00-\u9fa5]', text):
                # 移除可能的广告和无关内容
                lines = text.split('\n')
                content_lines = [line.strip() for line in lines if len(line.strip()) > 10]
                return '\n'.join(content_lines)
        
        return ""
    
    def check_completed(self, text: str) -> bool:
        """
        检查是否已完结（书海阁专用，更严格的检测）
        
        Args:
            text: 要检查的文本
        
        Returns:
            是否已完结
        """
        if not text:
            return False
        
        # 更严格的完结关键词匹配
        completed_patterns = [
            r'已完结',
            r'完结',
            r'完本',
            r'全本',
            r'已完本',
            r'大结局',
            r'全文完',
            r'全书完',
            r'完$',
        ]
        
        # 连载中的关键词（如果出现这些，说明未完结）
        ongoing_patterns = [
            r'连载中',
            r'更新中',
            r'连载',
            r'未完',
            r'未完结',
            r'持续更新',
        ]
        
        text_lower = text.lower()
        
        # 先检查是否有连载标识
        for pattern in ongoing_patterns:
            if re.search(pattern, text):
                return False
        
        # 检查是否有完结标识
        for pattern in completed_patterns:
            if re.search(pattern, text):
                return True
        
        return False

