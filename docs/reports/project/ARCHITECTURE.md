# 项目架构说明

## 目录结构

```
getBook/
├── scripts/
│   ├── core/                    # 核心模块（统一接口）
│   │   ├── pipeline.py         # 统一数据处理流水线
│   │   └── training_data_generator.py  # 统一训练数据生成
│   ├── scraper/                # 爬取模块
│   │   ├── adapters/          # 网站适配器
│   │   │   ├── base_adapter.py
│   │   │   └── shuhaige_adapter.py
│   │   ├── multi_site_scraper.py  # 多网站爬取器（推荐）
│   │   ├── novel_scraper.py   # 单本爬取
│   │   ├── novel_analyzer.py   # 小说分析
│   │   ├── site_manager.py    # 网站管理
│   │   └── batch_scraper.py   # 旧版（deprecated）
│   ├── creative/              # 创意处理模块
│   │   ├── rewrite_novel.py   # 小说改写
│   │   ├── processors/        # 文本处理
│   │   ├── generators/        # 内容生成
│   │   └── transformers/      # 格式转换
│   ├── ai/                    # AI模块
│   │   ├── analyzers/         # AI分析器
│   │   └── models/            # 模型训练
│   └── utils/                 # 工具脚本
│       ├── data_organizer.py  # 数据整理
│       ├── cleanup_empty_folders.py  # 清理工具
│       └── migrate_to_new_structure.py  # 迁移工具
├── data/
│   ├── sites/                 # 网站配置
│   └── training/              # 训练数据
│       ├── novels/            # 爬取的小说（网站/类型/小说名/）
│       └── processed/         # 处理后的数据
├── models/                    # 训练好的模型
├── docs/                      # 文档
└── run_pipeline.sh           # 统一入口脚本
```

## 核心模块

### 1. core/pipeline.py
统一的数据处理流水线，整合所有功能：
- 爬取小说
- 分析特征
- 生成训练数据
- 训练模型

### 2. core/training_data_generator.py
统一的训练数据生成器，支持：
- 多网站数据
- 多类型数据
- 自动提取章节
- 生成TSV格式训练数据

## 使用方式

### 统一流水线（推荐）
```bash
# 完整流程
./run_pipeline.sh --site m.shuhaige.net --category 都市 --count 10

# 只训练（已有数据）
./run_pipeline.sh --site m.shuhaige.net --category 都市 --count 10 \
  --skip scrape,analyze,generate

# 增量训练
./run_pipeline.sh --site m.shuhaige.net --category 都市 --count 5 \
  --incremental --skip scrape,analyze,generate
```

### 单独使用各模块
```bash
# 多网站爬取
./multi_scrape.sh

# 数据整理和训练
./organize_and_train.sh
```

## 已弃用的模块

以下模块已标记为deprecated，保留仅用于兼容性：

- `scripts/scraper/batch_scraper.py` - 使用 `multi_site_scraper.py` 替代
- `scripts/scraper/training_pipeline.py` - 使用 `core/pipeline.py` 替代

## 数据流

```
爬取 → 存储（网站/类型/小说名/） → 分析 → 生成训练数据 → 训练模型
```

## 扩展性

### 添加新网站
1. 在 `scripts/scraper/adapters/` 创建新的适配器
2. 继承 `BaseSiteAdapter`
3. 实现必要的方法
4. 在 `adapters/__init__.py` 注册

### 添加新功能
1. 在对应模块下创建新文件
2. 如需集成到流水线，在 `core/pipeline.py` 中添加

