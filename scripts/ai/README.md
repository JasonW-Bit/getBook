# AI模块说明

## 目录结构

```
scripts/ai/
├── __init__.py              # 模块初始化，导出主要接口
├── integration.py           # AI与创意处理模块集成（统一接口）
├── analyzers/               # AI分析器
│   ├── __init__.py
│   └── ai_analyzer.py       # AI分析器实现（OpenAI/本地LLM/TensorFlow）
└── models/                  # AI模型
    ├── __init__.py
    ├── tensorflow_model.py  # TensorFlow模型实现
    ├── train_model.py       # 模型训练脚本
    ├── incremental_train.py # 增量训练脚本
    └── model_evaluator.py   # 模型评估工具
```

## 核心功能

### 1. AI分析器 (`analyzers/`)
- **OpenAIAnalyzer**: OpenAI API分析器
- **LocalLLMAnalyzer**: 本地LLM分析器（Ollama等）
- **TensorFlowAnalyzer**: TensorFlow本地模型分析器
- **AIAnalyzerFactory**: 工厂类，统一创建分析器

### 2. AI模型 (`models/`)
- **TensorFlowTextRewriter**: TensorFlow文本改写模型
- **训练脚本**: 支持基础训练和增量训练
- **评估工具**: 模型性能评估

### 3. 集成模块 (`integration.py`)
- **UnifiedRewriter**: 统一改写器，整合AI和传统方法
- **CreativeAIEngine**: 创意AI引擎，完整处理流程
- **create_engine**: 工厂函数，创建引擎实例

## 使用方式

### 方式1: 使用统一接口（推荐）

```python
from scripts.ai.integration import UnifiedRewriter, create_engine

# 创建统一改写器
rewriter = UnifiedRewriter(
    ai_type="tensorflow",
    ai_model_path="models/text_rewriter_model",
    use_hybrid=True  # 混合模式：AI + 传统方法
)

# 改写文本
result = rewriter.rewrite(
    text="原始文本",
    style="都市幽默",
    context="上下文信息",
    use_ai=True
)

# 或使用引擎（完整流程）
engine = create_engine(ai_type="tensorflow")
results = engine.process_novel(
    content="小说内容",
    style="都市幽默",
    operations=['analyze', 'rewrite', 'generate']
)
```

### 方式2: 直接使用AI分析器

```python
from scripts.ai.analyzers.ai_analyzer import AIAnalyzerFactory

# 创建分析器
analyzer = AIAnalyzerFactory.create_analyzer(
    analyzer_type="tensorflow",
    model_path="models/text_rewriter_model"
)

# 使用分析器
rewritten = analyzer.rewrite_text("原始文本", style="都市幽默")
```

### 方式3: 使用TensorFlow模型

```python
from scripts.ai.models.tensorflow_model import TensorFlowTextRewriter

# 创建模型
rewriter = TensorFlowTextRewriter(model_path="models/text_rewriter_model")
rewriter.load_model()

# 改写文本
result = rewriter.rewrite("原始文本", style=11, temperature=0.7)
```

## 集成说明

AI模块已与创意处理模块（`scripts/creative/`）完全集成：

1. **统一接口**: `integration.py` 提供统一接口
2. **混合模式**: AI改写 + 传统方法微调
3. **自动降级**: AI失败时自动使用传统方法
4. **上下文感知**: 支持上下文信息传递

## 训练模型

```bash
# 基础训练
python3 scripts/ai/models/train_model.py data/training/processed/training_data.txt

# 增量训练
python3 scripts/ai/models/incremental_train.py data/training/processed/new_data.txt

# 评估模型
python3 scripts/ai/models/model_evaluator.py data/training/processed/validation_data.txt
```

## 配置说明

### TensorFlow模型路径
默认路径：`models/text_rewriter_model`

可以通过参数指定：
```python
rewriter = UnifiedRewriter(
    ai_type="tensorflow",
    ai_model_path="models/custom_model"
)
```

### AI类型选择
- `tensorflow`: 本地TensorFlow模型（推荐，完全本地）
- `openai`: OpenAI API（需要API密钥）
- `local`: 本地LLM（需要Ollama等服务）
- `offline`: 仅使用传统方法

