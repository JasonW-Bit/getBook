# 项目总览

## 项目简介

getBook 是一个完整的小说爬取、改写和AI训练系统，支持多网站、自动适配、风格改写和深度学习训练。

## 核心功能

### 1. 多网站爬取系统 🕷️

- **网站适配器架构**: 每个网站对应一个适配器，易于扩展
- **自动发现**: 未爬取过的网站自动解析结构
- **灵活选择**: 命令行可选择网站和类型
- **批量爬取**: 支持按类型、排名批量爬取
- **智能筛选**: 自动筛选已完结小说
- **数据组织**: 按网站和类型分类存放

### 2. 文本改写系统 ✍️

- **18种风格**: 都市、玄幻、言情、武侠、科幻等
- **AI驱动**: 支持OpenAI、本地LLM（Ollama）、TensorFlow
- **视角转换**: 第一人称/第三人称转换
- **自然改写**: 上下文感知，避免机械替换
- **人物替换**: 自动识别和替换人物名称

### 3. AI训练系统 🤖

- **TensorFlow模型**: 本地深度学习模型
- **增量训练**: 支持增量更新模型
- **数据整理**: 自动整理和生成训练数据
- **多风格支持**: 支持多种写作风格训练
- **模型管理**: 支持保存、加载和合并模型

### 4. 数据分析系统 📊

- **小说特征分析**: 自动提取小说特征
- **写作风格识别**: 识别写作风格
- **质量评估**: 评估数据质量
- **统计报告**: 生成详细统计报告

## 项目结构

```
getBook/
├── scripts/                    # 脚本目录
│   ├── scraper/               # 爬取模块
│   │   ├── adapters/         # 网站适配器
│   │   │   ├── __init__.py
│   │   │   ├── base_adapter.py      # 适配器基类
│   │   │   └── shuhaige_adapter.py  # 书海阁适配器
│   │   ├── multi_site_scraper.py    # 多网站爬取器（推荐）
│   │   ├── novel_scraper.py         # 单本爬取
│   │   ├── batch_scraper.py         # 批量爬取（旧版）
│   │   ├── site_manager.py          # 网站管理器
│   │   ├── novel_analyzer.py        # 小说分析器
│   │   └── generate_training_data.py # 训练数据生成
│   ├── creative/              # 创意处理
│   │   ├── rewrite_novel.py  # 主改写脚本
│   │   ├── processors/       # 文本处理器
│   │   ├── transformers/     # 格式转换器
│   │   ├── generators/       # 内容生成器
│   │   └── docs/            # 文档
│   ├── ai/                    # AI模块
│   │   ├── analyzers/        # AI分析器
│   │   │   └── ai_analyzer.py
│   │   └── models/           # AI模型
│   │       ├── tensorflow_model.py
│   │       ├── train_model.py
│   │       └── incremental_train.py
│   └── utils/                 # 工具脚本
│       ├── data_organizer.py  # 数据整理
│       ├── migrate_novels.py  # 文件迁移
│       └── training_data_pipeline.py # 训练数据流水线
├── data/                      # 数据目录
│   ├── sites/                # 网站配置
│   │   └── sites.json        # 已注册的网站列表
│   └── training/              # 训练数据
│       ├── novels/           # 爬取的小说
│       │   └── <网站名>/     # 按网站分类
│       │       └── <类型>/   # 按类型分类
│       └── processed/        # 处理后的数据
│           ├── training_data.txt    # 训练数据（TSV格式）
│           └── training_stats.json # 统计信息
├── models/                    # 模型文件
│   └── text_rewriter/        # TensorFlow模型
├── novels/                    # 单本爬取的小说
├── docs/                      # 项目文档
├── requirements.txt           # Python依赖
├── scrape.sh                  # 单本爬取便捷脚本
├── batch_scrape.sh            # 批量爬取便捷脚本
├── organize_and_train.sh      # 整理训练便捷脚本
├── README.md                  # 项目主文档
└── PROJECT_OVERVIEW.md        # 项目总览（本文件）
```

## 快速开始

### 1. 多网站爬取（推荐）

