# 快速参考手册

## 常用命令

### 爬取

```bash
# 单本爬取
./scrape.sh <URL>

# 多网站批量爬取（推荐）
./multi_scrape.sh register <网站URL>          # 注册网站
./multi_scrape.sh list                        # 列出已注册网站
./multi_scrape.sh scrape <网站> <类型> <数量>  # 爬取小说

# 或直接使用Python
python3 scripts/scraper/multi_site_scraper.py --register <URL>
python3 scripts/scraper/multi_site_scraper.py --list-sites
python3 scripts/scraper/multi_site_scraper.py --site <网站> --category <类型> --count <数量>

# 批量爬取（旧版，保留兼容）
python3 scripts/scraper/batch_scraper.py <网站> <类型> <数量>
./batch_scrape.sh <网站> <类型> <数量>
```

### 改写

```bash
# 传统方法
python3 scripts/creative/rewrite_novel.py <文件> --style=都市幽默

# AI改写
python3 scripts/creative/rewrite_novel.py <文件> \
  --use-ai --ai-type=tensorflow --style=都市幽默
```

### 训练

```bash
# 基础训练
python3 scripts/ai/models/train_model.py <数据文件>

# 增量训练
python3 scripts/ai/models/incremental_train.py <数据文件>

# 完整流水线
./organize_and_train.sh <数据目录>
```

### 数据整理

```bash
# 整理数据
python3 scripts/utils/data_organizer.py <源目录>

# 完整流水线（整理+训练）
./organize_and_train.sh <数据目录>
```

## 文件路径

### 数据文件
- 爬取数据: `data/training/novels/<网站名>/<类型>/`
- 整理数据: `data/training/processed/`
- 训练数据: `data/training/processed/training_data.txt`
- 网站配置: `data/sites/sites.json`

### 模型文件
- 模型目录: `models/text_rewriter_model/`
- 最佳模型: `models/text_rewriter_model/best_model.h5`
- 词汇表: `models/text_rewriter_model/vocab.json`

### 小说文件
- 原始小说: `novels/<小说标题>/<小说标题>.txt`
- 改写小说: `novels/<小说标题>/rewritten/<小说标题>_rewritten.txt`

## 风格列表

- 现代、古典、简洁、华丽
- 悬疑、浪漫、幽默、严肃
- 科幻、武侠、青春、都市
- 古风、诗化、口语、正式
- 网络、文艺、都市幽默

## AI类型

- `tensorflow` - TensorFlow本地模型（推荐，完全本地）
- `openai` - OpenAI API（需要API密钥）
- `local` - 本地LLM（Ollama等）

## 常见问题

### Q: 如何批量爬取？
A: 
```bash
# 推荐：多网站系统
./multi_scrape.sh register <网站URL>
./multi_scrape.sh scrape <网站> <类型> <数量>

# 或旧版
python3 scripts/scraper/batch_scraper.py <网站> <类型> <数量>
```

### Q: 如何训练模型？
A: `python3 scripts/ai/models/train_model.py <训练数据文件>`

### Q: 如何增量训练？
A: `python3 scripts/ai/models/incremental_train.py <新数据文件>`

### Q: 如何整理数据？
A: `python3 scripts/utils/data_organizer.py <源目录>`

### Q: 完整流程是什么？
A: `./organize_and_train.sh data/training/novels`

## 文档索引

- [项目总览](PROJECT_OVERVIEW.md)
- [脚本说明](scripts/README.md)
- [多网站系统](scripts/scraper/MULTI_SITE_README.md) - 推荐阅读
- [数据流水线](scripts/utils/DATA_PIPELINE.md)
- [批量爬取](scripts/scraper/BATCH_SCRAPER_README.md) - 旧版文档

