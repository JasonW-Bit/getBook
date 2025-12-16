# 模型下载和集成指南

## 概述

本项目支持从HuggingFace等平台下载和集成中文语言模型，用于文本改写、分析和生成任务。

## 推荐模型

### 1. 轻量级模型（适合资源受限环境）

- **Qwen-1.8B-Chat** (3.6GB)
  - 模型ID: `Qwen/Qwen-1_8B-Chat`
  - 最低内存: 8GB
  - 适合: 快速测试、资源受限环境

### 2. 中等规模模型（推荐）

- **ChatGLM3-6B** (12GB)
  - 模型ID: `THUDM/chatglm3-6b`
  - 最低内存: 16GB
  - 适合: 文本改写、对话生成

- **Qwen-7B-Chat** (14GB)
  - 模型ID: `Qwen/Qwen-7B-Chat`
  - 最低内存: 16GB
  - 适合: 文本改写、创作、对话

- **Baichuan2-7B-Chat** (14GB)
  - 模型ID: `baichuan-inc/Baichuan2-7B-Chat`
  - 最低内存: 16GB
  - 适合: 文本改写、对话生成

## 安装依赖

```bash
# 安装基础依赖
pip install transformers torch

# 如果需要使用HuggingFace Hub
pip install huggingface_hub

# 如果需要使用ChatGLM
pip install cpm_kernels
```

## 下载模型

### 方法1: 使用模型下载工具（推荐）

```bash
# 列出所有可用模型
python3 scripts/ai/models/model_downloader.py list

# 查看推荐模型（用于改写任务）
python3 scripts/ai/models/model_downloader.py recommend --use-case 改写

# 下载推荐模型
python3 scripts/ai/models/model_downloader.py download --model qwen-7b-chat

# 检查模型是否已下载
python3 scripts/ai/models/model_downloader.py check --model qwen-7b-chat
```

### 方法2: 使用HuggingFace CLI

```bash
# 安装HuggingFace CLI
pip install huggingface_hub

# 登录（可选，用于访问私有模型）
huggingface-cli login

# 下载模型
huggingface-cli download Qwen/Qwen-7B-Chat --local-dir models/pretrained/Qwen_Qwen-7B-Chat
```

### 方法3: 使用Python代码

```python
from scripts.ai.models.model_downloader import ModelDownloader

downloader = ModelDownloader()

# 下载模型
downloader.download_recommended_model('qwen-7b-chat')

# 或直接下载
downloader.download_from_huggingface('Qwen/Qwen-7B-Chat')
```

## 集成到项目

### 1. 在代码中使用

```python
from scripts.ai.models.huggingface_model import HuggingFaceTextRewriter

# 初始化改写器
rewriter = HuggingFaceTextRewriter(
    model_path='models/pretrained/Qwen_Qwen-7B-Chat',
    model_type='qwen'
)

# 改写文本
result = rewriter.rewrite(
    text="这是一个测试文本",
    style="都市幽默",
    context="小说章节上下文"
)
print(result)
```

### 2. 集成到AI分析器

```python
from scripts.ai.integration import AIAnalyzerFactory

# 创建HuggingFace分析器
analyzer = AIAnalyzerFactory.create(
    ai_type='huggingface',
    model_path='models/pretrained/Qwen_Qwen-7B-Chat',
    model_type='qwen'
)

# 使用分析器
if analyzer:
    result = analyzer.rewrite_text(
        text="原始文本",
        style="都市幽默"
    )
```

### 3. 在Pipeline中使用

修改 `scripts/core/pipeline.py` 或使用命令行参数：

```bash
python3 scripts/core/pipeline.py \
  --site m.shuhaige.net \
  --category 都市 \
  --count 10 \
  --use-ai \
  --ai-type huggingface \
  --model-path models/pretrained/Qwen_Qwen-7B-Chat
```

## 模型路径配置

下载的模型会保存在 `models/pretrained/` 目录下，目录结构如下：

```
models/pretrained/
├── Qwen_Qwen-7B-Chat/
│   ├── config.json
│   ├── tokenizer.json
│   ├── model.safetensors
│   └── ...
├── THUDM_chatglm3-6b/
│   └── ...
└── ...
```

## 性能优化

### 1. 使用GPU加速

如果有NVIDIA GPU，模型会自动使用GPU加速。确保已安装CUDA版本的PyTorch：

```bash
# CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### 2. 使用量化模型

对于资源受限的环境，可以使用量化模型：

```python
from transformers import BitsAndBytesConfig

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16
)

model = AutoModelForCausalLM.from_pretrained(
    model_path,
    quantization_config=quantization_config
)
```

### 3. 使用CPU优化

如果只能使用CPU，可以：

- 使用较小的模型（如Qwen-1.8B）
- 减少max_length参数
- 使用量化模型

## 常见问题

### 1. 下载速度慢

- 使用镜像站点
- 使用HuggingFace CLI的 `--resume-download` 参数
- 考虑使用国内镜像（如魔塔社区）

### 2. 内存不足

- 使用较小的模型
- 使用量化模型
- 减少batch_size
- 使用CPU模式（虽然慢但内存占用小）

### 3. 模型加载失败

- 检查模型路径是否正确
- 确保已安装所有依赖
- 检查模型文件是否完整下载

### 4. 生成速度慢

- 使用GPU加速
- 减少max_length
- 使用较小的模型
- 考虑使用量化模型

## 模型选择建议

| 使用场景 | 推荐模型 | 原因 |
|---------|---------|------|
| 快速测试 | Qwen-1.8B-Chat | 体积小，速度快 |
| 文本改写 | Qwen-7B-Chat | 性能好，支持中文 |
| 对话生成 | ChatGLM3-6B | 对话能力强 |
| 创作任务 | Qwen-7B-Chat | 创作能力强 |
| 资源受限 | Qwen-1.8B-Chat | 内存占用小 |

## 相关文件

- `scripts/ai/models/model_downloader.py` - 模型下载工具
- `scripts/ai/models/huggingface_model.py` - HuggingFace模型集成
- `scripts/ai/models/huggingface_analyzer.py` - HuggingFace分析器
- `scripts/ai/integration.py` - AI分析器工厂（已集成）

## 下一步

1. 下载推荐的模型
2. 测试模型性能
3. 根据需求调整参数
4. 集成到训练流程中

