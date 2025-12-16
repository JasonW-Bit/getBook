#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创意处理脚本
功能：添加创意元素、生成新内容、内容重组
"""

import os
import re
import sys
import random
from typing import List, Dict, Optional


class CreativeProcessor:
    """创意处理类"""
    
    def __init__(self, input_file: str, output_file: Optional[str] = None):
        """
        初始化创意处理器
        
        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径
        """
        self.input_file = input_file
        if not output_file:
            base_name = os.path.splitext(input_file)[0]
            self.output_file = f"{base_name}_creative.txt"
        else:
            self.output_file = output_file
        
        self.content = ""
        self.chapters = []
    
    def load_novel(self) -> bool:
        """加载小说内容"""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                self.content = f.read()
            
            # 分割章节
            self.chapters = self._split_chapters()
            print(f"✅ 成功加载小说: {self.input_file}")
            print(f"   共 {len(self.chapters)} 个章节")
            return True
        except Exception as e:
            print(f"❌ 加载失败: {e}")
            return False
    
    def _split_chapters(self) -> List[Dict]:
        """分割章节"""
        chapters = []
        # 匹配章节标题（如：第X章、第 X 章等）
        pattern = r'第\s*(\d+)\s*章[：:：]?\s*(.*?)\n'
        matches = list(re.finditer(pattern, self.content))
        
        for i, match in enumerate(matches):
            chapter_num = match.group(1)
            chapter_title = match.group(2) if match.group(2) else f"第{chapter_num}章"
            start_pos = match.end()
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(self.content)
            
            chapters.append({
                'num': int(chapter_num),
                'title': chapter_title,
                'content': self.content[start_pos:end_pos].strip()
            })
        
        return chapters
    
    def add_creative_elements(self, elements: List[str]) -> str:
        """
        添加创意元素
        
        Args:
            elements: 创意元素列表（如：['悬疑', '反转', '伏笔']）
        
        Returns:
            处理后的内容
        """
        result = self.content
        
        # 这里可以添加具体的创意元素处理逻辑
        # 例如：添加伏笔、设置悬念、增加反转等
        
        print(f"✅ 已添加创意元素: {', '.join(elements)}")
        return result
    
    def generate_new_content(self, chapter_num: int, content_type: str = "扩展") -> str:
        """
        生成新内容
        
        Args:
            chapter_num: 章节号
            content_type: 内容类型（扩展/补充/续写）
        
        Returns:
            生成的新内容
        """
        # 这里可以集成AI生成、模板填充等功能
        # 目前返回示例内容
        
        templates = {
            "扩展": "【扩展内容】这里可以添加更详细的描述和情节发展...",
            "补充": "【补充内容】这里可以补充背景信息和细节...",
            "续写": "【续写内容】故事继续发展...",
        }
        
        new_content = templates.get(content_type, "【新内容】")
        print(f"✅ 已生成新内容（第{chapter_num}章，类型：{content_type}）")
        return new_content
    
    def reorganize_content(self, method: str = "时间顺序") -> str:
        """
        内容重组
        
        Args:
            method: 重组方法（时间顺序/倒序/打乱/主题分组）
        
        Returns:
            重组后的内容
        """
        if not self.chapters:
            self._split_chapters()
        
        result = ""
        
        if method == "时间顺序":
            # 按章节号排序
            sorted_chapters = sorted(self.chapters, key=lambda x: x['num'])
            for ch in sorted_chapters:
                result += f"第{ch['num']}章: {ch['title']}\n\n{ch['content']}\n\n"
        
        elif method == "倒序":
            # 倒序排列
            sorted_chapters = sorted(self.chapters, key=lambda x: x['num'], reverse=True)
            for ch in sorted_chapters:
                result += f"第{ch['num']}章: {ch['title']}\n\n{ch['content']}\n\n"
        
        elif method == "打乱":
            # 随机打乱
            shuffled = self.chapters.copy()
            random.shuffle(shuffled)
            for ch in shuffled:
                result += f"第{ch['num']}章: {ch['title']}\n\n{ch['content']}\n\n"
        
        print(f"✅ 内容重组完成: {method}")
        return result
    
    def process(self, action: str, **kwargs) -> bool:
        """
        执行创意处理
        
        Args:
            action: 处理动作（add_elements/generate/reorganize）
            **kwargs: 其他参数
        
        Returns:
            是否成功
        """
        if not self.content:
            if not self.load_novel():
                return False
        
        result = self.content
        
        if action == "add_elements":
            elements = kwargs.get('elements', [])
            result = self.add_creative_elements(elements)
        
        elif action == "generate":
            chapter_num = kwargs.get('chapter_num', 1)
            content_type = kwargs.get('content_type', '扩展')
            new_content = self.generate_new_content(chapter_num, content_type)
            # 这里可以将新内容插入到指定位置
        
        elif action == "reorganize":
            method = kwargs.get('method', '时间顺序')
            result = self.reorganize_content(method)
        
        # 保存结果
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"✅ 处理完成，已保存到: {self.output_file}")
            return True
        except Exception as e:
            print(f"❌ 保存失败: {e}")
            return False


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python3 creative_process.py <输入文件> [输出文件] [--action=add_elements/generate/reorganize]")
        print("示例: python3 creative_process.py novel.txt --action=reorganize --method=倒序")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = None
    action = "reorganize"
    kwargs = {}
    
    # 解析参数
    for arg in sys.argv[2:]:
        if arg.startswith('--action='):
            action = arg.split('=')[1]
        elif arg.startswith('--method='):
            kwargs['method'] = arg.split('=')[1]
        elif arg.startswith('--elements='):
            kwargs['elements'] = arg.split('=')[1].split(',')
        elif arg.startswith('--chapter='):
            kwargs['chapter_num'] = int(arg.split('=')[1])
        elif not arg.startswith('--'):
            output_file = arg
    
    processor = CreativeProcessor(input_file, output_file)
    
    if processor.process(action, **kwargs):
        print("\n✅ 创意处理完成！")
    else:
        print("\n❌ 创意处理失败！")
        sys.exit(1)


if __name__ == '__main__':
    main()

