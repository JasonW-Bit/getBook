# 创意处理模块说明

## 目录结构

```
scripts/creative/
├── __init__.py              # 模块初始化
├── rewrite_novel.py         # 主改写脚本（入口）
├── processors/              # 文本处理器
│   ├── __init__.py
│   ├── text_processor.py    # 智能文本处理器
│   └── creative_process.py  # 创意处理
├── generators/              # 内容生成器
│   ├── __init__.py
│   └── generate_content.py # 内容生成
├── transformers/            # 格式转换器
│   ├── __init__.py
│   └── transform_format.py # 格式转换
└── docs/                    # 文档
```

## 核心功能

### 1. 文本改写 (`rewrite_novel.py`)
- **18种风格**: 现代、古典、简洁、华丽、悬疑、浪漫、幽默、严肃、科幻、武侠、青春、都市、古风、诗化、口语、正式、网络、文艺
- **视角转换**: 第一人称 ↔ 第三人称
- **姓名替换**: 自动替换人物姓名
- **AI集成**: 支持OpenAI、本地LLM、TensorFlow

### 2. 文本处理器 (`processors/`)
- **NaturalStyleRewriter**: 自然风格改写器
- **ContextualTextProcessor**: 基于上下文的处理器
- **智能改写**: 上下文感知，避免机械替换

### 3. 内容生成器 (`generators/`)
- **ContentGenerator**: 内容生成器
- **新章节生成**: 基于现有内容生成新章节
- **内容扩展**: 扩展现有章节内容
- **创意生成**: 生成全新内容

### 4. 格式转换器 (`transformers/`)
- **FormatTransformer**: 格式转换器
- **编码转换**: 支持多种编码格式
- **格式转换**: TXT/JSON等格式互转

## 使用方式

### 命令行使用

```bash
# 基础改写
python3 scripts/creative/rewrite_novel.py novel.txt --style=都市幽默

# 使用AI改写
python3 scripts/creative/rewrite_novel.py novel.txt \
  --use-ai --ai-type=tensorflow --style=都市幽默

# 视角转换
python3 scripts/creative/rewrite_novel.py novel.txt \
  --perspective=第三人称

# 姓名替换
python3 scripts/creative/rewrite_novel.py novel.txt \
  --replace-names
```

### Python代码使用

```python
from scripts.creative.rewrite_novel import NovelRewriter

# 创建改写器
rewriter = NovelRewriter("novel.txt", "output.txt")

# 分析小说
rewriter.analyze_novel(use_ai=True, ai_type="tensorflow")

# 改写
rewriter.rewrite(
    perspective="第三人称",
    style="都市幽默",
    replace_names=True,
    use_ai=True,
    ai_type="tensorflow"
)
```

### 使用统一接口

```python
from scripts.ai.integration import UnifiedRewriter

# 创建统一改写器
rewriter = UnifiedRewriter(
    ai_type="tensorflow",
    use_hybrid=True
)

# 改写文本
result = rewriter.rewrite(
    text="原始文本",
    style="都市幽默",
    use_ai=True
)
```

## 与AI模块集成

创意处理模块已与AI模块完全集成：

1. **自动使用AI**: 通过`--use-ai`参数启用
2. **混合模式**: AI改写 + 传统方法微调
3. **统一接口**: 使用`integration.py`的统一接口
4. **自动降级**: AI失败时自动使用传统方法

## 风格说明

详见 `docs/STYLES.md`

## 文档

- `docs/USAGE.md` - 使用说明
- `docs/STYLES.md` - 风格说明
- `docs/AI_SETUP.md` - AI配置
- `docs/TENSORFLOW_SETUP.md` - TensorFlow配置
- `docs/DEEP_LEARNING_GUIDE.md` - 深度学习指南

