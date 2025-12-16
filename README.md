# getBook - 多网站小说爬取与AI改写系统

一个完整的小说爬取、改写和AI训练系统，支持多网站、自动适配、风格改写和深度学习训练。

> **📐 架构优化完成**：项目已重构为模块化架构，统一接口位于 `scripts/core/`。详见 [ARCHITECTURE.md](docs/reports/project/ARCHITECTURE.md)

## ✨ 核心功能

### 🕷️ 多网站爬取
- ✅ **多网站支持**: 每个网站对应一个适配器，易于扩展
- ✅ **自动发现**: 未爬取过的网站自动解析结构
- ✅ **灵活选择**: 命令行可选择网站和类型
- ✅ **批量爬取**: 支持按类型、排名批量爬取
- ✅ **智能筛选**: 自动筛选已完结小说

### ✍️ 文本改写
- ✅ **18种风格**: 都市、玄幻、言情、武侠等
- ✅ **AI驱动**: 支持OpenAI、本地LLM、TensorFlow
- ✅ **视角转换**: 第一人称/第三人称转换
- ✅ **自然改写**: 上下文感知，避免机械替换

### 🤖 AI训练
- ✅ **TensorFlow模型**: 本地深度学习模型
- ✅ **增量训练**: 支持增量更新模型
- ✅ **数据整理**: 自动整理和生成训练数据
- ✅ **多风格支持**: 支持多种写作风格训练

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 多网站爬取（推荐）

```bash
# 1. 注册网站
python3 scripts/scraper/multi_site_scraper.py --register https://m.shuhaige.net

# 2. 查看已注册的网站
python3 scripts/scraper/multi_site_scraper.py --list-sites

# 3. 爬取小说
python3 scripts/scraper/multi_site_scraper.py \
  --site m.shuhaige.net \
  --category 都市 \
  --count 10 \
  --filter-completed

# 4. 生成训练数据
python3 scripts/scraper/generate_training_data.py --output data/training
```

### 单本爬取

```bash
# 使用便捷脚本
./scrape.sh https://m.shuhaige.net/350415/

# 或直接运行
python3 scripts/scraper/novel_scraper.py https://m.shuhaige.net/350415/
```

### 文本改写

```bash
# 传统方法
python3 scripts/creative/rewrite_novel.py novel.txt --style=都市幽默

# 使用AI（TensorFlow）
python3 scripts/creative/rewrite_novel.py novel.txt \
  --use-ai --ai-type=tensorflow --style=都市幽默
```

### 训练模型

```bash
# 基础训练
python3 scripts/ai/models/train_model.py \
  --data data/training/processed/training_data.txt \
  --model-path models/text_rewriter_model

# 增量训练
python3 scripts/ai/models/incremental_train.py \
  --data data/training/processed/training_data.txt \
  --model-path models/text_rewriter_model
```

## 📁 项目结构

```
getBook/
├── scripts/                    # 脚本目录
│   ├── scraper/               # 爬取模块
│   │   ├── adapters/         # 网站适配器
│   │   │   ├── base_adapter.py      # 适配器基类
│   │   │   └── shuhaige_adapter.py  # 书海阁适配器
│   │   ├── multi_site_scraper.py    # 多网站爬取器
│   │   ├── novel_scraper.py         # 单本爬取
│   │   ├── multi_site_scraper.py    # 多网站爬取器（推荐）
│   │   └── site_manager.py          # 网站管理器
│   ├── creative/              # 创意处理
│   │   ├── rewrite_novel.py  # 主改写脚本
│   │   └── docs/             # 文档
│   ├── ai/                    # AI模块
│   │   ├── analyzers/        # AI分析器
│   │   └── models/           # AI模型
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
├── requirements.txt           # Python依赖
├── scrape.sh                  # 单本爬取便捷脚本
└── README.md                  # 项目说明
```

## 📖 详细文档

