#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型下载器
从HuggingFace等平台下载和集成语言模型
"""

import os
import sys
import json
from typing import Optional, Dict, List
from pathlib import Path


class ModelDownloader:
    """模型下载器 - 支持从多个平台下载模型"""
    
    # 推荐的中文语言模型列表
    RECOMMENDED_MODELS = {
        'chatglm3-6b': {
            'name': 'THUDM/chatglm3-6b',
            'type': 'huggingface',
            'size': '12GB',
            'description': 'ChatGLM3-6B，清华大学开源的中文对话模型',
            'suitable_for': ['对话', '文本生成', '改写'],
            'min_memory': '16GB'
        },
        'qwen-7b-chat': {
            'name': 'Qwen/Qwen-7B-Chat',
            'type': 'huggingface',
            'size': '14GB',
            'description': '通义千问7B对话模型，阿里云开源',
            'suitable_for': ['对话', '文本生成', '改写', '创作'],
            'min_memory': '16GB'
        },
        'baichuan2-7b-chat': {
            'name': 'baichuan-inc/Baichuan2-7B-Chat',
            'type': 'huggingface',
            'size': '14GB',
            'description': '百川2-7B对话模型，百川智能开源',
            'suitable_for': ['对话', '文本生成', '改写'],
            'min_memory': '16GB'
        },
        'internlm-chat-7b': {
            'name': 'internlm/internlm-chat-7b',
            'type': 'huggingface',
            'size': '14GB',
            'description': '书生·浦语7B对话模型，上海AI Lab开源',
            'suitable_for': ['对话', '文本生成', '改写'],
            'min_memory': '16GB'
        },
        'qwen-1.8b-chat': {
            'name': 'Qwen/Qwen-1_8B-Chat',
            'type': 'huggingface',
            'size': '3.6GB',
            'description': '通义千问1.8B对话模型（轻量版）',
            'suitable_for': ['对话', '文本生成', '改写'],
            'min_memory': '8GB'
        },
        'chatglm2-6b': {
            'name': 'THUDM/chatglm2-6b',
            'type': 'huggingface',
            'size': '12GB',
            'description': 'ChatGLM2-6B，ChatGLM的升级版',
            'suitable_for': ['对话', '文本生成', '改写'],
            'min_memory': '16GB'
        }
    }
    
    def __init__(self, models_dir: str = "models/pretrained"):
        """
        初始化模型下载器
        
        Args:
            models_dir: 模型保存目录
        """
        self.models_dir = models_dir
        os.makedirs(self.models_dir, exist_ok=True)
    
    def list_available_models(self) -> Dict:
        """列出可用的模型"""
        return self.RECOMMENDED_MODELS
    
    def download_from_huggingface(self, model_name: str, local_dir: Optional[str] = None) -> bool:
        """
        从HuggingFace下载模型
        
        Args:
            model_name: 模型名称（如 'THUDM/chatglm3-6b'）
            local_dir: 本地保存目录
        
        Returns:
            是否成功
        """
        try:
            from transformers import AutoTokenizer, AutoModel, AutoModelForCausalLM
            from huggingface_hub import snapshot_download
        except ImportError:
            print("❌ 需要安装 transformers 和 huggingface_hub")
            print("   运行: pip install transformers huggingface_hub")
            return False
        
        if local_dir is None:
            # 使用模型名称作为目录名
            safe_name = model_name.replace('/', '_')
            local_dir = os.path.join(self.models_dir, safe_name)
        
        print(f"\n📥 开始下载模型: {model_name}")
        print(f"   保存到: {local_dir}")
        print(f"   这可能需要一些时间，请耐心等待...")
        
        try:
            # 下载模型
            snapshot_download(
                repo_id=model_name,
                local_dir=local_dir,
                local_dir_use_symlinks=False
            )
            
            print(f"\n✅ 模型下载完成: {local_dir}")
            return True
            
        except Exception as e:
            print(f"\n❌ 下载失败: {e}")
            print(f"   提示:")
            print(f"   1. 检查网络连接")
            print(f"   2. 确保有足够的磁盘空间")
            print(f"   3. 如果使用HuggingFace，可能需要登录: huggingface-cli login")
            return False
    
    def download_recommended_model(self, model_key: str) -> bool:
        """
        下载推荐的模型
        
        Args:
            model_key: 模型键名（如 'qwen-7b-chat'）
        
        Returns:
            是否成功
        """
        if model_key not in self.RECOMMENDED_MODELS:
            print(f"❌ 未知的模型: {model_key}")
            print(f"   可用模型: {', '.join(self.RECOMMENDED_MODELS.keys())}")
            return False
        
        model_info = self.RECOMMENDED_MODELS[model_key]
        return self.download_from_huggingface(model_info['name'])
    
    def check_model_exists(self, model_name: str) -> bool:
        """检查模型是否已下载"""
        safe_name = model_name.replace('/', '_')
        model_dir = os.path.join(self.models_dir, safe_name)
        return os.path.exists(model_dir) and os.path.isdir(model_dir)
    
    def get_model_info(self, model_key: str) -> Optional[Dict]:
        """获取模型信息"""
        return self.RECOMMENDED_MODELS.get(model_key)
    
    def recommend_model(self, use_case: str = '改写', memory_limit: Optional[int] = None) -> List[str]:
        """
        根据使用场景推荐模型
        
        Args:
            use_case: 使用场景（'改写', '生成', '对话'等）
            memory_limit: 内存限制（GB）
        
        Returns:
            推荐的模型列表
        """
        recommendations = []
        
        for key, info in self.RECOMMENDED_MODELS.items():
            # 检查是否适合使用场景
            if use_case in info.get('suitable_for', []):
                # 检查内存限制
                if memory_limit:
                    min_memory_str = info.get('min_memory', '16GB')
                    min_memory = int(min_memory_str.replace('GB', ''))
                    if memory_limit >= min_memory:
                        recommendations.append(key)
                else:
                    recommendations.append(key)
        
        return recommendations


def main():
    """命令行工具"""
    import argparse
    
    parser = argparse.ArgumentParser(description='模型下载工具')
    parser.add_argument('action', choices=['list', 'download', 'recommend', 'check'],
                       help='操作类型')
    parser.add_argument('--model', help='模型名称或键名')
    parser.add_argument('--use-case', default='改写', help='使用场景')
    parser.add_argument('--memory', type=int, help='内存限制（GB）')
    
    args = parser.parse_args()
    
    downloader = ModelDownloader()
    
    if args.action == 'list':
        print("\n📋 可用的中文语言模型:")
        print("=" * 60)
        for key, info in downloader.RECOMMENDED_MODELS.items():
            print(f"\n{key}:")
            print(f"  名称: {info['name']}")
            print(f"  大小: {info['size']}")
            print(f"  描述: {info['description']}")
            print(f"  适用: {', '.join(info['suitable_for'])}")
            print(f"  最低内存: {info['min_memory']}")
    
    elif args.action == 'recommend':
        recommendations = downloader.recommend_model(args.use_case, args.memory)
        if recommendations:
            print(f"\n💡 推荐模型（用于{args.use_case}）:")
            for key in recommendations:
                info = downloader.get_model_info(key)
                print(f"  - {key}: {info['description']} ({info['size']})")
        else:
            print(f"\n⚠️  未找到合适的模型")
    
    elif args.action == 'download':
        if not args.model:
            print("❌ 需要指定 --model")
            return
        
        # 检查是否是推荐的模型键名
        if args.model in downloader.RECOMMENDED_MODELS:
            downloader.download_recommended_model(args.model)
        else:
            # 直接使用模型名称
            downloader.download_from_huggingface(args.model)
    
    elif args.action == 'check':
        if not args.model:
            print("❌ 需要指定 --model")
            return
        
        if args.model in downloader.RECOMMENDED_MODELS:
            model_name = downloader.RECOMMENDED_MODELS[args.model]['name']
        else:
            model_name = args.model
        
        exists = downloader.check_model_exists(model_name)
        if exists:
            safe_name = model_name.replace('/', '_')
            model_dir = os.path.join(downloader.models_dir, safe_name)
            print(f"✅ 模型已下载: {model_dir}")
        else:
            print(f"❌ 模型未下载: {model_name}")


if __name__ == '__main__':
    main()

