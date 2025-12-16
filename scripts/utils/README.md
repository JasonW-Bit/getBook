# 工具脚本说明

## 数据整理工具

### `data_organizer.py`

整理爬取的小说数据，准备用于训练。

**功能**:
- 清理文本（移除广告、无关内容）
- 按分类整理
- 提取元数据
- 计算质量分数
- 生成整理摘要

**使用**:
```bash
python3 scripts/utils/data_organizer.py data/training/novels \
  --target data/training/processed
```

## 训练数据流水线

### `training_data_pipeline.py`

完整的训练数据流水线，整合数据整理、生成训练数据和增量训练。

**功能**:
- 自动整理数据
- 生成训练数据
- 投递给AI学习接口
- 增量训练完善模型

**使用**:
```bash
python3 scripts/utils/training_data_pipeline.py data/training/novels \
  --use-ai --epochs=10
```

## 增量训练

### `incremental_train.py` (在 `scripts/ai/models/`)

在已有模型基础上继续训练，完善模型数据。

**功能**:
- 加载已有模型
- 合并新词汇
- 增量训练
- 合并模型

**使用**:
```bash
python3 scripts/ai/models/incremental_train.py data/training/processed/training_data.txt \
  --epochs=10 --learning-rate=0.0001
```

## 完整工作流

### 首次训练
```bash
# 1. 爬取数据
python3 scripts/scraper/batch_scraper.py https://m.shuhaige.net 都市 10 --generate-data

# 2. 整理并训练
./organize_and_train.sh data/training/novels
```

### 增量完善
```bash
# 1. 爬取新数据
python3 scripts/scraper/batch_scraper.py https://m.shuhaige.net 都市 5 --generate-data

# 2. 整理并增量训练
./organize_and_train.sh data/training/novels --use-ai
```

## 数据流程

```
爬取数据 → 数据整理 → 生成训练数据 → 投递AI接口 → 增量训练 → 完善模型
```

## 详细文档

- `DATA_PIPELINE.md` - 完整流水线说明

