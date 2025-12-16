#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爱下电子书网站适配器
"""

from typing import List, Dict
from bs4 import BeautifulSoup
import re
from .base_adapter import BaseSiteAdapter


class Ixdzs8Adapter(BaseSiteAdapter):
    """爱下电子书网站适配器"""
    
    # 分类映射（根据网站URL结构）
    CATEGORY_MAP = {
        '都市': '3',  # 都市青春
        '玄幻': '1',  # 玄幻奇幻
        '武侠': '2',  # 武侠小说
        '修真': '4',  # 修真仙侠
        '军事': '6',  # 军事历史
        '历史': '6',  # 军事历史
        '网游': '7',  # 网游竞技
        '竞技': '7',  # 网游竞技
        '科幻': '8',  # 科幻灵异
        '灵异': '8',  # 科幻灵异
        '言情': '9',  # 言情穿越
        '穿越': '9',  # 言情穿越
        '耽美': '10',  # 耽美同人
        '同人': '10',  # 耽美同人
        '台言': '11',  # 台言古言
        '古言': '11',  # 台言古言
    }
    
    def get_category_url(self, category: str) -> str:
        """获取分类页面URL"""
        # URL格式: https://ixdzs8.com/sort/分类ID/index-分类ID-状态-字数-排序.html
        # 状态: 0=全部, 1=连载中, 2=已完结
        # 字数: 0=全部, 1=30万字以下, 2=30-50万字, 3=50-100万字, 4=100万字以上
        # 排序: 0=最新, 1=最热
        category_id = self.CATEGORY_MAP.get(category, '3')
        # 默认：已完结、全部字数、按最新排序、第1页
        return f"{self.base_url}/sort/{category_id}/index-{category_id}-2-0-0.html"
    
    def parse_category_page(self, soup: BeautifulSoup, category: str) -> List[Dict]:
        """解析分类页面"""
        novels = []
        
        # 查找所有小说链接（格式：/read/数字ID/）
        novel_links = soup.find_all('a', href=re.compile(r'/read/\d+/$'))
        
        seen_novel_ids = set()
        
        for link in novel_links:
            href = link.get('href', '')
            title = link.get_text(strip=True)
            
            if not title or len(title) < 2:
                continue
            
            # 提取小说ID
            novel_id_match = re.search(r'/read/(\d+)/', href)
            if not novel_id_match:
                continue
            
            novel_id = novel_id_match.group(1)
            
            # 去重
            if novel_id in seen_novel_ids:
                continue
            seen_novel_ids.add(novel_id)
            
            # 构建完整URL
            url = self.normalize_url(href)
            
            # 查找父容器获取更多信息
            parent = link.parent
            author = '未知'
            is_completed = False
            
            # 向上查找包含完整信息的容器
            for _ in range(5):  # 最多向上查找5层
                if not parent or parent.name in ['body', 'html']:
                    break
                
                parent_text = parent.get_text()
                
                # 提取作者（通常在标题附近）
                # 尝试多种模式
                author_patterns = [
                    r'([^\s\n]+)\s+\d+\.\d+万字',  # 作者名 字数
                    r'作者[：:]\s*([^\s\n]+)',  # 作者：xxx
                    r'([^\s\n]+)\s+已完结',  # 作者名 已完结
                ]
                
                for pattern in author_patterns:
                    match = re.search(pattern, parent_text)
                    if match:
                        potential_author = match.group(1).strip()
                        # 过滤掉明显不是作者的内容
                        if len(potential_author) < 30 and not re.search(r'万字|完结|更新|章节', potential_author):
                            author = potential_author
                            break
                
                # 检查是否完结
                if not is_completed:
                    is_completed = self.check_completed(parent_text)
                
                # 如果找到了作者和状态，可以提前退出
                if author != '未知' and is_completed:
                    break
                
                parent = parent.parent
            
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
        
        # 从页面标题提取信息（格式：小说名_作者:作者名_爱下电子书）
        title_elem = soup.find('title')
        if title_elem:
            title_text = title_elem.get_text(strip=True)
            # 提取小说名和作者
            match = re.search(r'^([^_]+)_作者[：:]?([^_]+)_', title_text)
            if match:
                info['title'] = match.group(1).strip()
                info['author'] = match.group(2).strip()
            else:
                # 如果没有匹配到，尝试只提取标题
                title_match = re.search(r'^([^_]+)', title_text)
                if title_match:
                    info['title'] = title_match.group(1).strip()
        
        # 如果标题元素中没有找到，尝试从h1或其他元素提取
        if 'title' not in info:
            h1_elem = soup.select_one('h1')
            if h1_elem:
                info['title'] = h1_elem.get_text(strip=True)
        
        # 提取作者
        if 'author' not in info:
            page_text = soup.get_text()
            author_elem = soup.find(string=re.compile(r'作者[：:]'))
            if author_elem:
                parent = author_elem.parent
                if parent:
                    author_text = parent.get_text(strip=True)
                    author_match = re.search(r'作者[：:]\s*([^\s\n]+)', author_text)
                    if author_match:
                        info['author'] = author_match.group(1).strip()
        
        # 提取简介
        desc_patterns = [
            soup.find(string=re.compile(r'简介[：:]|内容简介[：:]')),
            soup.find(string=re.compile(r'作品简介')),
        ]
        
        for desc_elem in desc_patterns:
            if desc_elem:
                parent = desc_elem.parent
                if parent:
                    desc_text = parent.get_text()
                    desc_match = re.search(r'(?:简介|内容简介|作品简介)[：:]\s*(.+?)(?=\n\n|\n第|$)', desc_text, re.DOTALL)
                    if desc_match:
                        info['description'] = desc_match.group(1).strip()
                        break
        
        # 如果没有找到简介，尝试查找包含大量文本的div
        if 'description' not in info:
            desc_divs = soup.find_all('div', class_=re.compile(r'desc|intro|summary', re.I))
            for div in desc_divs:
                text = div.get_text(strip=True)
                if len(text) > 50:
                    info['description'] = text
                    break
        
        return info
    
    def extract_chapters(self, soup: BeautifulSoup) -> List[Dict]:
        """提取章节列表"""
        chapters = []
        
        # 章节链接格式：/read/数字ID/p章节号.html
        all_links = soup.find_all('a', href=re.compile(r'/read/\d+/p\d+\.html'))
        
        seen_chapter_nums = set()
        
        for link in all_links:
            href = link.get('href', '')
            title = link.get_text(strip=True)
            
            if not href or not title:
                continue
            
            # 提取章节号
            chapter_match = re.search(r'/p(\d+)\.html', href)
            if not chapter_match:
                continue
            
            chapter_num = chapter_match.group(1)
            
            # 去重
            if chapter_num in seen_chapter_nums:
                continue
            seen_chapter_nums.add(chapter_num)
            
            # 构建完整URL
            full_url = self.normalize_url(href)
            
            chapters.append({
                'title': title.strip(),
                'url': full_url
            })
        
        # 按章节号排序
        chapters.sort(key=lambda x: int(re.search(r'/p(\d+)\.html', x['url']).group(1)) if re.search(r'/p(\d+)\.html', x['url']) else 0)
        
        return chapters
    
    def extract_chapter_content(self, soup: BeautifulSoup) -> str:
        """提取章节内容"""
        # 尝试多种选择器
        content_selectors = [
            '#content', '.content',
            '#chaptercontent', '.chaptercontent',
            '#novelcontent', '.novelcontent',
            '#text', '.text',
            '#article', '.article',
            '#read', '.read',
            '#booktext', '.booktext',
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # 移除脚本和样式
                for script in content_elem(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                    script.decompose()
                
                text = content_elem.get_text(separator='\n', strip=True)
                if len(text) > 200:  # 确保内容足够长
                    # 清理多余空白
                    text = re.sub(r'\n{3,}', '\n\n', text)
                    return text.strip()
        
        # 如果没找到，尝试查找包含大量中文的div
        divs = soup.find_all('div')
        for div in divs:
            text = div.get_text(strip=True)
            # 如果文本长度超过500字符，且包含大量中文，可能是正文
            if len(text) > 500 and len(re.findall(r'[\u4e00-\u9fa5]', text)) > 100:
                # 移除脚本和样式
                for script in div(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                    script.decompose()
                
                text = div.get_text(separator='\n', strip=True)
                # 清理多余空白和常见广告文本
                text = re.sub(r'\n{3,}', '\n\n', text)
                text = re.sub(r'(点击|收藏|推荐|订阅|加入书架).*?$', '', text, flags=re.MULTILINE)
                text = re.sub(r'上一页.*?下一页.*?$', '', text, flags=re.MULTILINE)
                text = re.sub(r'目录.*?返回.*?$', '', text, flags=re.MULTILINE)
                
                return text.strip()
        
        return ''

