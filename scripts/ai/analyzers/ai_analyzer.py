#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI分析器模块
支持多种AI服务进行小说分析和理解
"""

import os
import json
import re
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod


class AIAnalyzerBase(ABC):
    """AI分析器基类"""
    
    @abstractmethod
    def analyze_characters(self, content: str) -> Dict[str, Dict]:
        """分析人物"""
        pass
    
    @abstractmethod
    def analyze_storyline(self, content: str) -> Dict:
        """分析故事脉络"""
        pass
    
    @abstractmethod
    def analyze_plot(self, content: str) -> Dict:
        """分析情节结构"""
        pass
    
    @abstractmethod
    def rewrite_text(self, text: str, style: str, perspective: Optional[str] = None) -> str:
        """改写文本"""
        pass


class OpenAIAnalyzer(AIAnalyzerBase):
    """OpenAI API分析器"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        初始化OpenAI分析器
        
        Args:
            api_key: OpenAI API密钥
            model: 使用的模型名称
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        
        if not self.api_key:
            raise ValueError("需要设置OPENAI_API_KEY环境变量或传入api_key参数")
        
        try:
            import openai
            self.client = openai.OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("请安装openai库: pip install openai")
    
    def _call_api(self, prompt: str, system_prompt: Optional[str] = None, max_tokens: int = 2000) -> str:
        """调用OpenAI API"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"⚠️  API调用失败: {e}")
            return ""
    
    def analyze_characters(self, content: str) -> Dict[str, Dict]:
        """使用AI分析人物"""
        # 截取部分内容进行分析（避免token过多）
        sample = content[:5000] if len(content) > 5000 else content
        
        prompt = f"""请分析以下小说片段中的人物，提取主要人物的信息。

小说片段：
{sample}

请以JSON格式返回，包含以下字段：
- characters: 人物列表，每个人物包含 name（姓名）、role（角色类型：主角/配角/次要角色）、description（人物描述）、importance（重要性：1-10）

返回格式示例：
{{
  "characters": [
    {{
      "name": "陈旭",
      "role": "主角",
      "description": "32岁，即将结婚的男性",
      "importance": 10
    }}
  ]
}}
"""
        
        system_prompt = "你是一个专业的小说分析专家，擅长分析小说中的人物、情节和主题。"
        
        response = self._call_api(prompt, system_prompt, max_tokens=2000)
        
        # 解析JSON响应
        try:
            result = json.loads(response)
            characters = {}
            for char in result.get('characters', []):
                name = char.get('name', '')
                if name:
                    characters[name] = {
                        'name': name,
                        'role': char.get('role', '配角'),
                        'description': char.get('description', ''),
                        'importance': char.get('importance', 5),
                        'count': content.count(name)
                    }
            return characters
        except:
            return {}
    
    def analyze_storyline(self, content: str) -> Dict:
        """使用AI分析故事脉络"""
        # 提取章节标题和开头
        chapters = []
        chapter_pattern = r'第\s*(\d+)\s*章[：:：]?\s*(.*?)\n'
        
        for match in re.finditer(chapter_pattern, content):
            chapter_num = int(match.group(1))
            chapter_title = match.group(2).strip() if match.group(2) else f"第{chapter_num}章"
            start_pos = match.end()
            end_pos = min(start_pos + 500, len(content))
            chapter_content = content[start_pos:end_pos]
            
            chapters.append({
                'num': chapter_num,
                'title': chapter_title,
                'summary': chapter_content[:200]
            })
        
        # 选择代表性章节
        sample_chapters = chapters[:10] + chapters[len(chapters)//2:len(chapters)//2+5] + chapters[-10:]
        
        prompt = f"""请分析以下小说的故事脉络和主题。

章节信息：
{json.dumps(sample_chapters, ensure_ascii=False, indent=2)}

请分析：
1. 故事的主要主题和核心冲突
2. 故事的发展脉络（开端、发展、高潮、结尾）
3. 关键转折点
4. 故事的情感基调

