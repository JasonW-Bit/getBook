#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HuggingFace模型集成
将下载的HuggingFace模型集成到项目中，用于文本改写
"""

import os
import sys
from typing import Optional, Dict, List
import torch


class HuggingFaceTextRewriter:
    """基于HuggingFace模型的文本改写器"""
    
    def __init__(self, model_path: str, model_type: str = 'auto'):
        """
        初始化HuggingFace文本改写器
        
        Args:
            model_path: 模型路径（本地路径或HuggingFace模型ID）
            model_type: 模型类型（'auto', 'chatglm', 'qwen', 'baichuan'等）
        """
        self.model_path = model_path
        self.model_type = model_type
        self.model = None
        self.tokenizer = None
        self.device = self._get_device()
        
        # 加载模型
        self._load_model()
    
    def _get_device(self) -> str:
        """获取可用设备"""
        if torch.cuda.is_available():
            return 'cuda'
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            return 'mps'  # Apple Silicon
        else:
            return 'cpu'
    
    def _load_model(self):
        """加载模型和分词器"""
        try:
            from transformers import AutoTokenizer, AutoModel, AutoModelForCausalLM
            
            print(f"📥 加载模型: {self.model_path}")
            print(f"   设备: {self.device}")
            
            # 根据模型类型选择加载方式
            if 'chatglm' in self.model_path.lower() or 'chatglm' in self.model_type.lower():
                self._load_chatglm()
            elif 'qwen' in self.model_path.lower() or 'qwen' in self.model_type.lower():
                self._load_qwen()
            elif 'baichuan' in self.model_path.lower() or 'baichuan' in self.model_type.lower():
                self._load_baichuan()
            else:
                # 自动检测
                self._load_auto()
            
            print("✅ 模型加载完成")
            
        except ImportError:
            print("❌ 需要安装 transformers 和 torch")
            print("   运行: pip install transformers torch")
            raise
        except Exception as e:
            print(f"❌ 模型加载失败: {e}")
            raise
    
    def _load_chatglm(self):
        """加载ChatGLM模型"""
        from transformers import AutoTokenizer, AutoModel
        
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_path,
            trust_remote_code=True
        )
        self.model = AutoModel.from_pretrained(
            self.model_path,
            trust_remote_code=True,
            device_map='auto' if self.device != 'cpu' else None
        )
        
        if self.device == 'cpu':
            self.model = self.model.float()
        else:
            self.model = self.model.half()
        
        self.model.eval()
    
    def _load_qwen(self):
        """加载Qwen模型"""
        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_path,
            trust_remote_code=True
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            trust_remote_code=True,
            device_map='auto' if self.device != 'cpu' else None,
            torch_dtype=torch.float16 if self.device != 'cpu' else torch.float32
        )
        self.model.eval()
    
    def _load_baichuan(self):
        """加载Baichuan模型"""
        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_path,
            trust_remote_code=True
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            trust_remote_code=True,
            device_map='auto' if self.device != 'cpu' else None,
            torch_dtype=torch.float16 if self.device != 'cpu' else torch.float32
        )
        self.model.eval()
    
    def _load_auto(self):
        """自动加载模型"""
        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                trust_remote_code=True
            )
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                trust_remote_code=True,
                device_map='auto' if self.device != 'cpu' else None,
                torch_dtype=torch.float16 if self.device != 'cpu' else torch.float32
            )
            self.model.eval()
        except:
            # 尝试加载为AutoModel
            from transformers import AutoModel
            self.model = AutoModel.from_pretrained(
                self.model_path,
                trust_remote_code=True,
                device_map='auto' if self.device != 'cpu' else None
            )
            if self.device == 'cpu':
                self.model = self.model.float()
            else:
                self.model = self.model.half()
            self.model.eval()
    
    def rewrite(self, text: str, style: Optional[str] = None, 
                context: Optional[str] = None, max_length: int = 512) -> str:
        """
        改写文本
        
        Args:
            text: 原始文本
            style: 风格（可选）
            context: 上下文（可选）
            max_length: 最大长度
        
        Returns:
            改写后的文本
        """
        # 构建提示词
        prompt = self._build_prompt(text, style, context)
        
        # 根据模型类型选择生成方式
        if 'chatglm' in self.model_type.lower() or hasattr(self.model, 'chat'):
            return self._generate_chatglm(prompt, max_length)
        else:
            return self._generate_standard(prompt, max_length)
    
    def _build_prompt(self, text: str, style: Optional[str] = None, 
                     context: Optional[str] = None) -> str:
        """构建提示词"""
        prompt_parts = []
        
        if context:
            prompt_parts.append(f"上下文：{context}")
        
        if style:
            prompt_parts.append(f"风格：{style}")
        
        prompt_parts.append(f"请改写以下文本，保持原意但使表达更加生动自然：")
        prompt_parts.append(text)
        
        return "\n".join(prompt_parts)
    
    def _generate_chatglm(self, prompt: str, max_length: int) -> str:
        """使用ChatGLM生成"""
        if hasattr(self.model, 'chat'):
            response, _ = self.model.chat(
                self.tokenizer,
                prompt,
                history=[],
                max_length=max_length,
                temperature=0.7
            )
            return response
        else:
            return self._generate_standard(prompt, max_length)
    
    def _generate_standard(self, prompt: str, max_length: int) -> str:
        """标准生成方式"""
        inputs = self.tokenizer(prompt, return_tensors="pt", padding=True, truncation=True)
        
        if self.device != 'cpu':
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # 提取生成的部分（去除提示词）
        if prompt in generated_text:
            generated_text = generated_text.replace(prompt, "").strip()
        
        return generated_text
    
    def analyze(self, text: str) -> Dict:
        """分析文本"""
        # 可以在这里添加文本分析功能
        return {}


def main():
    """测试函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='HuggingFace模型测试')
    parser.add_argument('--model-path', required=True, help='模型路径')
    parser.add_argument('--text', help='要改写的文本')
    parser.add_argument('--style', help='风格')
    
    args = parser.parse_args()
    
    rewriter = HuggingFaceTextRewriter(args.model_path)
    
    if args.text:
        result = rewriter.rewrite(args.text, style=args.style)
        print(f"\n改写结果:\n{result}")
    else:
        print("✅ 模型加载成功，可以使用 rewrite() 方法进行改写")


if __name__ == '__main__':
    main()

