#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI模块
提供AI分析、模型训练和文本改写功能
"""

try:
    from .analyzers.ai_analyzer import (
        AIAnalyzerBase,
        OpenAIAnalyzer,
        LocalLLMAnalyzer,
        TensorFlowAnalyzer,
        AIAnalyzerFactory
    )
except ImportError:
    # 如果导入失败，设置为None
    AIAnalyzerBase = None
    OpenAIAnalyzer = None
    LocalLLMAnalyzer = None
    TensorFlowAnalyzer = None
    AIAnalyzerFactory = None

try:
    from .models.tensorflow_model import (
        TensorFlowTextRewriter,
        TensorFlowAnalyzer as TensorFlowModelAnalyzer
    )
except ImportError:
    TensorFlowTextRewriter = None
    TensorFlowModelAnalyzer = None

__all__ = [
    'AIAnalyzerBase',
    'OpenAIAnalyzer',
    'LocalLLMAnalyzer',
    'TensorFlowAnalyzer',
    'AIAnalyzerFactory',
    'TensorFlowTextRewriter',
    'TensorFlowModelAnalyzer',
]
