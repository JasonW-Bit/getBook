#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网站适配器模块
每个网站对应一个适配器类
"""

from .base_adapter import BaseSiteAdapter
from .shuhaige_adapter import ShuhaigeAdapter
from .ixdzs8_adapter import Ixdzs8Adapter

# 注册所有适配器
ADAPTERS = {
    'shuhaige.net': ShuhaigeAdapter,
    'm.shuhaige.net': ShuhaigeAdapter,
    'ixdzs8.com': Ixdzs8Adapter,
    'www.ixdzs8.com': Ixdzs8Adapter,
}

def get_adapter(site_name: str) -> BaseSiteAdapter:
    """获取网站适配器"""
    adapter_class = ADAPTERS.get(site_name)
    if adapter_class:
        return adapter_class
    return None

def list_adapters():
    """列出所有可用的适配器"""
    return list(ADAPTERS.keys())
