#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内容生成脚本
功能：生成新章节、内容扩展、创意生成
"""

import os
import sys
import json
import random
from typing import List, Dict, Optional

# 导入AI内容生成器
try:
    from .ai_content_generator import AIContentGenerator
    AI_GENERATOR_AVAILABLE = True
except ImportError:
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
        from ai_content_generator import AIContentGenerator
        AI_GENERATOR_AVAILABLE = True
    except ImportError:
        AI_GENERATOR_AVAILABLE = False
        AIContentGenerator = None


class ContentGenerator:
    """内容生成类"""
    
    def __init__(self, input_file: Optional[str] = None, output_file: Optional[str] = None):
        """
        初始化生成器
        
        Args:
            input_file: 输入文件路径（可选，用于基于现有内容生成）
            output_file: 输出文件路径
        """
        self.input_file = input_file
        if not output_file:
            if input_file:
                base_name = os.path.splitext(input_file)[0]
                self.output_file = f"{base_name}_generated.txt"
            else:
                self.output_file = "generated_novel.txt"
        else:
            self.output_file = output_file
        
        self.content = ""
        self.chapters = []
        self.templates = {
            '开头': [
                "在一个平凡的日子里，",
                "故事从这里开始，",
                "很久很久以前，",
                "那是一个不寻常的夜晚，",
            ],
            '发展': [
                "然而，事情并没有那么简单。",
                "就在这时，意外发生了。",
                "命运的齿轮开始转动。",
                "真相渐渐浮出水面。",
            ],
            '结尾': [
                "故事还在继续...",
                "这就是一切的开始。",
                "新的冒险即将展开。",
                "命运的转折点已经到来。",
            ]
        }
    
    def load_novel(self) -> bool:
        """加载小说内容"""
        if not self.input_file:
            return False
        
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                self.content = f.read()
            
            # 解析章节
            self.chapters = self._parse_chapters()
            print(f"✅ 成功加载小说: {self.input_file}")
            print(f"   共 {len(self.chapters)} 个章节")
            return True
        except Exception as e:
            print(f"❌ 加载失败: {e}")
            return False
    
    def _parse_chapters(self) -> List[Dict]:
        """解析章节"""
        chapters = []
        import re
        
        pattern = r'第\s*(\d+)\s*章[：:：]?\s*(.*?)\n'
        matches = list(re.finditer(pattern, self.content))
        
        for i, match in enumerate(matches):
            chapter_num = int(match.group(1))
            chapter_title = match.group(2).strip() if match.group(2) else f"第{chapter_num}章"
            start_pos = match.end()
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(self.content)
            
            chapters.append({
                'num': chapter_num,
                'title': chapter_title,
                'content': self.content[start_pos:end_pos].strip()
            })
        
        return chapters
    
    def generate_new_chapter(self, chapter_num: int, title: Optional[str] = None, 
                            style: str = "延续",
                            use_ai: bool = True,
                            ai_type: str = "tensorflow",
                            ai_model_path: Optional[str] = None) -> Dict:
        """
        生成新章节（支持AI生成）
        
        Args:
            chapter_num: 章节号
            title: 章节标题（可选）
            style: 生成风格（延续/转折/新起点）
            use_ai: 是否使用AI生成
            ai_type: AI类型
            ai_model_path: AI模型路径
        
        Returns:
            生成的章节内容
        """
        if not title:
            title = f"第{chapter_num}章"
        
        # 优先使用AI生成（如果可用）
        if use_ai and AI_GENERATOR_AVAILABLE and AIContentGenerator:
            try:
                ai_generator = AIContentGenerator(
                    ai_type=ai_type,
                    ai_model_path=ai_model_path
                )
                
                # 准备之前的章节内容
                previous_chapters = [ch.get('content', '') for ch in self.chapters]
                
                # 使用AI生成
                chapter = ai_generator.generate_new_chapter(
                    previous_chapters=previous_chapters,
                    chapter_num=chapter_num,
                    title=title,
                    style=style,
                    maintain_consistency=True
                )
                
                if chapter.get('content'):
                    print(f"✅ AI已生成新章节: {title}")
                    if not chapter.get('consistent', True):
                        print(f"⚠️  章节存在逻辑问题，但已生成")
                    return chapter
            except Exception as e:
                print(f"⚠️  AI生成失败，使用传统方法: {e}")
        
        # 传统方法（降级）
        if self.chapters:
            last_chapter = self.chapters[-1]
            context = last_chapter.get('content', '')[:500]
        else:
            context = ""
        
        content = self._generate_chapter_content(context, style)
        
        chapter = {
            'num': chapter_num,
            'title': title,
            'content': content
        }
        
        print(f"✅ 已生成新章节: {title}")
        return chapter
    
    def _generate_chapter_content(self, context: str, style: str) -> str:
        """生成章节内容"""
        content = ""
        
        # 开头
        content += random.choice(self.templates['开头'])
        content += "\n\n"
        
        # 基于上下文生成（简化版）
        if context:
            content += f"【基于前文发展】\n\n"
        
        # 发展
        content += random.choice(self.templates['发展'])
        content += "\n\n"
        
        # 中间内容（可以扩展）
        content += "这里是章节的主要内容。可以根据需要扩展，添加对话、描写、情节发展等。\n\n"
        
        # 结尾
        content += random.choice(self.templates['结尾'])
        
        return content
    
    def expand_content(self, chapter_num: int, expansion_type: str = "细节",
                       use_ai: bool = True,
                       ai_type: str = "tensorflow",
                       ai_model_path: Optional[str] = None) -> str:
        """
        内容扩展（支持AI扩展）
        
        Args:
            chapter_num: 章节号
            expansion_type: 扩展类型（细节/对话/描写/情节）
            use_ai: 是否使用AI扩展
            ai_type: AI类型
            ai_model_path: AI模型路径
        
        Returns:
            扩展后的内容
        """
        if not self.chapters:
            if not self.load_novel():
                return ""
        
        # 找到对应章节
        chapter = None
        for ch in self.chapters:
            if ch['num'] == chapter_num:
                chapter = ch
                break
        
        if not chapter:
            print(f"⚠️  未找到第{chapter_num}章")
            return ""
        
        original_content = chapter['content']
        
        # 优先使用AI扩展（如果可用）
        if use_ai and AI_GENERATOR_AVAILABLE and AIContentGenerator:
            try:
                ai_generator = AIContentGenerator(
                    ai_type=ai_type,
                    ai_model_path=ai_model_path
                )
                
                # 获取上下文（前后章节）
                context = ""
                chapter_index = next((i for i, ch in enumerate(self.chapters) if ch['num'] == chapter_num), -1)
                if chapter_index > 0:
                    context += f"前文: {self.chapters[chapter_index-1].get('content', '')[-300:]}"
                if chapter_index < len(self.chapters) - 1:
                    context += f"后文: {self.chapters[chapter_index+1].get('content', '')[:300]}"
                
                # 使用AI扩展
                expanded = ai_generator.expand_content(
                    original_content=original_content,
                    expansion_type=expansion_type,
                    context=context,
                    maintain_consistency=True
                )
                
                if expanded and expanded != original_content:
                    print(f"✅ AI内容扩展完成（第{chapter_num}章，类型：{expansion_type}）")
                    return expanded
            except Exception as e:
                print(f"⚠️  AI扩展失败，使用传统方法: {e}")
        
        # 传统方法（降级）
        expansion = ""
        if expansion_type == "细节":
            expansion = "\n\n【细节扩展】这里可以添加更详细的环境描写、心理活动等。\n\n"
        elif expansion_type == "对话":
            expansion = "\n\n【对话扩展】\n\"这里可以添加角色之间的对话。\"\n\n"
        elif expansion_type == "描写":
            expansion = "\n\n【描写扩展】这里可以添加更丰富的场景描写、人物描写等。\n\n"
        elif expansion_type == "情节":
            expansion = "\n\n【情节扩展】这里可以添加新的情节发展、转折点等。\n\n"
        
        expanded_content = original_content + expansion
        print(f"✅ 内容扩展完成（第{chapter_num}章，类型：{expansion_type}）")
        return expanded_content
    
    def creative_generate(self, theme: str = "冒险", length: int = 1000) -> str:
        """
        创意生成
        
        Args:
            theme: 主题（冒险/爱情/悬疑/科幻等）
            length: 生成长度（字符数）
        
        Returns:
            生成的内容
        """
        themes = {
            '冒险': {
                'setting': '一个充满未知的世界',
                'character': '勇敢的冒险者',
                'goal': '寻找传说中的宝藏'
            },
            '爱情': {
                'setting': '一个浪漫的城市',
                'character': '两个相遇的人',
                'goal': '找到真爱'
            },
            '悬疑': {
                'setting': '一个神秘的案件',
                'character': '聪明的侦探',
                'goal': '揭开真相'
            },
            '科幻': {
                'setting': '未来的世界',
                'character': '探索者',
                'goal': '发现新世界'
            }
        }
        
        theme_info = themes.get(theme, themes['冒险'])
        
        content = f"""
