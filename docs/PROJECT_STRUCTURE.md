# 项目结构详解

## 目录结构

```
getBook/
├── scripts/                    # 所有脚本代码
│   ├── scraper/               # 爬取模块
│   │   ├── adapters/         # 网站适配器（多网站支持）
│   │   ├── multi_site_scraper.py    # 多网站爬取器（推荐使用）
│   │   ├── novel_scraper.py         # 单本爬取
│   │   ├── multi_site_scraper.py     # 多网站爬取器（推荐）
│   │   ├── site_manager.py          # 网站管理器
│   │   └── generate_training_data.py # 训练数据生成
│   ├── creative/              # 创意处理模块
│   │   ├── rewrite_novel.py  # 主改写脚本
│   │   ├── processors/       # 文本处理器
│   │   ├── transformers/     # 格式转换器
│   │   ├── generators/       # 内容生成器
│   │   └── docs/            # 文档
│   ├── ai/                    # AI模块
│   │   ├── analyzers/        # AI分析器
│   │   └── models/           # AI模型（TensorFlow）
│   └── utils/                 # 工具脚本
│       ├── data_organizer.py  # 数据整理
│       └── training_data_pipeline.py # 训练数据流水线
├── data/                      # 数据目录
│   ├── sites/                # 网站配置
│   └── training/              # 训练数据
│       ├── novels/           # 爬取的小说（按网站/类型分类）
│       └── processed/        # 处理后的数据
├── models/                    # 模型文件
│   └── text_rewriter/        # TensorFlow模型
├── novels/                    # 单本爬取的小说
├── docs/                      # 项目文档
└── requirements.txt           # Python依赖
```

## 核心模块说明

### 1. 爬取模块 (scripts/scraper/)

#### adapters/ - 网站适配器
- **base_adapter.py**: 适配器基类，定义接口
- **shuhaige_adapter.py**: 书海阁网站适配器实现
- **__init__.py**: 适配器注册和管理

#### 主要脚本
- **multi_site_scraper.py**: 多网站爬取器（推荐）
  - 支持多网站
  - 自动适配
  - 灵活配置
  
- **novel_scraper.py**: 单本爬取
  - 支持断点续传
  - 自动处理分页
  - 错误重试

- **multi_site_scraper.py**: 多网站爬取器（推荐）
  - 保留兼容性
  - 建议使用 multi_site_scraper.py

- **site_manager.py**: 网站管理器
  - 网站注册
  - 自动发现
  - 配置管理

### 2. 创意处理模块 (scripts/creative/)

- **rewrite_novel.py**: 主改写脚本
  - 18种风格支持
  - AI驱动改写
  - 视角转换

- **processors/**: 文本处理器
- **transformers/**: 格式转换器
- **generators/**: 内容生成器

### 3. AI模块 (scripts/ai/)

- **analyzers/ai_analyzer.py**: AI分析器
  - OpenAI支持
  - 本地LLM支持
  - TensorFlow支持

- **models/**: AI模型
  - **tensorflow_model.py**: TensorFlow模型实现
  - **train_model.py**: 基础训练
  - **incremental_train.py**: 增量训练

### 4. 工具模块 (scripts/utils/)

- **data_organizer.py**: 数据整理
- **training_data_pipeline.py**: 训练数据流水线
- **migrate_novels.py**: 文件迁移

## 数据组织

### 爬取数据
```
data/training/novels/
├── <网站名>/          # 按网站分类
│   ├── <类型>/        # 按类型分类
│   │   ├── <小说名>/  # 按小说名分类
│   │   │   ├── <小说名>.txt
│   │   │   └── <小说名>.json
│   │   └── ...
│   └── ...
└── ...
```

**示例**:
```
data/training/novels/
└── m.shuhaige.net/
    ├── 都市/
    │   ├── 重生香江之金融帝国/
    │   │   ├── 重生香江之金融帝国.txt
    │   │   └── 重生香江之金融帝国.json
    │   └── 魔道祖师/
    │       ├── 魔道祖师.txt
    │       └── 魔道祖师.json
    └── 玄幻/
        └── ...
```

### 训练数据
```
data/training/processed/
├── training_data.txt      # TSV格式训练数据
└── training_stats.json    # 统计信息
```

### 模型文件
```
models/text_rewriter/
├── model_weights.h5       # 模型权重
├── vocabulary.json        # 词汇表
└── config.json           # 模型配置
```

## 配置文件

### 网站配置
```
data/sites/sites.json      # 已注册的网站列表
```

### 项目配置
```
requirements.txt           # Python依赖
```

## 文档组织

```
docs/                      # 项目文档
├── INDEX.md              # 文档索引
├── PROJECT_STRUCTURE.md  # 项目结构（本文件）
├── QUICK_START.md        # 快速开始
└── ...

scripts/scraper/          # 爬取模块文档
├── MULTI_SITE_README.md  # 多网站系统说明
└── QUICK_START_MULTI_SITE.md  # 快速开始

scripts/creative/docs/    # 创意处理文档
├── AI_SETUP.md          # AI配置
└── ...
```

## 扩展指南

### 添加新网站适配器

1. 在 `scripts/scraper/adapters/` 创建新文件
2. 继承 `BaseSiteAdapter`
3. 实现必要方法
4. 在 `__init__.py` 中注册

详见：[多网站爬取指南](../scripts/scraper/MULTI_SITE_README.md)

### 添加新风格

1. 在 `scripts/creative/rewrite_novel.py` 中添加风格定义
2. 实现风格转换逻辑
3. 更新文档

## 最佳实践

1. **使用多网站爬取器**: 推荐使用 `multi_site_scraper.py`
2. **数据分类存放**: 按网站和类型分类
3. **定期备份**: 备份训练数据和模型
4. **遵守规则**: 遵守网站robots.txt