- [项目总览](docs/reports/project/PROJECT_OVERVIEW.md) - 项目整体介绍
- [快速参考](QUICK_REFERENCE.md) - 常用命令速查
- [多网站爬取指南](scripts/scraper/MULTI_SITE_README.md) - 多网站系统详细说明
- [AI配置指南](scripts/creative/docs/AI_SETUP.md) - AI功能配置
- [TensorFlow设置](scripts/creative/docs/TENSORFLOW_SETUP.md) - 深度学习模型设置
- [完整文档索引](docs/INDEX.md) - 所有文档索引

## 🎯 完整工作流

### 从爬取到训练

```bash
# 1. 注册网站
python3 scripts/scraper/multi_site_scraper.py --register https://m.shuhaige.net

# 2. 批量爬取
python3 scripts/scraper/multi_site_scraper.py \
  --site m.shuhaige.net \
  --category 都市 \
  --count 10 \
  --filter-completed

# 3. 生成训练数据
python3 scripts/scraper/generate_training_data.py --output data/training

# 4. 训练模型
python3 scripts/ai/models/train_model.py \
  --data data/training/processed/training_data.txt \
  --model-path models/text_rewriter_model

# 5. 使用模型改写
python3 scripts/creative/rewrite_novel.py novel.txt \
  --use-ai --ai-type=tensorflow --style=都市幽默
```

## 🔧 添加新网站

### 方法1: 创建适配器（推荐）

1. 创建适配器文件：`scripts/scraper/adapters/new_site_adapter.py`
2. 继承 `BaseSiteAdapter` 并实现必要方法
3. 在 `adapters/__init__.py` 中注册
4. 注册网站：`--register https://new-site.com`

详见：[多网站爬取指南](scripts/scraper/MULTI_SITE_README.md)

### 方法2: 自动发现

系统会自动尝试解析未注册的网站结构，但可能需要手动创建适配器才能完整爬取。

## 📊 数据组织

爬取的数据按以下结构组织：

```
data/training/novels/
├── m.shuhaige.net/          # 网站名
│   ├── 都市/                # 类型
│   │   ├── 小说1/           # 小说名
│   │   │   ├── 小说1.txt
│   │   │   └── 小说1.json
│   │   └── 小说2/
│   │       └── ...
│   └── 玄幻/
│       └── ...
└── other-site.com/
    └── ...
```

## 🛠️ 主要脚本

### 爬取相关
- `scripts/scraper/multi_site_scraper.py` - 多网站爬取器（推荐）
- `scripts/scraper/novel_scraper.py` - 单本爬取
- `scripts/scraper/multi_site_scraper.py` - 多网站爬取器（推荐）
- `scripts/core/pipeline.py` - 统一数据处理流水线（推荐）

### 改写相关
- `scripts/creative/rewrite_novel.py` - 主改写脚本

### 训练相关
- `scripts/ai/models/train_model.py` - 基础训练
- `scripts/ai/models/incremental_train.py` - 增量训练
- `scripts/scraper/generate_training_data.py` - 训练数据生成

### 工具脚本
- `scrape.sh` - 单本爬取便捷脚本
- `organize_and_train.sh` - 整理训练便捷脚本

## ⚙️ 配置

### 环境变量（可选）

```bash
# OpenAI API（如果使用OpenAI）
export OPENAI_API_KEY="your-api-key"

# Ollama（如果使用本地LLM）
export OLLAMA_BASE_URL="http://localhost:11434"
```

## 📝 注意事项

1. **遵守网站规则**: 使用前请检查目标网站的robots.txt
2. **请求频率**: 默认延迟1.5秒，避免对服务器造成压力
3. **法律合规**: 请确保你有权爬取和使用相关内容
4. **数据备份**: 建议定期备份训练数据和模型

## 🤝 贡献

欢迎提交Issue和Pull Request！

详见：[CONTRIBUTING.md](CONTRIBUTING.md)

## 📄 许可证

（根据实际情况填写）

## 🔗 相关链接

- [项目总览](docs/reports/project/PROJECT_OVERVIEW.md)
- [快速参考](QUICK_REFERENCE.md)
- [完整文档索引](docs/INDEX.md)