【{theme}主题故事】

背景设定：{theme_info['setting']}

主要角色：{theme_info['character']}

目标：{theme_info['goal']}

故事开始：

{random.choice(self.templates['开头'])}
{theme_info['character']}踏上了{theme_info['goal']}的旅程。
在{theme_info['setting']}中，充满了未知和挑战。

{random.choice(self.templates['发展'])}
每一步都充满了危险，但也充满了希望。

{random.choice(self.templates['结尾'])}
"""
        
        # 扩展到指定长度
        while len(content) < length:
            content += "\n\n" + random.choice(self.templates['发展'])
        
        print(f"✅ 创意生成完成（主题：{theme}，长度：{len(content)}字符）")
        return content
    
    def save(self, content: str) -> bool:
        """保存内容"""
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 内容已保存到: {self.output_file}")
            return True
        except Exception as e:
            print(f"❌ 保存失败: {e}")
            return False


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python3 generate_content.py [输入文件] [输出文件] [--action=chapter/expand/creative]")
        print("示例: python3 generate_content.py novel.txt --action=chapter --chapter=10")
        print("示例: python3 generate_content.py --action=creative --theme=冒险 --length=2000")
        sys.exit(1)
    
    input_file = None
    output_file = None
    action = "chapter"
    kwargs = {}
    
    # 解析参数
    for arg in sys.argv[1:]:
        if arg.startswith('--action='):
            action = arg.split('=')[1]
        elif arg.startswith('--chapter='):
            kwargs['chapter_num'] = int(arg.split('=')[1])
        elif arg.startswith('--title='):
            kwargs['title'] = arg.split('=')[1]
        elif arg.startswith('--style='):
            kwargs['style'] = arg.split('=')[1]
        elif arg.startswith('--type='):
            kwargs['expansion_type'] = arg.split('=')[1]
        elif arg.startswith('--theme='):
            kwargs['theme'] = arg.split('=')[1]
        elif arg.startswith('--length='):
            kwargs['length'] = int(arg.split('=')[1])
        elif not arg.startswith('--'):
            if not input_file:
                input_file = arg
            elif not output_file:
                output_file = arg
    
    generator = ContentGenerator(input_file, output_file)
    
    success = False
    result = ""
    
    if action == "chapter":
        chapter_num = kwargs.get('chapter_num', 1)
        title = kwargs.get('title')
        style = kwargs.get('style', '延续')
        chapter = generator.generate_new_chapter(chapter_num, title, style)
        result = f"第{chapter['num']}章: {chapter['title']}\n\n{chapter['content']}\n"
        success = True
    
    elif action == "expand":
        if not input_file:
            print("❌ 扩展内容需要输入文件")
            sys.exit(1)
        chapter_num = kwargs.get('chapter_num', 1)
        expansion_type = kwargs.get('expansion_type', '细节')
        result = generator.expand_content(chapter_num, expansion_type)
        success = bool(result)
    
    elif action == "creative":
        theme = kwargs.get('theme', '冒险')
        length = kwargs.get('length', 1000)
        result = generator.creative_generate(theme, length)
        success = True
    
    if success and result:
        if generator.save(result):
            print("\n✅ 内容生成完成！")
        else:
            print("\n❌ 保存失败！")
            sys.exit(1)
    else:
        print("\n❌ 内容生成失败！")
        sys.exit(1)


if __name__ == '__main__':
    main()

