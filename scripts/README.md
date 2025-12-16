# 脚本目录说明

## 快速导航

- [爬取脚本](#爬取脚本-scraper)
- [工具脚本](#工具脚本-utils)
- [AI脚本](#ai脚本-ai)
- [创意处理](#创意处理脚本-creative)

## 目录结构

```
scripts/
├── scraper/              # 爬取相关脚本
│   └── novel_scraper.py  # 小说爬取脚本
│
├── utils/                # 工具脚本
│   └── migrate_novels.py # 文件迁移工具
│
├── ai/                   # AI相关脚本
│   ├── analyzers/        # AI分析器
│   │   └── ai_analyzer.py # AI分析器（OpenAI、本地LLM等）
│   └── models/           # AI模型
│       ├── tensorflow_model.py # TensorFlow模型实现
│       └── train_model.py      # 模型训练脚本
│
├── creative/             # 创意处理脚本
│   ├── rewrite_novel.py # 主改写脚本
│   ├── processors/      # 文本处理器
│   │   ├── text_processor.py    # 智能文本处理器
│   │   └── creative_process.py  # 创意处理
│   ├── transformers/    # 格式转换器
│   │   └── transform_format.py # 格式转换
│   ├── generators/      # 内容生成器
│   │   └── generate_content.py # 内容生成
│   └── docs/            # 文档
│       ├── README.md
│       ├── AI_SETUP.md
│       ├── TENSORFLOW_SETUP.md
│       └── ...
│
└── README.md            # 本文件
```

## 脚本分类

### 1. 爬取脚本 (`scraper/`)
- **novel_scraper.py**: 小说爬取脚本
- **用途**: 从网站爬取小说内容

### 2. 工具脚本 (`utils/`)
- **migrate_novels.py**: 文件迁移工具
- **用途**: 整理和迁移小说文件

### 3. AI脚本 (`ai/`)

#### 分析器 (`ai/analyzers/`)
- **ai_analyzer.py**: AI分析器
  - 支持OpenAI API
  - 支持本地LLM（Ollama）
  - 支持TensorFlow模型

#### 模型 (`ai/models/`)
- **tensorflow_model.py**: TensorFlow模型实现
- **train_model.py**: 模型训练脚本

### 4. 创意处理脚本 (`creative/`)

#### 主脚本
- **rewrite_novel.py**: 主改写脚本
  - 集成所有功能
  - 支持多种风格
  - 支持AI改写

#### 处理器 (`processors/`)
- **text_processor.py**: 智能文本处理器
- **creative_process.py**: 创意处理

#### 转换器 (`transformers/`)
- **transform_format.py**: 格式转换

#### 生成器 (`generators/`)
- **generate_content.py**: 内容生成

#### 文档 (`docs/`)
- 各种使用说明和配置指南

## 使用说明

### 爬取小说
```bash
python3 scripts/scraper/novel_scraper.py <URL>
```

### 迁移文件
```bash
python3 scripts/utils/migrate_novels.py
```

### 改写小说
```bash
python3 scripts/creative/rewrite_novel.py <文件> [选项]
```

### 训练模型
```bash
python3 scripts/ai/models/train_model.py <数据文件>
```

## 导入说明

脚本之间的导入路径已自动处理，可以直接使用相对导入。

