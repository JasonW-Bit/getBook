# 快速开始：从爬取到训练

## 完整流程（一键完成）

```bash
# 使用训练流水线，自动完成所有步骤
python3 scripts/scraper/training_pipeline.py https://m.shuhaige.net 都市 10
```

这将自动执行：
1. ✅ 批量爬取都市类型前10本小说
2. ✅ 分析小说特征
3. ✅ 生成训练数据
4. ✅ 训练TensorFlow模型

## 分步执行

### 步骤1: 批量爬取

```bash
python3 scripts/scraper/batch_scraper.py https://m.shuhaige.net 都市 10 \
  --analyze --generate-data
```

输出：
- `data/training/novels/都市/*.txt` - 小说文件
- `data/training/novels/training_data.txt` - 训练数据
- `data/training/novels/analysis.json` - 分析结果

### 步骤2: 训练模型

```bash
python3 scripts/ai/models/train_model.py data/training/novels/training_data.txt \
  --epochs=30 --batch-size=16
```

输出：
- `models/text_rewriter_model/best_model.h5` - 最佳模型
- `models/text_rewriter_model/vocab.json` - 词汇表

### 步骤3: 使用模型

```bash
python3 scripts/creative/rewrite_novel.py novel.txt \
  --use-ai --ai-type=tensorflow --style=都市幽默
```

## 数据流程验证

### 检查训练数据

```bash
# 查看训练数据
head -5 data/training/novels/training_data.txt

# 统计数据量
wc -l data/training/novels/training_data.txt
```

### 验证数据格式

训练脚本会自动验证：
- ✅ TSV格式正确
- ✅ 包含3列（原始文本、改写文本、风格ID）
- ✅ 数据长度足够（>10字符）

## 集成检查

✅ **数据格式**: 批量爬取工具生成的TSV格式与训练脚本完全兼容
✅ **文件路径**: 默认路径已配置好，无需手动指定
✅ **风格映射**: 风格ID映射一致
✅ **错误处理**: 完善的错误处理和验证

## 常见问题

### Q: 训练数据为空怎么办？
A: 检查批量爬取是否成功，确保使用了 `--generate-data` 选项

### Q: 如何增加训练数据量？
A: 增加爬取数量：`python3 scripts/scraper/batch_scraper.py ... 20`（改为20本）

### Q: 可以使用已有的小说文件吗？
A: 可以，将小说文件放在 `data/training/novels/` 目录下，然后运行生成训练数据步骤