请以JSON格式返回分析结果。
"""
        
        system_prompt = "你是一个专业的小说分析专家。"
        
        response = self._call_api(prompt, system_prompt, max_tokens=1500)
        
        try:
            return json.loads(response)
        except:
            return {'theme': '', 'structure': '', 'turning_points': [], 'tone': ''}
    
    def analyze_plot(self, content: str) -> Dict:
        """使用AI分析情节结构"""
        return self.analyze_storyline(content)
    
    def rewrite_text(self, text: str, style: str, perspective: Optional[str] = None, context: Optional[str] = None) -> str:
        """
        使用AI改写文本（深度学习优化版）
        
        Args:
            text: 要改写的文本
            style: 目标风格
            perspective: 目标视角
            context: 上下文信息（可选，用于更好的理解）
        """
        # 截取文本（避免token过多），但保留更多上下文
        if len(text) > 3000:
            # 如果文本很长，取前3000字符，但要尽量保持句子完整
            sample = text[:3000]
            # 找到最后一个句号，保持句子完整
            last_period = sample.rfind('。')
            last_exclamation = sample.rfind('！')
            last_question = sample.rfind('？')
            last_sentence_end = max(last_period, last_exclamation, last_question)
            if last_sentence_end > 2000:  # 如果找到的句子结束位置合理
                sample = text[:last_sentence_end + 1]
        else:
            sample = text
        
        style_descriptions = {
            '现代': '现代简洁的语言风格',
            '古典': '古典文雅的文言文风格',
            '简洁': '简洁明了的表达方式',
            '华丽': '华丽优美的辞藻',
            '悬疑': '悬疑紧张的氛围',
            '浪漫': '浪漫温馨的描写',
            '幽默': '幽默风趣的表达',
            '严肃': '严肃庄重的语调',
            '科幻': '科幻未来感的风格，充满科技元素',
            '武侠': '武侠小说的风格，充满江湖气息',
            '青春': '青春活泼的风格，轻松明快',
            '都市': '现代都市生活的风格，充满都市气息和现代感',
            '都市幽默': '都市风格与幽默风格的结合，既有都市感又充满幽默风趣',
            '都市+幽默': '都市风格与幽默风格的结合',
            '都市、幽默': '都市风格与幽默风格的结合',
            '古风': '古代文雅的风格',
            '诗化': '诗意化的表达，充满文学美感',
            '口语': '口语化的表达，贴近日常对话',
            '正式': '正式书面语的风格',
            '网络': '网络用语风格，轻松活泼',
            '文艺': '文艺范的风格，充满文学气息'
        }
        
        perspective_desc = f"，转换为{perspective}视角" if perspective else ""
        
        # 处理组合风格
        if '+' in style or '、' in style or '，' in style:
            styles = re.split(r'[+、，]', style)
            style_desc = '和'.join([style_descriptions.get(s.strip(), s.strip()) for s in styles])
        else:
            style_desc = style_descriptions.get(style, style)
        
        # 构建上下文信息
        context_info = ""
        if context:
            context_info = f"\n\n上下文信息：\n{context[:500]}"
        
        prompt = f"""你是一位资深的文本改写专家和语言优化大师，擅长使用深度学习技术进行自然语言处理和文本优化。

## 任务
请将以下文本改写为{style_desc}{perspective_desc}，并进行深度语言优化。

## 原文
{sample}{context_info}

## 改写要求（核心原则）

### 1. 深度理解文本
- **语义理解**：深入理解文本的语义、情感和语境
- **上下文连贯**：确保改写后的文本与上下文自然衔接
- **人物性格**：保持人物性格和说话风格的一致性
- **故事逻辑**：绝对不能改变故事情节、事件发展和逻辑关系

### 2. 自然流畅的语言优化
- **自然表达**：改写后的文本必须像人类自然写作一样流畅
- **避免机械化**：绝对不能进行简单的词汇替换，要理解后再改写
- **语言质量**：使用更生动、更精准、更符合风格特点的表达
- **流畅度**：确保每个句子都读起来自然顺畅，没有生硬感

### 3. 风格的自然融合
- **风格融入**：将{style_desc}的特点自然地融入到文本中
- **避免标签化**：不要生硬地插入风格关键词，要让风格体现在整体表达中
- **适度原则**：不要为了体现风格而过度修改，保持文本的连贯性
- **风格一致性**：确保整个文本的风格保持一致

### 4. 深度学习优化策略
- **语义分析**：分析文本的深层语义，理解作者的意图
- **语境适配**：根据不同的语境选择合适的表达方式
- **语言模型**：使用自然语言生成技术，让改写更像人类写作
- **质量提升**：在保持原意的基础上，提升文本的语言质量和可读性

## 改写示例（参考）

**原文**：陈旭说："好的，我明白了。"

**都市幽默风格改写**：
- ❌ 错误示例：陈旭在都市的咖啡厅里说："好的，我明白了。"，哈哈（生硬插入）
- ✅ 正确示例：陈旭在繁华都市的咖啡厅里，轻松地笑着说："好的，我明白了。"（自然融合）

## 输出要求
1. 直接输出改写后的文本，不要添加任何解释
2. 保持原文的段落结构和格式
3. 确保改写后的文本自然流畅，读起来像原创作品
4. 如果原文是对话，保持对话的自然性

