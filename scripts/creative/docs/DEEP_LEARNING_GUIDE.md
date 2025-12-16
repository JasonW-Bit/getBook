# 深度学习改写指南

## 概述

改写脚本现在集成了深度学习AI技术，能够进行更自然、更流畅的语言优化。相比传统的规则替换方法，深度学习改写具有以下优势：

1. **语义理解**：深入理解文本的语义和语境
2. **自然流畅**：生成更像人类写作的文本
3. **上下文连贯**：保持文本的连贯性和一致性
4. **智能优化**：在保持原意的基础上提升语言质量

## 使用方法

### 基础用法

```bash
# 使用深度学习AI进行改写（推荐）
python3 scripts/creative/rewrite_novel.py novel.txt \
  --use-ai --style=都市幽默

# 使用更强大的模型（GPT-4，质量更高）
python3 scripts/creative/rewrite_novel.py novel.txt \
  --use-ai --ai-type=openai --ai-model=gpt-4 --style=都市幽默
```

### 完整示例

```bash
# 1. 使用AI分析 + 深度学习改写
python3 scripts/creative/rewrite_novel.py novel.txt \
  --use-ai \
  --ai-type=openai \
  --ai-model=gpt-4 \
  --style=都市幽默 \
  --replace-names

# 2. 只使用AI改写（跳过分析，更快）
python3 scripts/creative/rewrite_novel.py novel.txt \
  --use-ai \
  --no-analyze \
  --style=都市幽默
```

## 深度学习改写的特点

### 1. 语义理解
- 理解文本的深层含义
- 分析人物性格和说话风格
- 理解故事的情感和氛围

### 2. 自然流畅
- 避免机械化的词汇替换
- 生成自然流畅的文本
- 保持文本的可读性

### 3. 上下文连贯
- 保持前后文的连贯性
- 理解上下文语境
- 确保改写后的文本与整体风格一致

### 4. 智能优化
- 在保持原意的基础上提升语言质量
- 根据风格特点自然融合
- 避免过度修改

## 模型选择

### GPT-4（推荐）
- **优点**：质量最高，理解能力最强，改写效果最好
- **缺点**：成本较高，速度较慢
- **适用**：重要作品、追求高质量改写

```bash
python3 scripts/creative/rewrite_novel.py novel.txt \
  --use-ai --ai-model=gpt-4 --style=都市幽默
```

### GPT-3.5-turbo（平衡）
- **优点**：成本较低，速度较快，质量良好
- **缺点**：理解能力略逊于GPT-4
- **适用**：一般作品、日常使用

```bash
python3 scripts/creative/rewrite_novel.py novel.txt \
  --use-ai --ai-model=gpt-3.5-turbo --style=都市幽默
```

### 本地LLM（免费）
- **优点**：完全免费，数据隐私
- **缺点**：质量可能不如GPT，需要本地部署
- **适用**：预算有限、注重隐私

```bash
python3 scripts/creative/rewrite_novel.py novel.txt \
  --use-ai --ai-type=local --ai-model=qwen:7b --style=都市幽默
```

## 改写质量对比

### 传统方法（规则替换）
```
原文：陈旭说："好的，我明白了。"
改写：陈旭在都市的咖啡厅里说："好的，我明白了。"，哈哈
问题：生硬插入，不自然
```

### 深度学习AI改写
```
原文：陈旭说："好的，我明白了。"
改写：陈旭在繁华都市的咖啡厅里，轻松地笑着说："好的，我明白了。"
优点：自然流畅，风格融合
```

## 最佳实践

### 1. 选择合适的模型
- 重要作品 → GPT-4
- 一般作品 → GPT-3.5-turbo
- 预算有限 → 本地LLM

### 2. 分段处理
- 大文件会自动分段处理
- 每段保持上下文连贯
- 确保整体风格一致

### 3. 结合分析功能
```bash
# 先分析，再改写（推荐）
python3 scripts/creative/rewrite_novel.py novel.txt \
  --use-ai --style=都市幽默

# 只改写，不分析（更快）
python3 scripts/creative/rewrite_novel.py novel.txt \
  --use-ai --no-analyze --style=都市幽默
```

### 4. 多次优化
- 可以多次运行，逐步优化
- 每次可以调整风格参数
- 对比不同版本的效果

## 成本估算

### GPT-4
- 输入：$0.03/1K tokens
- 输出：$0.06/1K tokens
- 10万字小说：约 $15-30

### GPT-3.5-turbo
- 输入：$0.0015/1K tokens
- 输出：$0.002/1K tokens
- 10万字小说：约 $1-2

### 本地LLM
- 完全免费
- 需要本地硬件支持

## 故障排除

### 1. API调用失败
- 检查API密钥是否正确
- 检查网络连接
- 检查账户余额

### 2. 改写质量不佳
- 尝试使用GPT-4模型
- 检查提示词是否清晰
- 尝试分段处理

### 3. 速度太慢
- 使用GPT-3.5-turbo
- 使用--no-analyze跳过分析
- 减少处理长度

## 技术原理

### 1. 上下文理解
- 提取前后文信息
- 分析整体语境
- 理解故事脉络

### 2. 语义分析
- 理解文本深层含义
- 分析人物性格
- 理解情感基调

### 3. 自然语言生成
- 使用大语言模型
- 生成自然流畅的文本
- 保持风格一致性

### 4. 质量控制
- 检查改写质量
- 确保原意不变
- 验证流畅性

## 总结

深度学习改写技术能够：
- ✅ 理解文本的深层语义
- ✅ 生成自然流畅的文本
- ✅ 保持上下文连贯
- ✅ 智能优化语言质量

相比传统方法，深度学习改写能够产生更自然、更流畅、更高质量的改写结果。

