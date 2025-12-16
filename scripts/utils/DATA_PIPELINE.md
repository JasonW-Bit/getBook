# 数据整理与训练流水线

## 功能概述

完整的训练数据流水线，从爬取数据到模型完善的自动化流程。

## 流程步骤

```
爬取数据 → 数据整理 → 生成训练数据 → 投递AI接口 → 增量训练 → 完善模型
```

## 使用方法

### 方式1: 完整流水线（推荐）

```bash
# 整理数据并投递给AI学习接口，进行增量训练
python3 scripts/utils/training_data_pipeline.py data/training/novels

# 使用AI生成改写样本
python3 scripts/utils/training_data_pipeline.py data/training/novels --use-ai
```

### 方式2: 分步执行

#### 步骤1: 整理数据

```bash
python3 scripts/utils/data_organizer.py data/training/novels \
  --target data/training/processed
```

功能：
- 清理文本（移除广告、无关内容）
- 按分类整理
- 提取元数据
- 计算质量分数
- 生成整理摘要

#### 步骤2: 生成训练数据

```bash
# 使用批量爬取工具生成训练数据
python3 scripts/scraper/batch_scraper.py https://m.shuhaige.net 都市 10 \
  --generate-data --output data/training/processed
```

#### 步骤3: 增量训练

```bash
# 在已有模型基础上继续训练
python3 scripts/ai/models/incremental_train.py data/training/processed/training_data.txt \
  --epochs=10 --learning-rate=0.0001
```

## 数据整理功能

### 清理内容
- ✅ 移除多余空白
- ✅ 移除广告和无关内容
- ✅ 移除重复章节标题
- ✅ 标准化格式

### 分类整理
- 按类型自动分类
- 保存清理后的文件
- 保存元数据JSON

### 质量评估
- 计算质量分数（0-100）
- 基于章节数、字符数、完整性
- 分类统计

## 增量训练功能

### 特点
- ✅ 在已有模型基础上继续训练
- ✅ 自动合并新词汇
- ✅ 使用较小学习率（避免破坏已有知识）
- ✅ 保留最佳模型

### 优势
- 不需要从头训练
- 快速融入新数据
- 保持模型稳定性

## 完整工作流

### 场景1: 首次训练

```bash
# 1. 批量爬取
python3 scripts/scraper/batch_scraper.py https://m.shuhaige.net 都市 10 \
  --analyze --generate-data

# 2. 整理数据
python3 scripts/utils/data_organizer.py data/training/novels

# 3. 基础训练
python3 scripts/ai/models/train_model.py data/training/processed/training_data.txt
```

### 场景2: 增量完善

```bash
# 1. 爬取新数据
python3 scripts/scraper/batch_scraper.py https://m.shuhaige.net 都市 5 \
  --generate-data

# 2. 整理新数据
python3 scripts/utils/data_organizer.py data/training/novels

# 3. 增量训练（完善模型）
python3 scripts/utils/training_data_pipeline.py data/training/novels --use-ai
```

## 数据投递流程

### 自动投递
流水线会自动：
1. 整理爬取的数据
2. 生成训练数据（TSV格式）
3. 投递给TensorFlow训练接口
4. 进行增量训练
5. 完善模型数据

### 数据格式
```
原始文本<TAB>改写文本<TAB>风格ID
```

### 模型更新
- 增量训练后自动保存
- 保留最佳模型
- 更新词汇表

## 文件结构

```
data/training/
├── novels/              # 原始爬取数据
│   └── 都市/
│       └── *.txt
├── processed/           # 整理后的数据
│   ├── 都市/
│   │   ├── *.txt       # 清理后的文件
│   │   └── *.json      # 元数据
│   ├── training_data.txt  # 训练数据
│   └── organization_summary.json  # 整理摘要
└── ...

models/text_rewriter_model/
├── best_model.h5       # 最佳模型
├── incremental_model.h5 # 增量训练模型
├── final_model.h5      # 最终模型
└── vocab.json          # 词汇表
```

## 最佳实践

1. **定期增量训练**: 每次爬取新数据后，进行增量训练
2. **数据质量**: 确保整理后的数据质量
3. **学习率**: 增量训练使用较小学习率（0.0001）
4. **训练轮数**: 增量训练通常10-20轮即可
5. **模型备份**: 训练前备份已有模型

## 故障排除

### 无法加载已有模型
- 检查模型文件是否存在
- 检查词汇表文件是否存在
- 可能需要先进行基础训练

### 增量训练失败
- 检查训练数据格式
- 检查数据量是否足够
- 查看错误日志

### 数据整理失败
- 检查源数据目录
- 检查文件编码
- 查看错误信息

