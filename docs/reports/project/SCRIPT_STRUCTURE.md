# 脚本目录结构

## 完整结构

```
scripts/
├── scraper/                    # 爬取脚本
│   ├── __init__.py
│   └── novel_scraper.py       # 小说爬取脚本
│
├── utils/                      # 工具脚本
│   ├── __init__.py
│   └── migrate_novels.py      # 文件迁移工具
│
├── ai/                         # AI相关脚本
│   ├── __init__.py
│   ├── analyzers/             # AI分析器
│   │   ├── __init__.py
│   │   └── ai_analyzer.py     # AI分析器（OpenAI、本地LLM、TensorFlow）
│   └── models/                # AI模型
│       ├── __init__.py
│       ├── tensorflow_model.py # TensorFlow模型实现
│       └── train_model.py      # 模型训练脚本
│
├── creative/                   # 创意处理脚本
│   ├── __init__.py
│   ├── rewrite_novel.py       # 主改写脚本（入口）
│   ├── processors/            # 文本处理器
│   │   ├── __init__.py
│   │   ├── text_processor.py  # 智能文本处理器
│   │   └── creative_process.py # 创意处理
│   ├── transformers/          # 格式转换器
│   │   ├── __init__.py
│   │   └── transform_format.py # 格式转换
│   ├── generators/            # 内容生成器
│   │   ├── __init__.py
│   │   └── generate_content.py # 内容生成
│   └── docs/                  # 文档
│       ├── README.md
│       ├── AI_SETUP.md
│       ├── TENSORFLOW_SETUP.md
│       ├── DEEP_LEARNING_GUIDE.md
│       ├── STYLES.md
│       ├── USAGE.md
│       ├── CHANGELOG.md
│       └── README_STRUCTURE.md
│
└── README.md                   # 脚本说明
```

## 分类说明

### 1. 爬取脚本 (`scraper/`)
**功能**: 从网站爬取小说内容

- `novel_scraper.py`: 主爬取脚本

### 2. 工具脚本 (`utils/`)
**功能**: 辅助工具和工具函数

- `migrate_novels.py`: 文件迁移和整理工具

### 3. AI脚本 (`ai/`)
**功能**: AI相关的所有功能

#### 分析器 (`ai/analyzers/`)
- `ai_analyzer.py`: 
  - OpenAI API分析器
  - 本地LLM分析器（Ollama）
  - TensorFlow分析器

#### 模型 (`ai/models/`)
- `tensorflow_model.py`: TensorFlow模型实现
- `train_model.py`: 模型训练脚本

### 4. 创意处理脚本 (`creative/`)
**功能**: 小说改写和创意处理

#### 主脚本
- `rewrite_novel.py`: 主入口脚本，集成所有功能

#### 处理器 (`processors/`)
- `text_processor.py`: 智能文本处理器（自然改写）
- `creative_process.py`: 创意处理（添加元素、重组等）

#### 转换器 (`transformers/`)
- `transform_format.py`: 格式转换（TXT/JSON、编码等）

#### 生成器 (`generators/`)
- `generate_content.py`: 内容生成（新章节、扩展等）

#### 文档 (`docs/`)
- 所有使用说明和配置文档

## 使用路径

### 爬取小说
```bash
python3 scripts/scraper/novel_scraper.py <URL>
# 或使用便捷脚本
./scrape.sh <URL>
```

### 迁移文件
```bash
python3 scripts/utils/migrate_novels.py
# 或使用便捷脚本
./migrate.sh
```

### 改写小说
```bash
python3 scripts/creative/rewrite_novel.py <文件> [选项]
```

### 训练模型
```bash
python3 scripts/ai/models/train_model.py <数据文件>
```

## 导入关系

```
rewrite_novel.py
  ├─> ai/analyzers/ai_analyzer.py
  │     └─> ai/models/tensorflow_model.py
  └─> creative/processors/text_processor.py
```

所有导入路径已自动处理，脚本可以正常工作。

