# AI功能配置指南

## 概述

改写脚本现在支持使用深度学习AI来增强阅读、分析和理解能力。支持两种AI服务：

1. **OpenAI API** - 使用GPT模型（需要API密钥）
2. **本地LLM** - 使用Ollama等本地服务（免费，需要本地部署）

## OpenAI配置

### 1. 获取API密钥

1. 访问 [OpenAI官网](https://platform.openai.com/)
2. 注册/登录账号
3. 创建API密钥

### 2. 设置环境变量

**macOS/Linux:**
```bash
export OPENAI_API_KEY="your-api-key-here"
```

**Windows:**
```cmd
set OPENAI_API_KEY=your-api-key-here
```

**永久设置（推荐）:**

在 `~/.zshrc` 或 `~/.bashrc` 中添加：
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 3. 安装依赖

```bash
pip install openai
```

### 4. 使用示例

```bash
# 使用OpenAI进行AI分析和改写
python3 scripts/creative/rewrite_novel.py novel.txt \
  --use-ai --ai-type=openai --style=悬疑

# 指定模型
python3 scripts/creative/rewrite_novel.py novel.txt \
  --use-ai --ai-type=openai --ai-model=gpt-4 --style=古典
```

## 本地LLM配置（Ollama）

### 1. 安装Ollama

访问 [Ollama官网](https://ollama.ai/) 下载并安装。

### 2. 下载模型

```bash
# 下载中文模型（推荐）
ollama pull qwen:7b

# 或其他模型
ollama pull llama2
ollama pull mistral
```

### 3. 启动服务

Ollama默认在 `http://localhost:11434` 运行。

### 4. 使用示例

```bash
# 使用本地LLM
python3 scripts/creative/rewrite_novel.py novel.txt \
  --use-ai --ai-type=local --ai-model=qwen:7b --style=简洁
```

## AI功能说明

### 分析功能

使用AI可以：
- **更准确的人物识别**：AI能理解上下文，准确识别人物
- **深度故事分析**：理解故事主题、情节结构、情感基调
- **人物关系分析**：识别人物之间的关系和角色定位

### 改写功能

使用AI可以：
- **智能风格转换**：根据风格要求智能改写文本
- **保持原意**：在改变风格的同时保持原意
- **自然流畅**：生成的文本更自然流畅

## 成本说明

### OpenAI API

- **GPT-3.5-turbo**: 约 $0.0015/1K tokens（输入），$0.002/1K tokens（输出）
- **GPT-4**: 约 $0.03/1K tokens（输入），$0.06/1K tokens（输出）
- 一部10万字的小说约需要 100K-200K tokens

### 本地LLM

- **完全免费**：运行在本地，无需API费用
- **需要硬件**：建议8GB+内存，支持GPU更佳
- **速度较慢**：处理速度取决于硬件配置

## 推荐配置

### 快速测试
```bash
# 使用传统方法（免费，快速）
python3 scripts/creative/rewrite_novel.py novel.txt --style=简洁
```

### 高质量改写
```bash
# 使用OpenAI GPT-4（需要API密钥，质量最高）
python3 scripts/creative/rewrite_novel.py novel.txt \
  --use-ai --ai-type=openai --ai-model=gpt-4 --style=悬疑
```

### 本地使用
```bash
# 使用本地LLM（免费，需要本地部署）
python3 scripts/creative/rewrite_novel.py novel.txt \
  --use-ai --ai-type=local --ai-model=qwen:7b --style=简洁
```

## 故障排除

### OpenAI API错误

1. **API密钥未设置**
   - 检查环境变量：`echo $OPENAI_API_KEY`
   - 确保已正确设置

2. **API配额不足**
   - 检查OpenAI账户余额
   - 升级账户或等待配额重置

3. **网络问题**
   - 检查网络连接
   - 可能需要代理

### 本地LLM错误

1. **服务未启动**
   - 检查Ollama是否运行：`curl http://localhost:11434/api/tags`
   - 启动Ollama服务

2. **模型未下载**
   - 使用 `ollama list` 查看已下载的模型
   - 使用 `ollama pull <model>` 下载模型

3. **内存不足**
   - 使用较小的模型
   - 关闭其他占用内存的程序

## 性能优化

1. **分段处理**：大文件会自动分段处理，避免token限制
2. **缓存结果**：分析结果会保存，避免重复分析
3. **混合模式**：可以只对关键部分使用AI，其他使用传统方法