```bash
# 注册网站
python3 scripts/scraper/multi_site_scraper.py --register https://m.shuhaige.net

# 查看已注册的网站
python3 scripts/scraper/multi_site_scraper.py --list-sites

# 爬取小说
python3 scripts/scraper/multi_site_scraper.py \
  --site m.shuhaige.net \
  --category 都市 \
  --count 10 \
  --filter-completed
```

### 2. 单本爬取

```bash
# 使用便捷脚本
./scrape.sh https://m.shuhaige.net/350415/

# 或直接运行
python3 scripts/scraper/novel_scraper.py https://m.shuhaige.net/350415/
```

### 3. 文本改写

```bash
# 传统方法
python3 scripts/creative/rewrite_novel.py novel.txt --style=都市幽默

# 使用AI（TensorFlow）
python3 scripts/creative/rewrite_novel.py novel.txt \
  --use-ai --ai-type=tensorflow --style=都市幽默
```

### 4. 训练模型

```bash
# 生成训练数据
python3 scripts/scraper/generate_training_data.py --output data/training

# 基础训练
python3 scripts/ai/models/train_model.py \
  --data data/training/processed/training_data.txt \
  --model-path models/text_rewriter_model

# 增量训练
python3 scripts/ai/models/incremental_train.py \
  --data data/training/processed/training_data.txt \
  --model-path models/text_rewriter_model
```

## 数据流程

### 爬取流程
```
网站 → 注册/发现 → 适配器 → 爬取 → 整理 → 保存到 data/training/novels/<网站>/<类型>/
```

### 改写流程
```
原始小说 → 分析 → 改写（规则/AI） → 保存到 novels/<小说名>/rewritten/
```

### 训练流程
```
爬取数据 → 整理 → 生成训练数据（TSV） → 训练模型 → 保存到 models/
```

## 主要脚本

### 爬取相关
- `scripts/scraper/multi_site_scraper.py` - 多网站爬取器（推荐）
- `scripts/scraper/novel_scraper.py` - 单本爬取
- `scripts/scraper/batch_scraper.py` - 批量爬取（旧版，保留兼容性）

### 改写相关
- `scripts/creative/rewrite_novel.py` - 主改写脚本

### 训练相关
- `scripts/ai/models/train_model.py` - 基础训练
- `scripts/ai/models/incremental_train.py` - 增量训练
- `scripts/scraper/generate_training_data.py` - 训练数据生成

### 工具相关
- `scripts/utils/data_organizer.py` - 数据整理
- `scripts/utils/migrate_novels.py` - 文件迁移
- `scripts/utils/training_data_pipeline.py` - 训练数据流水线

## 文档索引

### 使用文档
- [README.md](README.md) - 项目主文档
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - 快速参考
- [scripts/scraper/MULTI_SITE_README.md](scripts/scraper/MULTI_SITE_README.md) - 多网站系统详细说明
- [scripts/scraper/QUICK_START_MULTI_SITE.md](scripts/scraper/QUICK_START_MULTI_SITE.md) - 多网站快速开始

### 配置文档
- [scripts/creative/docs/AI_SETUP.md](scripts/creative/docs/AI_SETUP.md) - AI配置
- [scripts/creative/docs/TENSORFLOW_SETUP.md](scripts/creative/docs/TENSORFLOW_SETUP.md) - TensorFlow配置
- [scripts/creative/docs/DEEP_LEARNING_GUIDE.md](scripts/creative/docs/DEEP_LEARNING_GUIDE.md) - 深度学习指南

### 技术文档
- [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) - 项目结构
- [docs/INDEX.md](docs/INDEX.md) - 完整文档索引

## 依赖安装

```bash
pip install -r requirements.txt
```

主要依赖：
- `requests` - HTTP请求
- `beautifulsoup4` - HTML解析
- `tensorflow` - 深度学习
- `numpy` - 数值计算
- `openai` - OpenAI API（可选）

## 支持的网站

- ✅ m.shuhaige.net (书海阁) - 已实现适配器

## 添加新网站

详见：[多网站爬取指南](scripts/scraper/MULTI_SITE_README.md)

## 许可证

（根据实际情况填写）

## 贡献

欢迎提交Issue和Pull Request！

详见：[CONTRIBUTING.md](CONTRIBUTING.md)
