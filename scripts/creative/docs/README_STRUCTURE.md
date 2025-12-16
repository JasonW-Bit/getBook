# 项目目录结构说明

## 整体结构

```
getBook/
├── scripts/                    # 脚本目录
│   ├── novel_scraper.py      # 小说爬取脚本
│   └── creative/              # 创意处理脚本目录
│       ├── rewrite_novel.py          # 主改写脚本
│       ├── ai_analyzer.py            # AI分析器
│       ├── tensorflow_model.py       # TensorFlow模型
│       ├── train_model.py           # 模型训练脚本
│       ├── text_processor.py        # 智能文本处理器
│       ├── creative_process.py      # 创意处理
│       ├── transform_format.py      # 格式转换
│       ├── generate_content.py      # 内容生成
│       └── README.md                # 脚本说明
├── models/                    # 模型文件目录
│   └── text_rewriter_model/   # TensorFlow模型文件
│       ├── best_model.h5      # 最佳模型权重
│       ├── final_model.h5     # 最终模型权重
│       └── vocab.json         # 词汇表
├── data/                      # 数据目录
│   └── training/              # 训练数据
│       ├── training_data.txt  # 训练数据文件
│       └── README.md          # 数据格式说明
├── novels/                    # 小说文件目录
│   └── [小说标题]/           # 每部小说的文件夹
│       ├── [小说标题].txt    # 原始文件
│       └── rewritten/        # 改写文件目录
│           └── [小说标题]_rewritten.txt
├── docs/                      # 文档目录
│   └── PROJECT_STRUCTURE.md  # 项目结构文档
├── requirements.txt           # Python依赖
└── README.md                 # 项目说明
```

## 核心脚本说明

### 1. 改写脚本 (`rewrite_novel.py`)
- **功能**: 小说改写主脚本
- **支持**: 多种风格、AI改写、TensorFlow本地模型
- **使用**: `python3 scripts/creative/rewrite_novel.py <文件> [选项]`

### 2. AI分析器 (`ai_analyzer.py`)
- **功能**: 集成多种AI服务
- **支持**: OpenAI、本地LLM、TensorFlow
- **用途**: 文本分析和改写

### 3. TensorFlow模型 (`tensorflow_model.py`)
- **功能**: 本地深度学习模型
- **特点**: 完全本地化、可训练、可定制
- **架构**: Transformer风格

### 4. 模型训练 (`train_model.py`)
- **功能**: 训练TensorFlow模型
- **使用**: `python3 scripts/creative/train_model.py <数据文件>`

## 数据目录

### `data/training/`
- **用途**: 存放训练数据
- **格式**: TSV（制表符分隔）
- **内容**: 原始文本、改写文本、风格ID

### `models/`
- **用途**: 存放训练好的模型
- **内容**: 模型权重、词汇表、配置文件

## 输出目录

### `novels/`
- **结构**: 每部小说一个文件夹
- **内容**: 
  - 原始文件
  - `rewritten/` 子目录（改写后的文件）

## 文档目录

### `docs/`
- 项目结构文档
- 使用指南
- API文档

## 配置文件

### `requirements.txt`
- Python依赖包列表
- 包含: requests, beautifulsoup4, tensorflow等

## 使用流程

1. **爬取小说**: `python3 scripts/novel_scraper.py <URL>`
2. **准备训练数据**: 编辑 `data/training/training_data.txt`
3. **训练模型**: `python3 scripts/creative/train_model.py data/training/training_data.txt`
4. **改写小说**: `python3 scripts/creative/rewrite_novel.py novel.txt --use-ai --ai-type=tensorflow`

