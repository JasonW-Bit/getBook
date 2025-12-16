# TensorFlow本地模型搭建指南

## 概述

本项目支持使用TensorFlow在本地搭建深度学习语言模型，用于文本改写。完全本地化，无需外部API，数据隐私有保障。

## 安装依赖

### 1. 安装TensorFlow

```bash
# CPU版本（推荐用于测试）
pip install tensorflow>=2.10.0

# GPU版本（如果有NVIDIA GPU，推荐）
pip install tensorflow-gpu>=2.10.0
```

### 2. 安装其他依赖

```bash
pip install numpy>=1.21.0
```

### 3. 验证安装

```bash
python3 -c "import tensorflow as tf; print(f'TensorFlow版本: {tf.__version__}'); print(f'GPU可用: {len(tf.config.list_physical_devices(\"GPU\")) > 0}')"
```

## 模型架构

### 架构特点

1. **Transformer风格**：使用多头注意力机制
2. **风格嵌入**：支持多种风格同时训练
3. **字符级处理**：适合中文文本
4. **端到端训练**：从原始文本到改写文本

### 模型结构

```
输入文本 → 文本嵌入
输入风格 → 风格嵌入
    ↓
融合嵌入
    ↓
Transformer编码器（2层）
    ↓
输出层（词汇表大小）
```

## 训练模型

### 1. 准备训练数据

创建训练数据文件（TSV格式）：

```
原始文本<TAB>改写文本<TAB>风格ID
```

示例 `data/training_data.txt`：
```
陈旭说：好的，我明白了。	陈旭在都市的咖啡厅里，轻松地笑着说：好的，我明白了。	18
他很高兴。	他超级高兴。	6
她走在街上。	她穿梭在都市的街道上。	11
```

### 风格ID映射

- 0: 现代
- 1: 古典
- 2: 简洁
- 3: 华丽
- 4: 悬疑
- 5: 浪漫
- 6: 幽默
- 7: 严肃
- 8: 科幻
- 9: 武侠
- 10: 青春
- 11: 都市
- 12: 古风
- 13: 诗化
- 14: 口语
- 15: 正式
- 16: 网络
- 17: 文艺
- 18: 都市幽默

### 2. 训练模型

```bash
python3 scripts/creative/train_model.py data/training_data.txt models/text_rewriter
```

参数说明：
- `data/training_data.txt`: 训练数据文件
- `models/text_rewriter`: 模型保存路径

### 3. 训练参数调整

编辑 `train_model.py` 可以调整：
- `epochs`: 训练轮数（默认20）
- `batch_size`: 批次大小（默认16）
- `validation_split`: 验证集比例（默认0.2）

## 使用模型

### 1. 在改写脚本中使用

```bash
# 使用TensorFlow模型
python3 scripts/creative/rewrite_novel.py novel.txt \
  --use-ai --ai-type=tensorflow --style=都市幽默
```

### 2. 指定模型路径

```bash
python3 scripts/creative/rewrite_novel.py novel.txt \
  --use-ai --ai-type=tensorflow \
  --ai-model-path=models/my_model \
  --style=都市幽默
```

## 模型优化

### 1. 增加训练数据

- 收集更多改写样本
- 覆盖更多风格
- 提高数据质量

### 2. 调整模型参数

编辑 `tensorflow_model.py`：
- `embedding_dim`: 词向量维度（默认256）
- `style_embedding_dim`: 风格嵌入维度（默认64）
- Transformer层数：默认2层，可以增加到4-6层

### 3. 使用预训练模型

可以加载预训练的中文BERT或GPT模型作为基础：
- 中文BERT
- 中文GPT
- 其他中文预训练模型

## 性能优化

### 1. 使用GPU

```bash
# 检查GPU
python3 -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
```

### 2. 批量处理

在 `tensorflow_model.py` 中调整 `batch_size`

### 3. 模型量化

训练后可以量化模型以减少内存占用：
```python
converter = tf.lite.TFLiteConverter.from_saved_model(model_path)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()
```

## 故障排除

### 1. 内存不足

- 减少 `batch_size`
- 减少 `max_length`
- 使用模型量化

### 2. 训练速度慢

- 使用GPU
- 减少训练数据量
- 减少模型复杂度

### 3. 模型效果不佳

- 增加训练数据
- 增加训练轮数
- 调整学习率
- 使用预训练模型

## 模型文件结构

```
models/text_rewriter_model/
├── best_model.h5          # 最佳模型权重
├── final_model.h5         # 最终模型权重
└── vocab.json            # 词汇表
```

## 与API模型对比

| 特性 | TensorFlow本地 | OpenAI API |
|------|---------------|------------|
| 成本 | 免费 | 按token收费 |
| 速度 | 取决于硬件 | 网络延迟 |
| 隐私 | 完全本地 | 数据上传 |
| 质量 | 取决于训练 | 高质量 |
| 部署 | 需要训练 | 直接使用 |

## 最佳实践

1. **数据准备**：收集高质量的改写样本
2. **模型训练**：使用GPU加速训练
3. **模型评估**：在验证集上评估效果
4. **持续优化**：根据使用反馈调整模型

## 下一步

- 集成预训练的中文模型
- 支持更多风格
- 优化模型架构
- 添加模型评估指标

