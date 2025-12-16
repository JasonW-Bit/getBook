# 语言模型集成指南

## 快速开始

### 1. 安装依赖

```bash
# 基础依赖
pip install transformers torch huggingface_hub

# 如果需要GPU加速（CUDA 11.8）
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 如果需要GPU加速（CUDA 12.1）
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### 2. 查看可用模型

```bash
python3 scripts/ai/models/model_downloader.py list
```

### 3. 下载模型

```bash
# 下载推荐的轻量级模型（3.6GB）
python3 scripts/ai/models/model_downloader.py download --model qwen-1.8b-chat

# 下载高性能模型（14GB）
python3 scripts/ai/models/model_downloader.py download --model qwen-7b-chat
```

### 4. 使用模型

在代码中使用：

```python
from scripts.ai.analyzers.ai_analyzer import AIAnalyzerFactory

# 创建HuggingFace分析器
analyzer = AIAnalyzerFactory.create_analyzer(
    analyzer_type='huggingface',
    model_path='models/pretrained/Qwen_Qwen-7B-Chat',
    model_type='qwen'
)

# 改写文本
if analyzer:
    result = analyzer.rewrite_text(
        text="原始文本",
        style="都市幽默"
    )
    print(result)
```

## 推荐模型

| 模型 | 大小 | 内存需求 | 适用场景 |
|------|------|---------|---------|
| Qwen-1.8B-Chat | 3.6GB | 8GB | 快速测试、资源受限 |
| ChatGLM3-6B | 12GB | 16GB | 对话生成、文本改写 |
| Qwen-7B-Chat | 14GB | 16GB | **推荐** 文本改写、创作 |
| Baichuan2-7B-Chat | 14GB | 16GB | 文本改写、对话 |

## 详细文档

查看完整文档：`docs/guides/MODEL_DOWNLOAD_GUIDE.md`

