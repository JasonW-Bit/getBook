# 多网站批量爬取系统

## 概述

这是一个支持多网站、自动适配的小说批量爬取系统。系统采用适配器模式，每个网站对应一个适配器，支持自动发现和解析新网站。

## 架构设计

```
scripts/scraper/
├── adapters/              # 网站适配器模块
│   ├── __init__.py       # 适配器注册
│   ├── base_adapter.py   # 适配器基类
│   └── shuhaige_adapter.py  # 书海阁适配器
├── site_manager.py       # 网站管理器
├── multi_site_scraper.py # 多网站爬取器
└── generate_training_data.py  # 训练数据生成
```

## 功能特性

1. **多网站支持**: 每个网站对应一个适配器，易于扩展
2. **自动发现**: 如果网站未爬取过，自动解析网站结构
3. **灵活选择**: 命令行可选择网站和类型
4. **数据组织**: 按网站和类型分类存放
5. **训练数据**: 自动生成深度学习训练数据

## 使用方法

### 1. 注册网站

```bash
# 注册新网站（会自动检测是否有适配器）
python3 scripts/scraper/multi_site_scraper.py --register https://m.shuhaige.net
```

### 2. 列出已注册的网站

```bash
python3 scripts/scraper/multi_site_scraper.py --list-sites
```

### 3. 批量爬取

```bash
# 爬取指定网站和类型的小说
python3 scripts/scraper/multi_site_scraper.py \
  --site m.shuhaige.net \
  --category 都市 \
  --count 10 \
  --filter-completed

# 爬取多个类型
python3 scripts/scraper/multi_site_scraper.py --site m.shuhaige.net --category 都市 --count 5
python3 scripts/scraper/multi_site_scraper.py --site m.shuhaige.net --category 玄幻 --count 5
```

### 4. 生成训练数据

```bash
# 从爬取的小说生成训练数据
python3 scripts/scraper/generate_training_data.py --output data/training
```

## 数据组织

爬取的数据按以下结构组织：

```
data/training/
├── novels/                    # 爬取的小说
│   ├── m.shuhaige.net/       # 网站名
│   │   ├── 都市/             # 类型
│   │   │   ├── 小说1.txt
│   │   │   ├── 小说1.json
│   │   │   └── ...
│   │   └── 玄幻/
│   │       └── ...
│   └── other-site.com/
│       └── ...
├── processed/                 # 处理后的数据
│   ├── training_data.txt     # 训练数据（TSV格式）
│   └── training_stats.json   # 统计信息
└── sites/                     # 网站配置
    └── sites.json            # 已注册的网站列表
```

## 添加新网站适配器

### 方法1: 创建适配器类

1. 在 `adapters/` 目录下创建新的适配器文件，例如 `new_site_adapter.py`:

```python
from .base_adapter import BaseSiteAdapter
from bs4 import BeautifulSoup
from typing import List, Dict

class NewSiteAdapter(BaseSiteAdapter):
    """新网站适配器"""
    
    def get_category_url(self, category: str) -> str:
        # 返回分类页面URL
        return f"{self.base_url}/category/{category}/"
    
    def parse_category_page(self, soup: BeautifulSoup, category: str) -> List[Dict]:
        # 解析分类页面，返回小说列表
        novels = []
        # ... 解析逻辑
        return novels
    
    def extract_novel_info(self, soup: BeautifulSoup) -> Dict:
        # 提取小说基本信息
        return {'title': ..., 'author': ..., ...}
    
    def extract_chapters(self, soup: BeautifulSoup) -> List[Dict]:
        # 提取章节列表
        return [{'title': ..., 'url': ...}, ...]
    
    def extract_chapter_content(self, soup: BeautifulSoup) -> str:
        # 提取章节内容
        return "..."
```

2. 在 `adapters/__init__.py` 中注册：

```python
from .new_site_adapter import NewSiteAdapter

ADAPTERS = {
    'shuhaige.net': ShuhaigeAdapter,
    'm.shuhaige.net': ShuhaigeAdapter,
    'new-site.com': NewSiteAdapter,  # 添加新适配器
}
```

### 方法2: 自动发现（需要手动创建适配器）

如果网站未注册，系统会尝试自动发现网站结构，但需要手动创建适配器才能完整爬取。

## 完整工作流

```bash
# 1. 注册网站
python3 scripts/scraper/multi_site_scraper.py --register https://m.shuhaige.net

# 2. 爬取小说
python3 scripts/scraper/multi_site_scraper.py \
  --site m.shuhaige.net \
  --category 都市 \
  --count 10 \
  --filter-completed

# 3. 生成训练数据
python3 scripts/scraper/generate_training_data.py --output data/training

# 4. 训练模型（使用现有的训练脚本）
python3 scripts/ai/models/train_model.py \
  --data data/training/processed/training_data.txt \
  --model-path models/text_rewriter_model
```

## 命令行参数

### multi_site_scraper.py

- `--register URL`: 注册新网站
- `--list-sites`: 列出所有已注册的网站
- `--site SITE_NAME`: 网站名称（必需）
- `--category CATEGORY`: 小说类型（必需）
- `--count N`: 爬取数量（默认：10）
- `--output DIR`: 输出目录（默认：data/training）
- `--no-filter-completed`: 不筛选，爬取所有小说
- `--generate-data`: 自动生成训练数据

### generate_training_data.py

- `--output DIR`: 输出目录（默认：data/training）
- `--use-ai`: 使用AI生成改写样本

## 注意事项

1. **首次使用**: 需要先注册网站才能爬取
2. **适配器**: 如果网站没有适配器，系统会尝试自动发现，但可能需要手动创建适配器
3. **数据组织**: 数据按网站和类型分类存放，便于管理和训练
4. **训练数据**: 生成的是TSV格式，可直接用于TensorFlow训练

## 扩展性

系统设计为高度可扩展：

- **新网站**: 只需创建适配器类并注册
- **新功能**: 可在基类中添加通用方法
- **新类型**: 自动支持所有网站已实现的类型

