#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创意处理模块
提供文本改写、内容生成和格式转换功能
"""

try:
    from .processors.text_processor import (
        NaturalStyleRewriter,
        ContextualTextProcessor
    )
except ImportError:
    NaturalStyleRewriter = None
    ContextualTextProcessor = None

try:
    from .generators.generate_content import ContentGenerator
except ImportError:
    ContentGenerator = None

try:
    from .transformers.transform_format import FormatTransformer
except ImportError:
    FormatTransformer = None

__all__ = [
    'NaturalStyleRewriter',
    'ContextualTextProcessor',
    'ContentGenerator',
    'FormatTransformer',
]
