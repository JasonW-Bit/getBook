#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多网站批量爬取器
支持多个网站，自动选择适配器或解析网站结构
"""

import os
import sys
import json
import time
import re
import argparse
import shutil
from typing import List, Dict, Optional
from pathlib import Path

# 导入适配器和网站管理器
sys.path.insert(0, os.path.dirname(__file__))
from site_manager import SiteManager
from adapters.base_adapter import BaseSiteAdapter
from novel_scraper import NovelScraper
from novel_analyzer import NovelAnalyzer
from data_validator import DataValidator


class MultiSiteScraper:
    """多网站批量爬取器"""
    
    def __init__(self, output_base_dir: str = "data/training"):
        """
        初始化多网站爬取器
        
        Args:
            output_base_dir: 输出基础目录
        """
        self.output_base_dir = output_base_dir
        self.site_manager = SiteManager()
        self.analyzer = NovelAnalyzer()
        
        # 创建输出目录
        os.makedirs(output_base_dir, exist_ok=True)
        
        # 统计信息
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'total_chapters': 0,
            'total_chars': 0,
            'sites': {}
        }
        
        self.scraped_novels = []
        self.failed_novels = []
    
    def register_site(self, url: str) -> Dict:
        """
        注册网站
        
        Args:
            url: 网站URL
        
        Returns:
            网站配置信息
        """
        return self.site_manager.register_site(url)
    
    def get_category_list(self, site_name: str, category: str, filter_completed: bool = True) -> List[Dict]:
        """
        获取指定网站和类型的小说列表
        
        Args:
            site_name: 网站名称
            category: 小说类型
            filter_completed: 是否只获取已完结的小说
        
        Returns:
            小说列表
        """
        print(f"\n📚 正在获取 {site_name} 的 {category} 类型小说列表...")
        if filter_completed:
            print(f"   🔍 筛选条件: 仅已完结")
        
        # 获取适配器
        adapter = self.site_manager.get_adapter_for_site(site_name)
        if not adapter:
            print(f"❌ 无法获取适配器，请先注册网站")
            return []
        
        # 获取分类页面URL
        category_url = adapter.get_category_url(category)
        print(f"   🔗 分类页面: {category_url}")
        
        # 获取分类页面
        try:
            scraper = NovelScraper(category_url, delay=1.5, output_dir=self.output_base_dir)
            soup = scraper.get_page(category_url, silent=False)
            if not soup:
                print(f"❌ 无法获取分类页面")
                return []
        except Exception as e:
            print(f"❌ 获取分类页面失败: {e}")
            return []
        
        # 解析分类页面
        novels = adapter.parse_category_page(soup, category)
        
        # 筛选已完结
        if filter_completed:
            # 先检查列表页是否有完结标识
            completed_count = sum(1 for n in novels if n.get('completed', False))
            
            print(f"   📊 列表页检测到 {completed_count} 本标记为已完结的小说")
            
            # 如果列表页没有完结标识或数量不足，访问小说页面详细检查
            if completed_count == 0 or completed_count < len(novels) * 0.3:
                print(f"   ⚠️  列表页完结标识不足，访问小说详情页进行详细检查...")
                checked_novels = []
                check_count = min(len(novels), 50)  # 检查前50本
                
                for i, novel in enumerate(novels[:check_count], 1):
                    try:
                        novel_url = novel['url']
                        print(f"   🔍 [{i}/{check_count}] 检查: {novel.get('title', '未知')[:30]}...", end=' ')
                        
                        temp_scraper = NovelScraper(novel_url, delay=0.8, output_dir=self.output_base_dir)
                        novel_soup = temp_scraper.get_page(novel_url, silent=True)
                        
                        try:
                            if novel_soup:
                                novel_text = novel_soup.get_text()
                                
                                # 方法1: 检查页面文本中的完结标识
                                is_completed = adapter.check_completed(novel_text)
                                
                                # 方法2: 如果方法1未检测到，检查最后一章标题
                                if not is_completed:
                                    # 尝试提取章节列表，检查最后一章
                                    try:
                                        chapters = adapter.extract_chapters(novel_soup)
                                        if chapters:
                                            last_chapter = chapters[-1]
                                            last_chapter_title = last_chapter.get('title', '')
                                            # 检查最后一章是否包含完结标识
                                            if adapter.check_completed(last_chapter_title):
                                                is_completed = True
                                            
                                            # 如果最后一章标题包含"大结局"、"完"等，也认为是完结
                                            if re.search(r'大结局|全文完|全书完|完$', last_chapter_title):
                                                is_completed = True
                                    except:
                                        pass
                                
                                if is_completed:
                                    novel['completed'] = True
                                    checked_novels.append(novel)
                                    print("✅ 已完结")
                                else:
                                    print("❌ 未完结")
                            else:
                                print("⚠️  无法获取页面")
                        finally:
                            # 清理临时scraper的session
                            if hasattr(temp_scraper, 'session'):
                                try:
                                    temp_scraper.session.close()
                                except:
                                    pass
                    except Exception as e:
                        print(f"❌ 检查失败: {str(e)[:30]}")
                        # 确保清理临时scraper
                        if 'temp_scraper' in locals() and hasattr(temp_scraper, 'session'):
                            try:
                                temp_scraper.session.close()
                            except:
                                pass
                        continue
                
                novels = checked_novels
                print(f"   ✅ 详细检查完成，找到 {len(checked_novels)} 本已完结小说")
            else:
                # 如果列表页有足够的完结标识，直接筛选，但也要验证一下
                print(f"   ✅ 列表页有足够的完结标识，直接筛选...")
                novels = [n for n in novels if n.get('completed', False)]
                
                # 对筛选结果进行二次验证（随机抽查几本）
                if len(novels) > 0:
                    import random
                    sample_size = min(3, len(novels))
                    sample_novels = random.sample(novels, sample_size)
                    print(f"   🔍 随机抽查 {sample_size} 本进行验证...")
                    
                    verified_count = 0
                    for novel in sample_novels:
                        try:
                            novel_url = novel['url']
                            temp_scraper = NovelScraper(novel_url, delay=0.5, output_dir=self.output_base_dir)
                            novel_soup = temp_scraper.get_page(novel_url, silent=True)
                            if novel_soup:
                                novel_text = novel_soup.get_text()
                                if adapter.check_completed(novel_text):
                                    verified_count += 1
                        except:
                            pass
                    
                    if verified_count < sample_size * 0.5:
                        print(f"   ⚠️  验证通过率较低 ({verified_count}/{sample_size})，建议使用详细检查模式")
        
        print(f"✅ 找到 {len(novels)} 本 {category} 类型的小说" + 
              (f"（已筛选：仅已完结）" if filter_completed else ""))
        
        return novels
    
    def scrape_novel(self, site_name: str, novel_info: Dict) -> bool:
        """
        爬取单本小说
        
        Args:
            site_name: 网站名称
            novel_info: 小说信息
        
        Returns:
            是否成功
        """
        url = novel_info['url']
        title = novel_info['title']
        category = novel_info.get('category', '未知')
        
        print(f"\n{'='*60}")
        print(f"📖 正在爬取: {title}")
        print(f"   网站: {site_name}")
        print(f"   类型: {category}")
        print(f"   URL: {url}")
        print(f"{'='*60}")
        
        try:
            # 创建输出目录：data/training/novels/网站名/类型/小说名/
            # 先使用临时目录让NovelScraper爬取
            temp_dir = os.path.join(self.output_base_dir, 'novels', site_name, category, '.temp')
            os.makedirs(temp_dir, exist_ok=True)
            
            # 使用NovelScraper爬取
            scraper = NovelScraper(url, delay=1.5, output_dir=temp_dir)
            novel_info_dict = scraper.scrape_novel()
            
            if novel_info_dict and novel_info_dict.get('title'):
                # 获取实际标题
                actual_title = novel_info_dict.get('title', title)
                safe_title = re.sub(r'[<>:"/\\|?*]', '', actual_title)
                
                # 创建最终目录：网站名/类型/小说名/
                novel_dir = os.path.join(self.output_base_dir, 'novels', site_name, category, safe_title)
                os.makedirs(novel_dir, exist_ok=True)
                
                # 确定文件路径
                txt_file = os.path.join(novel_dir, f"{safe_title}.txt")
                json_file = os.path.join(novel_dir, f"{safe_title}.json")
                
                # 查找NovelScraper保存的文件
                source_txt = None
                source_json = None
                
                # 检查NovelScraper创建的子文件夹
                if hasattr(scraper, 'novel_output_dir') and scraper.novel_output_dir:
                    potential_txt = os.path.join(scraper.novel_output_dir, f"{safe_title}.txt")
                    potential_json = os.path.join(scraper.novel_output_dir, f"{safe_title}.json")
                    if os.path.exists(potential_txt):
                        source_txt = potential_txt
                    if os.path.exists(potential_json):
                        source_json = potential_json
                
                # 如果没找到，在temp_dir中查找
                if not source_txt:
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            if file.endswith('.txt') and safe_title in file:
                                source_txt = os.path.join(root, file)
                                break
                        if source_txt:
                            break
                
                # 移动或复制文件到最终位置
                if source_txt and os.path.exists(source_txt) and source_txt != txt_file:
                    try:
                        shutil.move(source_txt, txt_file)
                    except (OSError, IOError, PermissionError):
                        # 如果移动失败，尝试复制
                        try:
                            shutil.copy2(source_txt, txt_file)
                        except (OSError, IOError, PermissionError):
                            print(f"⚠️  无法移动或复制文件: {source_txt}")
                elif not os.path.exists(txt_file):
                    # 如果文件不存在，手动保存
                    content = self._extract_full_content(novel_info_dict)
                    if content:
                        with open(txt_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                
                if source_json and os.path.exists(source_json) and source_json != json_file:
                    shutil.move(source_json, json_file)
                
                # 保存TXT（如果还没有保存）
                if not os.path.exists(txt_file):
                    try:
                        scraper.save_to_txt()
                        # 移动文件到正确位置
                        if hasattr(scraper, 'novel_output_dir') and scraper.novel_output_dir:
                            source_file = os.path.join(scraper.novel_output_dir, f"{safe_title}.txt")
                            if os.path.exists(source_file) and source_file != txt_file:
                                try:
                                    shutil.move(source_file, txt_file)
                                except (OSError, IOError, PermissionError):
                                    try:
                                        shutil.copy2(source_file, txt_file)
                                    except (OSError, IOError, PermissionError):
                                        print(f"⚠️  无法移动或复制文件: {source_file}")
                    except (OSError, IOError, PermissionError) as e:
                        # 手动保存
                        content = self._extract_full_content(novel_info_dict)
                        if content:
                            try:
                                with open(txt_file, 'w', encoding='utf-8') as f:
                                    f.write(content)
                            except (OSError, IOError, PermissionError):
                                print(f"⚠️  无法保存文件: {txt_file}")
                
                # 数据质量验证
                is_valid, error_msg, validation_stats = DataValidator.validate_novel(novel_info_dict)
                
                if not is_valid:
                    print(f"⚠️  数据质量检查未通过: {error_msg}")
                    print(f"   统计: 总章节{validation_stats['total_chapters']}, "
                          f"有效章节{validation_stats['valid_chapters']}, "
                          f"空章节{validation_stats['empty_chapters']}, "
                          f"总字符{validation_stats['total_chars']}, "
                          f"有效字符{validation_stats['valid_chars']}")
                    
                    # 删除已创建的文件和目录
                    if os.path.exists(txt_file):
                        try:
                            os.remove(txt_file)
                        except (OSError, PermissionError):
                            pass
                    if os.path.exists(json_file):
                        try:
                            os.remove(json_file)
                        except (OSError, PermissionError):
                            pass
                    if os.path.exists(novel_dir):
                        try:
                            shutil.rmtree(novel_dir)
                        except (OSError, PermissionError):
                            pass  # 静默失败，不影响主流程
                    
                    self.failed_novels.append(novel_info)
                    self.stats['failed'] += 1
                    if site_name not in self.stats['sites']:
                        self.stats['sites'][site_name] = {'success': 0, 'failed': 0}
                    self.stats['sites'][site_name]['failed'] += 1
                    print(f"❌ 爬取失败（数据质量不合格）: {title}")
                    return False
                
                # 清理内容（移除不相关数据）
                cleaned_chapters = []
                for chapter in novel_info_dict.get('chapters', []):
                    content = chapter.get('content', '')
                    cleaned_content = DataValidator.clean_content(content)
                    if cleaned_content:
                        cleaned_chapters.append({
                            'title': chapter.get('title', ''),
                            'url': chapter.get('url', ''),
                            'content': cleaned_content
                        })
                
                # 更新小说信息
                novel_info_dict['chapters'] = cleaned_chapters
                
                # 重新保存清理后的内容
                content = self._extract_full_content(novel_info_dict)
                if content:
                    with open(txt_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                
                # 保存元数据
                metadata = {
                    'title': actual_title,
                    'author': novel_info_dict.get('author', '未知'),
                    'description': novel_info_dict.get('description', ''),
                    'url': url,
                    'site': site_name,
                    'category': category,
                    'scraped_time': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'chapters': validation_stats['valid_chapters'],
                    'total_chapters': validation_stats['total_chapters'],
                    'total_chars': validation_stats['valid_chars'],
                    'validation_stats': validation_stats
                }
                
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
                
                # 统计
                self.stats['success'] += 1
                self.stats['total_chapters'] += validation_stats['valid_chapters']
                self.stats['total_chars'] += validation_stats['valid_chars']
                
                if site_name not in self.stats['sites']:
                    self.stats['sites'][site_name] = {'success': 0, 'failed': 0}
                self.stats['sites'][site_name]['success'] += 1
                
                self.scraped_novels.append({
                    **novel_info,
                    'title': actual_title,
                    'file': txt_file,
                    'site': site_name,
                    'category': category,
                    'novel_dir': novel_dir,
                    'metadata': metadata
                })
                
                print(f"✅ 爬取成功: {actual_title} ({validation_stats['valid_chapters']}/{validation_stats['total_chapters']}章有效, {validation_stats['valid_chars']}字符)")
                
                # 清理临时文件和目录
                self._cleanup_temp_files(temp_dir, scraper)
                
                return True
            else:
                # 清理临时文件（即使失败也要清理）
                if 'temp_dir' in locals():
                    self._cleanup_temp_files(temp_dir, None)
                
                self.failed_novels.append(novel_info)
                self.stats['failed'] += 1
                if site_name not in self.stats['sites']:
                    self.stats['sites'][site_name] = {'success': 0, 'failed': 0}
                self.stats['sites'][site_name]['failed'] += 1
                print(f"❌ 爬取失败: {title}")
                return False
                
        except Exception as e:
            import traceback
            print(f"❌ 爬取出错: {e}")
            traceback.print_exc()
            
            # 清理临时文件（即使出错也要清理）
            if 'temp_dir' in locals():
                self._cleanup_temp_files(temp_dir, None)
            
            self.failed_novels.append(novel_info)
            self.stats['failed'] += 1
            if site_name not in self.stats['sites']:
                self.stats['sites'][site_name] = {'success': 0, 'failed': 0}
            self.stats['sites'][site_name]['failed'] += 1
            return False
    
    def batch_scrape(self, site_name: str, category: str, count: int = 10, 
                     filter_completed: bool = True) -> Dict:
        """
        批量爬取
        
        Args:
            site_name: 网站名称
            category: 小说类型
            count: 爬取数量
            filter_completed: 是否只爬取已完结的
        
        Returns:
            爬取统计
        """
        print(f"\n🚀 开始批量爬取")
        print(f"   网站: {site_name}")
        print(f"   类型: {category}")
        print(f"   数量: {count} 本")
        if filter_completed:
            print(f"   筛选: 仅已完结")
        
        # 获取小说列表
        novels = self.get_category_list(site_name, category, filter_completed)
        
        if not novels:
            print("❌ 未找到符合条件的小说列表")
            return self.stats
        
        if len(novels) < count:
            print(f"⚠️  只找到 {len(novels)} 本符合条件的小说（请求 {count} 本）")
        
        novels = novels[:count]
        self.stats['total'] = len(novels)
        
        print(f"\n📚 准备爬取以下 {len(novels)} 本小说:")
        for i, novel in enumerate(novels[:10], 1):
            status = "✅ 已完结" if novel.get('completed', False) else "⏳ 连载中"
            print(f"   {i}. {novel['title'][:50]:50s} - {status}")
        if len(novels) > 10:
            print(f"   ... 还有 {len(novels) - 10} 本")
        
        # 逐个爬取
        for idx, novel_info in enumerate(novels, 1):
            print(f"\n📖 进度: [{idx}/{len(novels)}]")
            self.scrape_novel(site_name, novel_info)
            if idx < len(novels):
                time.sleep(2)
        
        # 批量爬取完成后，清理所有临时目录
        self._cleanup_all_temp_dirs(site_name, category)
        
        return self.stats
    
    def _cleanup_temp_files(self, temp_dir: str, scraper: Optional[NovelScraper] = None):
        """
        清理临时文件和目录
        
        Args:
            temp_dir: 临时目录路径
            scraper: NovelScraper实例（可选）
        """
        try:
            # 清理临时目录
            if temp_dir and os.path.exists(temp_dir):
                # 检查是否是.temp目录
                if temp_dir.endswith('.temp') or '.temp' in temp_dir:
                    try:
                        shutil.rmtree(temp_dir)
                        print(f"   🗑️  已清理临时目录: {os.path.basename(temp_dir)}")
                    except (OSError, PermissionError) as e:
                        print(f"   ⚠️  清理临时目录失败: {e}")
            
            # 清理scraper创建的临时文件
            if scraper and hasattr(scraper, 'novel_output_dir') and scraper.novel_output_dir:
                # 如果novel_output_dir在temp_dir中，清理它
                if temp_dir and temp_dir in scraper.novel_output_dir:
                    try:
                        if os.path.exists(scraper.novel_output_dir):
                            shutil.rmtree(scraper.novel_output_dir)
                    except (OSError, PermissionError):
                        pass
            
            # 清理scraper的session（释放连接）
            if scraper and hasattr(scraper, 'session'):
                try:
                    scraper.session.close()
                except:
                    pass
                    
        except Exception as e:
            # 静默失败，不影响主流程
            pass
    
    def _cleanup_all_temp_dirs(self, site_name: str, category: str):
        """
        清理指定网站和类型的所有临时目录
        
        Args:
            site_name: 网站名称
            category: 小说类型
        """
        try:
            temp_base_dir = os.path.join(self.output_base_dir, 'novels', site_name, category)
            if os.path.exists(temp_base_dir):
                # 查找所有.temp目录
                for root, dirs, files in os.walk(temp_base_dir):
                    if '.temp' in root:
                        try:
                            shutil.rmtree(root)
                            print(f"   🗑️  已清理临时目录: {os.path.basename(root)}")
                        except (OSError, PermissionError):
                            pass
        except Exception as e:
            # 静默失败
            pass
    
    def _extract_full_content(self, novel_info: Dict) -> str:
        """从小说信息中提取完整内容"""
        content_parts = []
        
        if novel_info.get('title'):
            content_parts.append(f"标题: {novel_info['title']}")
        if novel_info.get('author'):
            content_parts.append(f"作者: {novel_info['author']}")
        if novel_info.get('description'):
            content_parts.append(f"\n简介:\n{novel_info['description']}")
        
        content_parts.append("\n" + "="*50 + "\n")
        
        chapters = novel_info.get('chapters', [])
        for chapter in chapters:
            if isinstance(chapter, dict):
                title = chapter.get('title', '')
                content = chapter.get('content', '')
                if title and content:
                    content_parts.append(f"\n{title}")
                    content_parts.append("="*50)
                    content_parts.append(f"\n{content}\n")
        
        return '\n'.join(content_parts)
    
    def generate_summary(self) -> Dict:
        """生成爬取摘要"""
        summary = {
            'stats': self.stats,
            'successful_novels': [
                {
                    'title': n['title'],
                    'site': n.get('site', '未知'),
                    'category': n.get('category', '未知'),
                    'file': n.get('file', '')
                }
                for n in self.scraped_novels
            ],
            'failed_novels': [
                {
                    'title': n['title'],
                    'url': n['url']
                }
                for n in self.failed_novels
            ]
        }
        return summary


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='多网站批量小说爬取工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 注册网站并爬取
  python3 multi_site_scraper.py --register https://m.shuhaige.net
  python3 multi_site_scraper.py --site m.shuhaige.net --category 都市 --count 10
  
  # 列出已注册的网站
  python3 multi_site_scraper.py --list-sites
  
  # 爬取多个网站
  python3 multi_site_scraper.py --site m.shuhaige.net --category 都市 --count 5
  python3 multi_site_scraper.py --site m.shuhaige.net --category 玄幻 --count 5
        """
    )
    
    parser.add_argument('--register', type=str, metavar='URL',
                       help='注册新网站（URL）')
    parser.add_argument('--list-sites', action='store_true',
                       help='列出所有已注册的网站')
    parser.add_argument('--site', type=str, metavar='SITE_NAME',
                       help='网站名称（如：m.shuhaige.net）')
    parser.add_argument('--category', type=str, metavar='CATEGORY',
                       help='小说类型（如：都市、玄幻、言情等）')
    parser.add_argument('--count', type=int, default=10, metavar='N',
                       help='爬取数量（默认：10）')
    parser.add_argument('--output', '-o', default='data/training',
                       help='输出目录（默认：data/training）')
    parser.add_argument('--no-filter-completed', dest='filter_completed', action='store_false',
                       help='不筛选，爬取所有小说（包括连载中的）')
    parser.add_argument('--generate-data', '-g', action='store_true',
                       help='自动生成训练数据文件')
    
    args = parser.parse_args()
    
    scraper = MultiSiteScraper(args.output)
    
    # 注册网站
    if args.register:
        config = scraper.register_site(args.register)
        if config:
            print(f"\n✅ 网站注册成功: {config.get('url')}")
            if config.get('adapter'):
                print(f"   适配器: {config['adapter']}")
            else:
                print(f"   状态: {config.get('status')}")
                print(f"   ⚠️  需要手动创建适配器")
        return
    
    # 列出网站
    if args.list_sites:
        sites = scraper.site_manager.list_sites()
        print(f"\n📋 已注册的网站 ({len(sites)} 个):")
        for site in sites:
            print(f"\n   {site['name']}")
            print(f"   URL: {site['url']}")
            print(f"   状态: {site['status']}")
            if site.get('adapter'):
                print(f"   适配器: {site['adapter']}")
            if site.get('categories'):
                print(f"   分类: {', '.join(site['categories'])}")
        return
    
    # 批量爬取
    if not args.site or not args.category:
        parser.print_help()
        print("\n❌ 错误: 需要指定 --site 和 --category")
        return
    
    stats = scraper.batch_scrape(args.site, args.category, args.count, args.filter_completed)
    
    # 生成摘要
    summary = scraper.generate_summary()
    summary_file = os.path.join(args.output, 'novels', 'summary.json')
    os.makedirs(os.path.dirname(summary_file), exist_ok=True)
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    # 保存爬取的小说信息
    novels_info_file = os.path.join(args.output, 'novels', 'scraped_novels.json')
    with open(novels_info_file, 'w', encoding='utf-8') as f:
        json.dump(scraper.scraped_novels, f, ensure_ascii=False, indent=2)
    
    # 打印统计
    print(f"\n{'='*60}")
    print("📊 爬取统计")
    print(f"{'='*60}")
    print(f"  总计: {stats['total']} 本")
    print(f"  成功: {stats['success']} 本")
    print(f"  失败: {stats['failed']} 本")
    print(f"  总章节: {stats['total_chapters']} 章")
    print(f"  总字符: {stats['total_chars']:,} 字符")
    
    if stats['sites']:
        print(f"\n   按网站统计:")
        for site_name, site_stats in stats['sites'].items():
            print(f"     {site_name}: 成功 {site_stats['success']} 本, 失败 {site_stats['failed']} 本")
    
    print(f"\n📁 文件保存在: {args.output}/novels/")
    print(f"📄 摘要文件: {summary_file}")
    
    # 生成训练数据
    if args.generate_data:
        print(f"\n📝 正在生成训练数据...")
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
        from training_data_generator import TrainingDataGenerator
        
        generator = TrainingDataGenerator(args.output)
        training_file = generator.generate_from_novels(use_ai=args.use_ai)
        
        if training_file:
            print(f"   ✅ 训练数据已生成: {training_file}")
        else:
            print(f"   ❌ 训练数据生成失败")


if __name__ == '__main__':
    main()