请开始改写（直接输出改写后的文本）：
"""
        
        system_prompt = f"你是一个专业的文本改写专家，擅长将文本改写为不同的风格和视角。"
        
        response = self._call_api(prompt, system_prompt, max_tokens=2500)
        return response if response else text


class LocalLLMAnalyzer(AIAnalyzerBase):
    """本地LLM分析器（支持Ollama等）"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        """
        初始化本地LLM分析器
        
        Args:
            base_url: Ollama服务地址
            model: 模型名称
        """
        self.base_url = base_url
        self.model = model
        self.available = False
        
        # 检查服务是否可用
        try:
            import requests
            response = requests.get(f"{base_url}/api/tags", timeout=2)
            if response.status_code == 200:
                self.available = True
                print(f"✅ 本地LLM服务连接成功: {base_url}")
            else:
                print(f"⚠️  本地LLM服务不可用: {base_url}")
        except:
            print(f"⚠️  无法连接到本地LLM服务: {base_url}")
    
    def _call_api(self, prompt: str) -> str:
        """调用本地LLM API"""
        if not self.available:
            return ""
        
        try:
            import requests
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            if response.status_code == 200:
                return response.json().get('response', '')
        except Exception as e:
            print(f"⚠️  本地LLM调用失败: {e}")
        
        return ""
    
    def analyze_characters(self, content: str) -> Dict[str, Dict]:
        """分析人物（简化版）"""
        # 本地模型的分析逻辑可以简化
        return {}
    
    def analyze_storyline(self, content: str) -> Dict:
        """分析故事脉络"""
        return {}
    
    def analyze_plot(self, content: str) -> Dict:
        """分析情节结构"""
        return {}
    
    def rewrite_text(self, text: str, style: str, perspective: Optional[str] = None, context: Optional[str] = None) -> str:
        """改写文本（支持上下文）"""
        context_info = f"\n\n上下文：\n{context}" if context else ""
        prompt = f"""请将以下文本改写为{style}风格，要求自然流畅，不能生硬替换：

{text[:2000]}{context_info}

请直接输出改写后的文本："""
        return self._call_api(prompt) or text


class AIAnalyzerFactory:
    """AI分析器工厂类"""
    
    @staticmethod
    def create_analyzer(analyzer_type: str = "openai", **kwargs) -> Optional[AIAnalyzerBase]:
        """
        创建AI分析器
        
        Args:
            analyzer_type: 分析器类型（openai/local/tensorflow/offline）
            **kwargs: 其他参数
        
        Returns:
            AI分析器实例
        """
        if analyzer_type == "openai":
            try:
                return OpenAIAnalyzer(
                    api_key=kwargs.get('api_key'),
                    model=kwargs.get('model', 'gpt-3.5-turbo')
                )
            except Exception as e:
                print(f"⚠️  无法创建OpenAI分析器: {e}")
                return None
        
        elif analyzer_type == "local":
            try:
                return LocalLLMAnalyzer(
                    base_url=kwargs.get('base_url', 'http://localhost:11434'),
                    model=kwargs.get('model', 'llama2')
                )
            except Exception as e:
                print(f"⚠️  无法创建本地LLM分析器: {e}")
                return None
        
        elif analyzer_type == "tensorflow":
            try:
                import sys
                import os
                sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'models'))
                from tensorflow_model import TensorFlowAnalyzer
                model_path = kwargs.get('model_path', 'models/text_rewriter_model')
                analyzer = TensorFlowAnalyzer(model_path=model_path)
                if analyzer.load_model():
                    print("✅ TensorFlow模型加载成功")
                    return analyzer
                else:
                    print("⚠️  TensorFlow模型未找到，请先训练模型")
                    print("   运行: python3 scripts/creative/train_model.py <训练数据>")
                    return None
            except ImportError as e:
                print(f"⚠️  无法导入TensorFlow模块: {e}")
                print("   请安装: pip install tensorflow")
                return None
            except Exception as e:
                print(f"⚠️  无法创建TensorFlow分析器: {e}")
                return None
        
        elif analyzer_type == "huggingface":
            try:
                import sys
                import os
                sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'models'))
                from huggingface_analyzer import HuggingFaceAnalyzer
                model_path = kwargs.get('model_path', 'models/pretrained/Qwen_Qwen-7B-Chat')
                model_type = kwargs.get('model_type', 'auto')
                analyzer = HuggingFaceAnalyzer(model_path=model_path, model_type=model_type)
                print("✅ HuggingFace模型加载成功")
                return analyzer
            except ImportError as e:
                print(f"⚠️  无法导入HuggingFace模块: {e}")
                print("   请安装: pip install transformers torch huggingface_hub")
                return None
            except Exception as e:
                print(f"⚠️  无法创建HuggingFace分析器: {e}")
                print("   提示: 请先下载模型")
                print("   运行: python3 scripts/ai/models/model_downloader.py download --model qwen-7b-chat")
                return None
        
        elif analyzer_type == "offline":
            # 返回None，使用传统方法
            return None
        
        return None

