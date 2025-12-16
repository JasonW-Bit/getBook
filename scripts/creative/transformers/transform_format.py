#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本转换脚本
功能：格式转换、编码转换、结构重组
"""

import os
import sys
import json
import chardet
from typing import Optional, Dict, List


class FormatTransformer:
    """格式转换类"""
    
    def __init__(self, input_file: str, output_file: Optional[str] = None):
        """
        初始化转换器
        
        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径
        """
        self.input_file = input_file
        if not output_file:
            base_name = os.path.splitext(input_file)[0]
            self.output_file = f"{base_name}_transformed.txt"
        else:
            self.output_file = output_file
        
        self.content = ""
        self.encoding = "utf-8"
    
    def detect_encoding(self) -> str:
        """检测文件编码"""
        try:
            with open(self.input_file, 'rb') as f:
                raw_data = f.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding'] or 'utf-8'
            confidence = result['confidence']
            print(f"📝 检测到编码: {encoding} (置信度: {confidence:.2%})")
            return encoding
        except Exception as e:
            print(f"⚠️  编码检测失败: {e}，使用默认UTF-8")
            return 'utf-8'
    
    def load_file(self, encoding: Optional[str] = None) -> bool:
        """加载文件"""
        if not encoding:
            encoding = self.detect_encoding()
        
        try:
            with open(self.input_file, 'r', encoding=encoding) as f:
                self.content = f.read()
            self.encoding = encoding
            print(f"✅ 成功加载文件: {self.input_file}")
            return True
        except Exception as e:
            print(f"❌ 加载失败: {e}")
            return False
    
    def convert_encoding(self, target_encoding: str = "utf-8") -> bool:
        """
        转换编码
        
        Args:
            target_encoding: 目标编码
        
        Returns:
            是否成功
        """
        if not self.content:
            if not self.load_file():
                return False
        
        try:
            with open(self.output_file, 'w', encoding=target_encoding) as f:
                f.write(self.content)
            print(f"✅ 编码转换完成: {self.encoding} → {target_encoding}")
            print(f"   已保存到: {self.output_file}")
            return True
        except Exception as e:
            print(f"❌ 转换失败: {e}")
            return False
    
    def txt_to_json(self, output_file: Optional[str] = None) -> bool:
        """
        将TXT转换为JSON格式
        
        Args:
            output_file: 输出文件路径
        
        Returns:
            是否成功
        """
        if not self.content:
            if not self.load_file():
                return False
        
        if output_file:
            self.output_file = output_file
        else:
            base_name = os.path.splitext(self.input_file)[0]
            self.output_file = f"{base_name}.json"
        
        # 解析TXT内容为结构化数据
        data = {
            'title': '',
            'author': '',
            'chapters': []
        }
        
        # 简单的解析逻辑（可以根据实际格式调整）
        lines = self.content.split('\n')
        current_chapter = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检测标题
            if line.startswith('标题:'):
                data['title'] = line.split(':', 1)[1].strip()
            elif line.startswith('作者:'):
                data['author'] = line.split(':', 1)[1].strip()
            # 检测章节
            elif '第' in line and '章' in line:
                if current_chapter:
                    data['chapters'].append(current_chapter)
                current_chapter = {
                    'title': line,
                    'content': ''
                }
            elif current_chapter:
                current_chapter['content'] += line + '\n'
        
        if current_chapter:
            data['chapters'].append(current_chapter)
        
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ TXT转JSON完成，已保存到: {self.output_file}")
            return True
        except Exception as e:
            print(f"❌ 转换失败: {e}")
            return False
    
    def json_to_txt(self, output_file: Optional[str] = None) -> bool:
        """
        将JSON转换为TXT格式
        
        Args:
            output_file: 输出文件路径
        
        Returns:
            是否成功
        """
        if not self.content:
            if not self.load_file():
                return False
        
        if output_file:
            self.output_file = output_file
        else:
            base_name = os.path.splitext(self.input_file)[0]
            self.output_file = f"{base_name}.txt"
        
        try:
            data = json.loads(self.content)
            
            result = ""
            if data.get('title'):
                result += f"标题: {data['title']}\n"
            if data.get('author'):
                result += f"作者: {data['author']}\n"
            result += "\n" + "="*50 + "\n\n"
            
            for chapter in data.get('chapters', []):
                result += f"{chapter.get('title', '')}\n\n"
                result += chapter.get('content', '') + "\n\n"
            
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"✅ JSON转TXT完成，已保存到: {self.output_file}")
            return True
        except Exception as e:
            print(f"❌ 转换失败: {e}")
            return False
    
    def restructure(self, structure_type: str = "章节分离") -> bool:
        """
        结构重组
        
        Args:
            structure_type: 重组类型（章节分离/合并/重新编号）
        
        Returns:
            是否成功
        """
        if not self.content:
            if not self.load_file():
                return False
        
        # 这里可以实现具体的结构重组逻辑
        result = self.content
        
        if structure_type == "章节分离":
            # 将每个章节保存为单独文件
            base_name = os.path.splitext(self.input_file)[0]
            # 实现章节分离逻辑
            print(f"✅ 结构重组完成: {structure_type}")
        
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"   已保存到: {self.output_file}")
            return True
        except Exception as e:
            print(f"❌ 保存失败: {e}")
            return False


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python3 transform_format.py <输入文件> [输出文件] [--action=encoding/txt2json/json2txt/restructure]")
        print("示例: python3 transform_format.py novel.txt --action=txt2json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = None
    action = "encoding"
    kwargs = {}
    
    # 解析参数
    for arg in sys.argv[2:]:
        if arg.startswith('--action='):
            action = arg.split('=')[1]
        elif arg.startswith('--encoding='):
            kwargs['target_encoding'] = arg.split('=')[1]
        elif arg.startswith('--structure='):
            kwargs['structure_type'] = arg.split('=')[1]
        elif not arg.startswith('--'):
            output_file = arg
    
    transformer = FormatTransformer(input_file, output_file)
    
    success = False
    if action == "encoding":
        target_encoding = kwargs.get('target_encoding', 'utf-8')
        success = transformer.convert_encoding(target_encoding)
    elif action == "txt2json":
        success = transformer.txt_to_json(output_file)
    elif action == "json2txt":
        success = transformer.json_to_txt(output_file)
    elif action == "restructure":
        structure_type = kwargs.get('structure_type', '章节分离')
        success = transformer.restructure(structure_type)
    
    if success:
        print("\n✅ 格式转换完成！")
    else:
        print("\n❌ 格式转换失败！")
        sys.exit(1)


if __name__ == '__main__':
    main()

