# 批量爬取与训练代码集成说明

## 集成状态 ✅

批量爬取工具已与训练代码完全集成，形成完整的训练数据流水线。

## 数据流程

```
批量爬取 → 小说分析 → 生成训练数据 → TensorFlow训练 → 模型使用
```

## 数据格式兼容性

### 批量爬取工具生成格式
```
原始文本<TAB>改写文本<TAB>风格ID
```

### 训练脚本读取格式
```
原始文本<TAB>改写文本<TAB>风格ID
```

✅ **完全兼容**

## 完整流程

### 方式1: 使用流水线脚本（推荐）

```bash
# 完整流程：爬取→分析→生成→训练
python3 scripts/scraper/training_pipeline.py https://m.shuhaige.net 都市 10

# 使用AI生成改写样本
python3 scripts/scraper/training_pipeline.py https://m.shuhaige.net 都市 10 --use-ai

# 只训练（已有训练数据）
python3 scripts/scraper/training_pipeline.py https://m.shuhaige.net 都市 10 \
  --skip-scrape --skip-analyze --skip-generate
```

### 方式2: 分步执行

```bash
# 步骤1: 批量爬取
python3 scripts/scraper/batch_scraper.py https://m.shuhaige.net 都市 10 \
  --analyze --generate-data

# 步骤2: 训练模型
python3 scripts/ai/models/train_model.py data/training/novels/training_data.txt \
  --epochs=50 --batch-size=32
```

## 文件路径对应

| 功能 | 生成文件 | 使用文件 |
|------|---------|---------|
| 批量爬取 | `data/training/novels/training_data.txt` | ✅ |
| 训练脚本 | - | `data/training/novels/training_data.txt` |
| 模型保存 | - | `models/text_rewriter_model/` |
| 模型使用 | - | `models/text_rewriter_model/` |

## 数据验证

训练脚本会自动验证数据：
- ✅ 检查文件是否存在
- ✅ 验证TSV格式
- ✅ 检查数据长度（至少10字符）
- ✅ 统计有效数据量
- ✅ 显示错误数据（前5条）

## 集成检查清单

- [x] 数据格式兼容（TSV格式）
- [x] 文件路径对应
- [x] 风格ID映射一致
- [x] 错误处理完善
- [x] 流水线脚本集成
- [x] 文档说明完整

## 使用示例

### 完整示例

```bash
# 1. 爬取都市类型前10本小说
python3 scripts/scraper/batch_scraper.py https://m.shuhaige.net 都市 10 \
  --analyze --generate-data

# 2. 检查生成的数据
head -5 data/training/novels/training_data.txt

# 3. 训练模型
python3 scripts/ai/models/train_model.py data/training/novels/training_data.txt \
  --epochs=30 --batch-size=16

# 4. 使用模型
python3 scripts/creative/rewrite_novel.py novel.txt \
  --use-ai --ai-type=tensorflow --style=都市幽默
```

### 一键流水线

```bash
# 使用流水线脚本，自动完成所有步骤
python3 scripts/scraper/training_pipeline.py https://m.shuhaige.net 都市 10 \
  --use-ai --epochs=30
```

## 数据质量检查

训练脚本会自动检查：
- 数据文件是否存在
- 数据量是否足够（建议至少100条）
- 数据格式是否正确
- 风格ID是否有效

## 故障排除

### 训练数据为空
- 检查批量爬取是否成功
- 检查生成训练数据步骤是否执行
- 查看 `data/training/novels/training_data.txt` 文件

### 数据格式错误
- 确保使用TSV格式（制表符分隔）
- 检查是否有特殊字符
- 查看训练脚本的错误提示

### 模型训练失败
- 检查训练数据量（至少10条）
- 检查TensorFlow是否正确安装
- 查看错误日志

## 总结

✅ **完全集成**: 批量爬取工具与训练代码已完全集成
✅ **格式兼容**: 数据格式完全兼容
✅ **流程顺畅**: 从爬取到训练一键完成
✅ **文档完善**: 提供完整的使用文档

