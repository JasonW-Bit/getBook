# 项目架构优化计划

## 优化目标

1. 删除临时脚本和冗余代码
2. 合并重复功能
3. 统一接口和架构
4. 规范化项目结构

## 需要删除的文件

### 临时脚本
- `batch_scrape.sh` - 旧版批量爬取脚本（已被multi_scrape.sh替代）
- `migrate.sh` - 迁移脚本（一次性使用，可删除）

### 冗余代码（标记为deprecated）
- `scripts/scraper/batch_scraper.py` - 旧版批量爬取器（保留兼容性，标记deprecated）
- `scripts/scraper/training_pipeline.py` - 旧版训练流水线（已被core/pipeline.py替代）
- `scripts/utils/generate_training_data.py` - 旧版训练数据生成（已被core/training_data_generator.py替代）

## 需要合并的功能

### 训练数据生成
- 统一到 `scripts/core/training_data_generator.py`
- 删除 `scripts/scraper/generate_training_data.py` 和 `scripts/utils/generate_training_data.py`

### 流水线
- 统一到 `scripts/core/pipeline.py`
- 标记旧版pipeline为deprecated

## 新的架构

```
scripts/
├── core/                    # 核心模块（新增）
│   ├── pipeline.py         # 统一流水线
│   └── training_data_generator.py  # 统一训练数据生成
├── scraper/                # 爬取模块
│   ├── adapters/          # 网站适配器
│   ├── multi_site_scraper.py  # 多网站爬取器（推荐）
│   ├── novel_scraper.py   # 单本爬取
│   └── batch_scraper.py   # 旧版（deprecated）
├── creative/              # 创意处理
├── ai/                    # AI模块
└── utils/                 # 工具脚本
```

## 统一接口

所有功能通过 `scripts/core/pipeline.py` 统一入口。

