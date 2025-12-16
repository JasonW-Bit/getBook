#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小说改写脚本（增强版）
功能：
- 阅读并理解小说内容
- 提炼故事脉络、人物形象、情节起伏
- 改写小说风格
- 转换人称视角
- 替换人物姓名
- 多种风格选项
"""

import os
import re
import sys
import json
import random
from typing import Dict, List, Optional, Set, Tuple
from collections import Counter, defaultdict

# 导入AI和创意处理模块
import sys
import os

# 添加父目录到路径
parent_dir = os.path.dirname(os.path.dirname(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from scripts.ai.integration import UnifiedRewriter, CreativeAIEngine, create_engine
    from scripts.ai.analyzers.ai_analyzer import AIAnalyzerFactory
    AI_AVAILABLE = True
    INTEGRATION_AVAILABLE = True
except ImportError:
    try:
        # 尝试相对导入
        from ..ai.integration import UnifiedRewriter, CreativeAIEngine, create_engine
        from ..ai.analyzers.ai_analyzer import AIAnalyzerFactory
        AI_AVAILABLE = True
        INTEGRATION_AVAILABLE = True
    except ImportError:
        try:
            # 降级到直接导入
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai', 'analyzers'))
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai', 'models'))
            from ai_analyzer import AIAnalyzerFactory
            AI_AVAILABLE = True
            INTEGRATION_AVAILABLE = False
        except ImportError:
            AI_AVAILABLE = False
            INTEGRATION_AVAILABLE = False
            print("⚠️  AI分析器模块未找到，将使用传统分析方法")

# 尝试导入智能文本处理器
try:
    from scripts.creative.processors.text_processor import NaturalStyleRewriter
    NATURAL_REWRITER_AVAILABLE = True
except ImportError:
    try:
        from .processors.text_processor import NaturalStyleRewriter
        NATURAL_REWRITER_AVAILABLE = True
    except ImportError:
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'processors'))
            from text_processor import NaturalStyleRewriter
            NATURAL_REWRITER_AVAILABLE = True
        except ImportError:
            NATURAL_REWRITER_AVAILABLE = False


class NovelAnalyzer:
    """小说分析器"""
    
    def __init__(self, content: str):
        self.content = content
        self.characters = {}  # 人物信息
        self.storyline = []   # 故事脉络
        self.plot_points = [] # 情节转折点
        self.chapters = []    # 章节信息
    
    def extract_characters(self) -> Dict[str, Dict]:
        """
        提取人物信息
        
        Returns:
            人物字典，包含姓名、出现次数、角色类型等
        """
        # 排除词列表（不是人名的常见词）
        exclude_words = {
            '大家', '自己', '他们', '我们', '你们', '她们', '它们',
            '什么', '怎么', '这样', '那样', '这个', '那个', '这些', '那些',
            '今天', '明天', '昨天', '现在', '以后', '之前', '之后',
            '开始', '结束', '完成', '继续', '然后', '接着', '最后',
            '第一', '第二', '第三', '第四', '第五', '第六', '第七', '第八', '第九', '第十',
            '一个', '两个', '三个', '四个', '五个',
            '这里', '那里', '哪里', '这边', '那边',
            '结婚', '拒绝', '临时', '彩礼', '之后', '当天',
            '点头', '笑道', '说道', '说道', '说道', '说道',
            '哈哈', '呵呵', '嘿嘿', '嘻嘻',
            '小说', '章节', '内容', '标题', '作者', '简介',
        }
        
        # 更精确的姓名模式：常见中文姓氏 + 名字（2-3个字）
        common_surnames = ['王', '李', '张', '刘', '陈', '杨', '赵', '黄', '周', '吴',
                          '徐', '孙', '胡', '朱', '高', '林', '何', '郭', '马', '罗',
                          '梁', '宋', '郑', '谢', '韩', '唐', '冯', '于', '董', '萧',
                          '程', '曹', '袁', '邓', '许', '傅', '沈', '曾', '彭', '吕',
                          '苏', '卢', '蒋', '蔡', '贾', '丁', '魏', '薛', '叶', '阎']
        
        # 方法1: 查找"姓氏+名字"模式
        surname_pattern = '|'.join(common_surnames)
        name_pattern1 = rf'({surname_pattern})[一-龥]{{1,2}}(?=[，。！？：；\s]|$)'
        
        # 方法2: 查找引号内的称呼（可能是人名）
        quote_pattern = r'["""]([一-龥]{2,3})["""]'
        
        # 方法3: 查找"XX说"、"XX道"等模式
        speech_pattern = r'([一-龥]{2,3})(?:说|道|问|答|喊|叫|想|看|听|走|来|去)(?=[，。！？：；\s]|$)'
        
        potential_names = set()
        
        # 提取所有可能的姓名
        for pattern in [name_pattern1, quote_pattern, speech_pattern]:
            matches = re.findall(pattern, self.content)
            potential_names.update(matches)
        
        # 过滤排除词
        potential_names = {name for name in potential_names 
                         if name not in exclude_words 
                         and len(name) >= 2 
                         and len(name) <= 4}
        
        # 统计出现频率
        name_counter = Counter()
        for name in potential_names:
            # 使用单词边界匹配，避免部分匹配
            pattern = r'(?<![一-龥])' + re.escape(name) + r'(?![一-龥])'
            count = len(re.findall(pattern, self.content))
            if count >= 10:  # 提高阈值，减少误识别
                name_counter[name] = count
        
        # 进一步过滤：检查是否出现在对话或动作中
        characters = {}
        for name, count in name_counter.most_common(30):
            # 检查是否出现在合理的上下文中
            pattern = r'(?<![一-龥])' + re.escape(name) + r'(?![一-龥])'
            matches = list(re.finditer(pattern, self.content))[:5]
            
            valid = False
            for match in matches:
                start = max(0, match.start() - 20)
                end = min(len(self.content), match.end() + 20)
                context = self.content[start:end]
                # 检查是否在对话、动作等合理上下文中
                if any(keyword in context for keyword in ['说', '道', '问', '答', '想', '看', '走', '来', '去', '的', '是']):
                    valid = True
                    break
            
            if valid:
                role_type = self._classify_character(name, count)
                characters[name] = {
                    'name': name,
                    'count': count,
                    'role': role_type,
                    'mentions': []
                }
        
        # 提取人物出现的上下文
        for name in characters.keys():
            mentions = []
            pattern = r'(?<![一-龥])' + re.escape(name) + r'(?![一-龥])'
            for match in re.finditer(pattern, self.content):
                start = max(0, match.start() - 50)
                end = min(len(self.content), match.end() + 50)
                context = self.content[start:end]
                mentions.append(context)
            characters[name]['mentions'] = mentions[:10]
        
        self.characters = characters
        print(f"📊 识别到 {len(characters)} 个主要人物")
        if characters:
            top_chars = sorted(characters.items(), key=lambda x: x[1]['count'], reverse=True)[:5]
            print(f"   主要人物: {', '.join([name for name, _ in top_chars])}")
        return characters
    
    def _classify_character(self, name: str, count: int) -> str:
        """分类角色类型"""
        # 根据出现频率判断
        if count > 100:
            return '主角'
        elif count > 50:
            return '主要角色'
        elif count > 20:
            return '配角'
        else:
            return '次要角色'
    
    def analyze_storyline(self) -> List[Dict]:
        """
        分析故事脉络
        
        Returns:
            故事脉络列表
        """
        # 分割章节
        chapter_pattern = r'第\s*(\d+)\s*章[：:：]?\s*(.*?)\n'
        chapters = []
        
        for match in re.finditer(chapter_pattern, self.content):
            chapter_num = int(match.group(1))
            chapter_title = match.group(2).strip() if match.group(2) else f"第{chapter_num}章"
            start_pos = match.end()
            
            # 查找下一章位置
            next_match = None
            for next_match_iter in re.finditer(chapter_pattern, self.content):
                if next_match_iter.start() > match.start():
                    next_match = next_match_iter
                    break
            
            end_pos = next_match.start() if next_match else len(self.content)
            chapter_content = self.content[start_pos:end_pos]
            
            chapters.append({
                'num': chapter_num,
                'title': chapter_title,
                'content': chapter_content,
                'length': len(chapter_content),
                'key_events': self._extract_key_events(chapter_content)
            })
        
        self.chapters = chapters
        self.storyline = chapters
        
        print(f"📖 分析完成，共 {len(chapters)} 个章节")
        return chapters
    
    def _extract_key_events(self, content: str) -> List[str]:
        """提取关键事件"""
        events = []
        
        # 查找关键动作词
        action_patterns = [
            r'[^。！？]{0,30}(发现|遇到|决定|开始|结束|离开|到达|找到|失去)[^。！？]{0,30}[。！？]',
            r'[^。！？]{0,30}(突然|忽然|终于|竟然|没想到)[^。！？]{0,30}[。！？]',
        ]
        
        for pattern in action_patterns:
            matches = re.findall(pattern, content)
            events.extend(matches[:3])  # 每章最多3个关键事件
        
        return events
    
    def analyze_plot_structure(self) -> Dict:
        """
        分析情节结构
        
        Returns:
            情节结构信息
        """
        plot_structure = {
            'beginning': [],  # 开端
            'development': [], # 发展
            'climax': [],     # 高潮
            'ending': []      # 结尾
        }
        
        if not self.chapters:
            self.analyze_storyline()
        
        total_chapters = len(self.chapters)
        
        # 根据章节位置划分情节阶段
        for i, chapter in enumerate(self.chapters):
            position = i / total_chapters if total_chapters > 0 else 0
            
            if position < 0.2:
                plot_structure['beginning'].append(chapter)
            elif position < 0.7:
                plot_structure['development'].append(chapter)
            elif position < 0.9:
                plot_structure['climax'].append(chapter)
            else:
                plot_structure['ending'].append(chapter)
        
        self.plot_points = plot_structure
        return plot_structure
    
    def generate_summary(self) -> Dict:
        """生成故事摘要"""
        summary = {
            'total_chapters': len(self.chapters),
            'total_characters': len(self.characters),
            'main_characters': [],
            'story_arc': '',
            'key_themes': []
        }
        
        # 主要人物（按出现频率）
        if self.characters:
            main_chars = sorted(self.characters.items(), 
                              key=lambda x: x[1]['count'], reverse=True)[:5]
            summary['main_characters'] = [name for name, _ in main_chars]
        
        # 故事弧线
        if self.plot_points:
            summary['story_arc'] = f"开端({len(self.plot_points['beginning'])}章) -> " \
                                 f"发展({len(self.plot_points['development'])}章) -> " \
                                 f"高潮({len(self.plot_points['climax'])}章) -> " \
                                 f"结尾({len(self.plot_points['ending'])}章)"
        
        return summary


class CharacterNameMapper:
    """人物姓名映射器"""
    
    def __init__(self):
        self.name_mapping = {}
        self.name_pool = {
            'male': ['张伟', '王强', '李明', '刘洋', '陈军', '杨磊', '赵刚', '黄勇', 
                    '周杰', '吴斌', '徐涛', '孙浩', '马超', '朱峰', '胡亮'],
            'female': ['李娜', '王芳', '张敏', '刘静', '陈丽', '杨雪', '赵琳', '黄梅',
                      '周雨', '吴婷', '徐雯', '孙悦', '马莉', '朱欣', '胡颖'],
            'surname': ['张', '王', '李', '刘', '陈', '杨', '赵', '黄', '周', '吴', 
                       '徐', '孙', '马', '朱', '胡', '林', '何', '高', '梁', '郑']
        }
        self.used_names = set()
    
    def generate_name(self, gender: str = 'unknown') -> str:
        """生成新姓名"""
        if gender == 'male' or gender == 'unknown':
            pool = self.name_pool['male'] + self.name_pool['female']
        else:
            pool = self.name_pool['female']
        
        # 找到未使用的姓名
        available = [n for n in pool if n not in self.used_names]
        if not available:
            # 如果都用完了，组合生成
            surname = self.name_pool['surname'][len(self.used_names) % len(self.name_pool['surname'])]
            given = ['伟', '强', '明', '洋', '军', '磊', '刚', '勇'][len(self.used_names) % 8]
            name = surname + given
        else:
            name = available[0]
        
        self.used_names.add(name)
        return name
    
    def create_mapping(self, original_names: List[str]) -> Dict[str, str]:
        """创建姓名映射"""
        mapping = {}
        for orig_name in original_names:
            if orig_name not in mapping:
                new_name = self.generate_name()
                mapping[orig_name] = new_name
        self.name_mapping = mapping
        return mapping
    
    def replace_names(self, text: str) -> str:
        """替换文本中的姓名"""
        result = text
        # 按长度从长到短排序，避免短名覆盖长名
        sorted_names = sorted(self.name_mapping.items(), key=lambda x: len(x[0]), reverse=True)
        for orig, new in sorted_names:
            result = result.replace(orig, new)
        return result


class NovelRewriter:
    """小说改写类（增强版）"""
    
    def __init__(self, input_file: str, output_file: Optional[str] = None, output_dir: str = "rewritten"):
        """
        初始化改写器
        
        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径（可选）
            output_dir: 输出文件夹名称，默认为"rewritten"
        """
        self.input_file = input_file
        self.output_dir = output_dir
        
        # 获取输入文件的目录和文件名
        input_dir = os.path.dirname(input_file)
        input_basename = os.path.basename(input_file)
        input_name, input_ext = os.path.splitext(input_basename)
        
        # 创建输出文件夹
        if input_dir:
            self.output_dir_path = os.path.join(input_dir, output_dir)
        else:
            self.output_dir_path = output_dir
        
        if not os.path.exists(self.output_dir_path):
            os.makedirs(self.output_dir_path)
            print(f"📁 创建输出文件夹: {self.output_dir_path}/")
        
        # 设置输出文件路径
        if not output_file:
            output_basename = f"{input_name}_rewritten{input_ext}"
            self.output_file = os.path.join(self.output_dir_path, output_basename)
        else:
            if not os.path.dirname(output_file):
                self.output_file = os.path.join(self.output_dir_path, output_file)
            else:
                self.output_file = output_file
        
        self.content = ""
        self.metadata = {}
        self.analyzer = None
        self.name_mapper = CharacterNameMapper()
        self.ai_analyzer = None  # AI分析器
        self.ai_analyzer = None  # AI分析器
    
    def load_novel(self) -> bool:
        """加载小说内容"""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                self.content = f.read()
            print(f"✅ 成功加载小说: {self.input_file}")
            return True
        except Exception as e:
            print(f"❌ 加载失败: {e}")
            return False
    
    def analyze_novel(self, use_ai: bool = False, ai_type: str = "openai", **ai_kwargs) -> bool:
        """
        分析小说内容
        
        Args:
            use_ai: 是否使用AI分析
            ai_type: AI类型（openai/local/offline）
            **ai_kwargs: AI相关参数
        """
        if not self.content:
            if not self.load_novel():
                return False
        
        print("\n📚 开始分析小说内容...")
        
        # 尝试使用AI分析
        if use_ai and AI_AVAILABLE:
            try:
                self.ai_analyzer = AIAnalyzerFactory.create_analyzer(ai_type, **ai_kwargs)
                if self.ai_analyzer:
                    print("🤖 使用AI进行深度分析...")
                    
                    # 使用AI分析人物
                    ai_characters = self.ai_analyzer.analyze_characters(self.content)
                    if ai_characters:
                        print(f"   AI识别到 {len(ai_characters)} 个人物")
                    
                    # 使用AI分析故事脉络
                    ai_storyline = self.ai_analyzer.analyze_storyline(self.content)
                    if ai_storyline:
                        print(f"   AI分析完成：{ai_storyline.get('theme', '未知主题')}")
            except Exception as e:
                print(f"⚠️  AI分析失败，使用传统方法: {e}")
                self.ai_analyzer = None
        
        # 使用传统方法分析
        if not self.analyzer:
            self.analyzer = NovelAnalyzer(self.content)
        
        # 提取人物
        characters = self.analyzer.extract_characters()
        
        # 合并AI分析结果
        if use_ai and self.ai_analyzer:
            ai_characters = self.ai_analyzer.analyze_characters(self.content)
            if ai_characters:
                for name, info in ai_characters.items():
                    if name not in self.analyzer.characters:
                        self.analyzer.characters[name] = {
                            'name': name,
                            'count': self.content.count(name),
                            'role': info.get('role', '配角'),
                            'description': info.get('description', ''),
                            'importance': info.get('importance', 5)
                        }
        
        # 分析故事脉络
        storyline = self.analyzer.analyze_storyline()
        
        # 分析情节结构
        plot_structure = self.analyzer.analyze_plot_structure()
        
        # 生成摘要
        summary = self.analyzer.generate_summary()
        
        print(f"\n📊 分析结果:")
        print(f"   总章节数: {summary['total_chapters']}")
        print(f"   主要人物: {', '.join(summary['main_characters'][:5])}")
        print(f"   故事结构: {summary['story_arc']}")
        
        return True
    
    def change_perspective(self, from_perspective: str = "第一人称", to_perspective: str = "第三人称") -> str:
        """转换人称视角"""
        if from_perspective == to_perspective:
            return self.content
        
        result = self.content
        
        if from_perspective == "第一人称" and to_perspective == "第三人称":
            replacements = {
                r'\b我\b': '他',
                r'\b我的\b': '他的',
                r'\b我们\b': '他们',
                r'\b我们的\b': '他们的',
                r'\b自己\b': '他自己',
            }
            for pattern, replacement in replacements.items():
                result = re.sub(pattern, replacement, result)
        
        elif from_perspective == "第三人称" and to_perspective == "第一人称":
            replacements = {
                r'\b他\b': '我',
                r'\b他的\b': '我的',
                r'\b他们\b': '我们',
                r'\b他们的\b': '我们的',
            }
            for pattern, replacement in replacements.items():
                result = re.sub(pattern, replacement, result)
        
        print(f"✅ 视角转换完成: {from_perspective} → {to_perspective}")
        return result
    
    def _split_into_chapters(self, content: str) -> List[str]:
        """将内容分割成章节"""
        chapters = []
        
        # 查找章节标记
        chapter_pattern = r'第\s*(\d+)\s*章[：:：]?\s*(.*?)\n'
        matches = list(re.finditer(chapter_pattern, content))
        
        if not matches:
            # 如果没有章节标记，返回整个内容作为一个章节
            return [content]
        
        for i, match in enumerate(matches):
            chapter_start = match.end()
            next_match = matches[i + 1] if i + 1 < len(matches) else None
            chapter_end = next_match.start() if next_match else len(content)
            
            chapter_text = content[chapter_start:chapter_end].strip()
            if chapter_text:
                chapters.append(chapter_text)
        
        return chapters if chapters else [content]
    
    def change_style(self, style: str = "现代", use_ai: bool = False, 
                     ai_type: str = "tensorflow",
                     novel_context: Optional[Dict] = None,
                     chapter_context: Optional[str] = None,
                     **ai_kwargs) -> str:
        """
        修改语言风格（增强版，支持统一接口）
        
        Args:
            style: 目标风格
                基础风格：现代/古典/简洁/华丽/悬疑/浪漫/幽默/严肃
                扩展风格：科幻/武侠/青春/都市/古风/诗化/口语/正式/网络/文艺
            use_ai: 是否使用AI进行改写
            ai_type: AI类型 (openai/local/tensorflow)
            **ai_kwargs: AI相关参数
        """
        # 优先使用统一接口（如果可用）
        if use_ai and INTEGRATION_AVAILABLE:
            try:
                from scripts.ai.integration import UnifiedRewriter
                model_path = ai_kwargs.get('model_path', 'models/text_rewriter_model')
                rewriter = UnifiedRewriter(
                    ai_type=ai_type,
                    ai_model_path=model_path,
                    use_hybrid=True
                )
                
                # 提取上下文（增强版）
                context = chapter_context if chapter_context else ""
                if not context and self.analyzer:
                    summary = self.analyzer.generate_summary()
                    context = f"故事主题：{summary.get('story_arc', '')}，主要人物：{', '.join(summary.get('main_characters', [])[:5])}"
                
                # 使用统一接口改写（传入小说上下文）
                result = rewriter.rewrite(
                    self.content,
                    style=style,
                    context=context,
                    use_ai=True,
                    novel_context=novel_context,
                    chapter_num=0
                )
                
                if result and result != self.content:
                    print(f"✅ 使用统一接口完成风格转换: {style}")
                    return result
            except Exception as e:
                print(f"⚠️  统一接口失败，降级到传统方法: {e}")
        
        # 如果使用AI且AI分析器可用，使用AI改写（深度学习优化版）
        if use_ai and self.ai_analyzer:
            print(f"🤖 使用深度学习AI进行风格转换和语言优化: {style}")
            try:
                # 智能分段处理（保持上下文连贯）
                result_parts = []
                chunk_size = 3000  # 增加处理长度，保持更多上下文
                total_chunks = (len(self.content) + chunk_size - 1) // chunk_size
                
                # 提取整体上下文信息（用于帮助AI理解）
                context_summary = ""
                if self.analyzer:
                    summary = self.analyzer.generate_summary()
                    context_summary = f"故事主题：{summary.get('story_arc', '')}，主要人物：{', '.join(summary.get('main_characters', [])[:5])}"
                
                for i in range(0, len(self.content), chunk_size):
                    # 获取当前块
                    chunk = self.content[i:i+chunk_size]
                    
                    # 获取前一块的结尾（作为上下文）
                    prev_context = ""
                    if i > 0:
                        prev_start = max(0, i - 500)  # 前500字符作为上下文
                        prev_context = self.content[prev_start:i]
                    
                    # 获取下一块的开头（作为上下文）
                    next_context = ""
                    if i + chunk_size < len(self.content):
                        next_end = min(len(self.content), i + chunk_size + 200)  # 后200字符作为上下文
                        next_context = self.content[i+chunk_size:next_end]
                    
                    # 构建完整上下文
                    full_context = f"{prev_context}\n\n[当前文本]\n\n{chunk}\n\n[后续文本预览]\n\n{next_context}"
                    if context_summary:
                        full_context = f"{context_summary}\n\n{full_context}"
                    
                    # 使用AI改写（传入上下文）
                    rewritten_chunk = self.ai_analyzer.rewrite_text(
                        chunk, 
                        style, 
                        context=full_context
                    )
                    
                    result_parts.append(rewritten_chunk)
                    current_chunk = (i // chunk_size) + 1
                    print(f"   🤖 AI处理进度: {current_chunk}/{total_chunks} ({current_chunk*100//total_chunks}%)")
                
                result = ''.join(result_parts)
                print(f"✅ 深度学习AI风格转换完成: {style}")
                return result
            except Exception as e:
                print(f"⚠️  AI改写失败，使用传统方法: {e}")
                import traceback
                traceback.print_exc()
        
        # 传统方法 - 优先使用自然改写器
        if NATURAL_REWRITER_AVAILABLE and style in ['都市', '幽默', '都市幽默', '都市+幽默', '都市、幽默']:
            print(f"✨ 使用智能文本处理器进行自然改写...")
            try:
                natural_rewriter = NaturalStyleRewriter()
                result = natural_rewriter.rewrite_naturally(self.content, style)
                print(f"✅ 自然风格转换完成: {style}")
                return result
            except Exception as e:
                print(f"⚠️  智能改写失败，使用传统方法: {e}")
        
        # 传统方法（备用）
        result = self.content
        
        if style == "简洁":
            # 简化表达
            result = re.sub(r'，[^，。！？]{0,5}，', '，', result)
            result = re.sub(r'。\s*。', '。', result)
            result = re.sub(r'[，。！？]{2,}', lambda m: m.group(0)[0], result)
        
        elif style == "华丽":
            # 增加修饰词
            result = re.sub(r'(\w+)([，。！？])', r'\1，\2', result)
            # 添加形容词
            result = re.sub(r'(是)([^，。！？]+)', r'\1如此的\2', result)
        
        elif style == "古典":
            # 转换为古典风格
            replacements = {
                r'的': '之',
                r'了': '矣',
                r'吗': '乎',
                r'呢': '焉',
            }
            for pattern, replacement in replacements.items():
                result = re.sub(pattern, replacement, result)
        
        elif style == "悬疑":
            # 增加悬疑氛围
            result = re.sub(r'([。！？])\s*', r'\1\n\n【气氛紧张】\n\n', result[:1000]) + result[1000:]
        
        elif style == "浪漫":
            # 增加浪漫元素
            result = re.sub(r'(说|道)([^，。！？]+)', r'\1，眼中闪烁着温柔的光芒\2', result)
        
        elif style == "幽默":
            # 增加幽默元素
            result = re.sub(r'([。！？])\s*([^，。！？]{0,20})', r'\1\n【有趣的是】\2', result[:500]) + result[500:]
        
        elif style == "严肃":
            # 严肃风格
            result = re.sub(r'([，。！？])\s*', r'\1\n', result)
        
        elif style == "科幻":
            # 科幻风格：增加科技感、未来感
            result = re.sub(r'(说|道)', r'通过通讯器说道', result[:500]) + result[500:]
            result = re.sub(r'(看|观察)', r'通过扫描仪观察', result[:500]) + result[500:]
        
        elif style == "武侠":
            # 武侠风格：增加武侠元素
            result = re.sub(r'(走|来|去)', r'施展轻功\1', result[:500]) + result[500:]
            result = re.sub(r'(说|道)', r'抱拳说道', result[:300]) + result[300:]
        
        elif style == "青春":
            # 青春风格：轻松活泼
            result = re.sub(r'([。！？])\s*', r'\1\n\n', result)
            result = re.sub(r'(很|非常)', r'超级', result[:1000]) + result[1000:]
        
        elif style == "都市":
            # 都市风格：现代都市生活，增加都市场景描写
            # 适度增加都市元素，避免过度替换
            # 在关键位置添加都市场景
            result = re.sub(r'(说|道)([^，。！？]{5,30}[，。！？])', 
                          lambda m: f"{m.group(1)}，在都市的咖啡厅里{m.group(2)}" if random.random() < 0.1 else m.group(0), 
                          result)
            # 增加都市氛围词汇（适度）
            result = re.sub(r'\b(城市|地方)\b', r'都市', result[:5000]) + result[5000:]
            # 增加现代都市生活元素
            result = re.sub(r'(走|来|去)([^，。！？]{0,15}[，。！？])', 
                          lambda m: f"穿梭在都市街道上{m.group(1)}{m.group(2)}" if random.random() < 0.05 else m.group(0), 
                          result)
        
        elif style == "幽默":
            # 幽默风格：幽默风趣的表达，增加幽默元素
            # 在对话中适度增加幽默感（避免过度）
            result = re.sub(r'(".*?")([，。！？])', 
                          lambda m: f"{m.group(1)}，哈哈{m.group(2)}" if random.random() < 0.15 else m.group(0), 
                          result)
            # 使用轻松幽默的词汇
            result = re.sub(r'\b(很|非常)\b', r'超级', result[:3000]) + result[3000:]
            result = re.sub(r'\b(好)\b', r'棒极了', result[:2000]) + result[2000:]
            result = re.sub(r'\b(说|道)\b', 
                          lambda m: '笑着说' if random.random() < 0.1 else m.group(0), 
                          result)
            # 适度增加幽默描述（每段最多一个）
            lines = result.split('\n')
            new_lines = []
            humor_added = False
            for line in lines:
                if not humor_added and len(line) > 20 and random.random() < 0.05:
                    new_lines.append(line + ' 【有趣的是】')
                    humor_added = True
                else:
                    new_lines.append(line)
                if '。' in line or '！' in line or '？' in line:
                    humor_added = False
            result = '\n'.join(new_lines)
        
        elif style == "都市幽默" or style == "都市+幽默" or style == "都市、幽默":
            # 组合风格：都市+幽默，既有都市感又有幽默感
            # 先应用都市元素（适度）
            result = re.sub(r'\b(城市|地方)\b', r'都市', result[:5000]) + result[5000:]
            # 在关键位置添加都市场景
            result = re.sub(r'(说|道)([^，。！？]{5,30}[，。！？])', 
                          lambda m: f"{m.group(1)}，在都市的咖啡厅里笑着说{m.group(2)}" if random.random() < 0.08 else m.group(0), 
                          result)
            # 应用幽默元素
            result = re.sub(r'\b(很|非常)\b', r'超级', result[:3000]) + result[3000:]
            result = re.sub(r'\b(好)\b', r'棒极了', result[:2000]) + result[2000:]
            result = re.sub(r'(".*?")([，。！？])', 
                          lambda m: f"{m.group(1)}，哈哈{m.group(2)}" if random.random() < 0.12 else m.group(0), 
                          result)
            # 适度增加幽默描述
            lines = result.split('\n')
            new_lines = []
            humor_added = False
            for line in lines:
                if not humor_added and len(line) > 30 and random.random() < 0.03:
                    new_lines.append(line + ' 【在都市的喧嚣中，有趣的是】')
                    humor_added = True
                else:
                    new_lines.append(line)
                if '。' in line or '！' in line or '？' in line:
                    humor_added = False
            result = '\n'.join(new_lines)
        
        elif style == "古风":
            # 古风风格：古代文雅
            replacements = {
                r'的': '之',
                r'了': '矣',
                r'吗': '乎',
                r'呢': '焉',
                r'说': '曰',
                r'看': '观',
            }
            for pattern, replacement in replacements.items():
                result = re.sub(pattern, replacement, result)
        
        elif style == "诗化":
            # 诗化风格：增加诗意
            result = re.sub(r'([。！？])\s*', r'\1\n\n', result)
            result = re.sub(r'(\w+)([，。！？])', r'\1，如诗如画\2', result[:500]) + result[500:]
        
        elif style == "口语":
            # 口语化风格：更贴近日常对话
            result = re.sub(r'([，。！？])\s*', r'\1 ', result)
            result = re.sub(r'(很|非常)', r'挺', result[:1000]) + result[1000:]
        
        elif style == "正式":
            # 正式风格：正式书面语
            result = re.sub(r'(说|道)', r'表示', result)
            result = re.sub(r'(看|观察)', r'审视', result[:500]) + result[500:]
        
        elif style == "网络":
            # 网络风格：网络用语
            result = re.sub(r'(很|非常)', r'超', result[:1000]) + result[1000:]
            result = re.sub(r'(好)', r'棒', result[:500]) + result[500:]
        
        elif style == "文艺":
            # 文艺风格：文艺范
            result = re.sub(r'([。！？])\s*', r'\1\n\n', result)
            result = re.sub(r'(说|道)', r'轻声说道', result[:500]) + result[500:]
        
        elif style == "现代":
            # 现代风格：保持原样或轻微调整
            pass  # 现代风格通常不需要太多改动
        
        print(f"✅ 风格转换完成: {style}")
        return result
    
    def replace_character_names(self, replace_names: bool = True) -> str:
        """替换人物姓名"""
        if not replace_names:
            return self.content
        
        if not self.analyzer:
            if not self.analyze_novel():
                return self.content
        
        # 获取主要人物列表
        if not self.analyzer.characters:
            return self.content
        
        character_names = list(self.analyzer.characters.keys())
        
        # 创建姓名映射
        name_mapping = self.name_mapper.create_mapping(character_names)
        
        # 替换姓名
        result = self.name_mapper.replace_names(self.content)
        
        print(f"✅ 姓名替换完成，共替换 {len(name_mapping)} 个人物")
        print(f"   姓名映射: {dict(list(name_mapping.items())[:5])}...")
        
        return result
    
    def rewrite(self, perspective: Optional[str] = None, 
                style: Optional[str] = None, 
                replace_names: bool = False,
                analyze: bool = True,
                use_ai: bool = False,
                ai_type: str = "tensorflow",
                maintain_consistency: bool = True,
                **ai_kwargs) -> bool:
        """
        执行改写
        
        Args:
            perspective: 目标视角（可选）
            style: 目标风格（可选）
            replace_names: 是否替换人物姓名
            analyze: 是否先分析小说
        
        Returns:
            是否成功
        """
        if not self.content:
            if not self.load_novel():
                return False
        
        # 分析小说（如果需要）
        novel_context = None
        if analyze:
            if not self.analyze_novel(use_ai=use_ai, ai_type=ai_type, **ai_kwargs):
                print("⚠️  分析失败，继续使用基础改写功能")
            
            # 如果启用一致性检查，构建小说上下文
            if maintain_consistency:
                try:
                    from scripts.ai.context_manager import NovelContextManager
                    context_manager = NovelContextManager()
                    novel_context = context_manager.build_context(self.content)
                    print("✅ 已构建小说上下文，将用于保持逻辑一致性")
                except Exception as e:
                    print(f"⚠️  上下文构建失败: {e}")
        
        result = self.content
        
        # 如果内容很长，按章节处理以保持一致性
        chapters = self._split_into_chapters(result)
        if len(chapters) > 1 and maintain_consistency:
            print(f"📚 检测到 {len(chapters)} 个章节，将按章节处理以保持逻辑一致性...")
            rewritten_chapters = []
            
            for i, chapter in enumerate(chapters):
                print(f"   处理第 {i+1}/{len(chapters)} 章...")
                chapter_result = chapter
                
                # 替换姓名
                if replace_names:
                    chapter_result = self.replace_character_names(replace_names=True)
                
                # 转换视角
                if perspective:
                    chapter_result = self.change_perspective(to_perspective=perspective)
                
                # 修改风格（使用统一接口，传入章节上下文）
                if style:
                    chapter_context = None
                    if novel_context:
                        # 获取当前章节的上下文
                        try:
                            from scripts.ai.context_manager import NovelContextManager
                            context_manager = NovelContextManager()
                            chapter_context = context_manager.get_context_for_rewrite(
                                chapter_result,
                                chapter_num=i+1
                            )
                        except:
                            pass
                    
                    chapter_result = self.change_style(
                        style=style, 
                        use_ai=use_ai,
                        ai_type=ai_type,
                        novel_context=novel_context,
                        chapter_context=chapter_context,
                        **ai_kwargs
                    )
                
                rewritten_chapters.append(chapter_result)
            
            result = '\n\n'.join(rewritten_chapters)
            
            # 验证整本书的一致性
            if maintain_consistency:
                try:
                    from scripts.ai.consistency_checker import ConsistencyChecker
                    checker = ConsistencyChecker()
                    checker.analyze_novel(self.content)
                    is_consistent, issues = checker.validate_rewritten_novel(
                        chapters, rewritten_chapters
                    )
                    if not is_consistent:
                        print(f"⚠️  整本书存在逻辑一致性问题: {len(issues)} 个问题")
                        for issue in issues[:5]:
                            print(f"    - {issue}")
                except Exception as e:
                    print(f"⚠️  一致性检查失败: {e}")
        else:
            # 单章节或短文本处理
            # 替换姓名
            if replace_names:
                result = self.replace_character_names(replace_names=True)
            
            # 转换视角
            if perspective:
                result = self.change_perspective(to_perspective=perspective)
            
            # 修改风格（使用统一接口）
            if style:
                result = self.change_style(
                    style=style, 
                    use_ai=use_ai,
                    ai_type=ai_type,
                    novel_context=novel_context,
                    **ai_kwargs
                )
        
        # 保存结果
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"\n✅ 改写完成，已保存到: {self.output_file}")
            
            # 保存分析报告（如果进行了分析）
            if self.analyzer:
                report_file = os.path.splitext(self.output_file)[0] + '_analysis.json'
                report = {
                    'characters': {name: {'count': info['count'], 'role': info['role']} 
                                 for name, info in self.analyzer.characters.items()},
                    'summary': self.analyzer.generate_summary(),
                    'name_mapping': self.name_mapper.name_mapping if replace_names else {}
                }
                with open(report_file, 'w', encoding='utf-8') as f:
                    json.dump(report, f, ensure_ascii=False, indent=2)
                print(f"📊 分析报告已保存到: {report_file}")
            
            return True
        except Exception as e:
            print(f"❌ 保存失败: {e}")
            return False


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python3 rewrite_novel.py <输入文件> [输出文件] [选项]")
        print("\n基础选项:")
        print("  --perspective=第一人称/第三人称  # 转换人称视角")
        print("  --style=风格名称  # 修改风格")
        print("    基础风格：现代/古典/简洁/华丽/悬疑/浪漫/幽默/严肃")
        print("    扩展风格：科幻/武侠/青春/都市/古风/诗化/口语/正式/网络/文艺")
        print("  --replace-names                    # 替换人物姓名")
        print("  --no-analyze                      # 跳过小说分析（更快但功能受限）")
        print("  --output-dir=rewritten            # 输出文件夹名称")
        print("\nAI选项（需要配置API密钥）:")
        print("  --use-ai                          # 启用AI分析（需要OPENAI_API_KEY环境变量）")
        print("  --ai-type=openai/local/tensorflow  # AI类型")
        print("                                     #   openai: OpenAI API（需要API密钥）")
        print("                                     #   local: 本地LLM（Ollama等）")
        print("                                     #   tensorflow: TensorFlow本地模型（推荐，完全本地）")
        print("  --ai-model=gpt-4                  # AI模型名称（仅openai，推荐gpt-4）")
        print("  --ai-model-path=models/text_rewriter  # TensorFlow模型路径（仅tensorflow）")
        print("  --ai-base-url=http://localhost:11434  # 本地LLM服务地址（仅local）")
        print("\n示例:")
        print("  # 传统方法")
        print("  python3 rewrite_novel.py novel.txt --perspective=第三人称 --style=简洁")
        print("  # 使用OpenAI AI分析")
        print("  python3 rewrite_novel.py novel.txt --use-ai --ai-type=openai --style=悬疑")
        print("  # 使用本地LLM")
        print("  python3 rewrite_novel.py novel.txt --use-ai --ai-type=local --ai-model=llama2")
        print("\n说明:")
        print("  - 改写后的文件会保存在输入文件所在目录的 rewritten/ 文件夹中")
        print("  - 使用AI需要设置OPENAI_API_KEY环境变量或配置本地LLM服务")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = None
    perspective = None
    style = None
    replace_names = False
    analyze = True
    output_dir = "rewritten"
    use_ai = False
    ai_type = "openai"
    ai_kwargs = {}
    
    # 解析参数
    for arg in sys.argv[2:]:
        if arg.startswith('--perspective='):
            perspective = arg.split('=')[1]
        elif arg.startswith('--style='):
            style = arg.split('=')[1]
        elif arg == '--replace-names':
            replace_names = True
        elif arg == '--no-analyze':
            analyze = False
        elif arg == '--use-ai':
            use_ai = True
        elif arg.startswith('--ai-type='):
            ai_type = arg.split('=')[1]
        elif arg.startswith('--ai-model='):
            ai_kwargs['model'] = arg.split('=')[1]
        elif arg.startswith('--ai-model-path='):
            ai_kwargs['model_path'] = arg.split('=')[1]
        elif arg.startswith('--ai-base-url='):
            ai_kwargs['base_url'] = arg.split('=')[1]
        elif arg.startswith('--output-dir='):
            output_dir = arg.split('=')[1]
        elif not arg.startswith('--'):
            output_file = arg
    
    rewriter = NovelRewriter(input_file, output_file, output_dir=output_dir)
    
    if rewriter.rewrite(perspective=perspective, style=style, 
                       replace_names=replace_names, analyze=analyze,
                       use_ai=use_ai, ai_type=ai_type, **ai_kwargs):
        print("\n✅ 改写完成！")
        print(f"📁 文件已保存到: {rewriter.output_file}")
    else:
        print("\n❌ 改写失败！")
        sys.exit(1)


if __name__ == '__main__':
    main()
