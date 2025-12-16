# 脚本重组说明

## 重组完成 ✅

所有脚本已按功能分类整理，目录结构更加清晰。

## 重组内容

### 1. 爬取脚本 → `scraper/`
- `novel_scraper.py` → `scraper/novel_scraper.py`

### 2. 工具脚本 → `utils/`
- `migrate_novels.py` → `utils/migrate_novels.py`

### 3. AI脚本 → `ai/`
- `ai_analyzer.py` → `ai/analyzers/ai_analyzer.py`
- `tensorflow_model.py` → `ai/models/tensorflow_model.py`
- `train_model.py` → `ai/models/train_model.py`

### 4. 创意处理脚本 → `creative/`
- `rewrite_novel.py` → `creative/rewrite_novel.py` (保留)
- `text_processor.py` → `creative/processors/text_processor.py`
- `creative_process.py` → `creative/processors/creative_process.py`
- `transform_format.py` → `creative/transformers/transform_format.py`
- `generate_content.py` → `creative/generators/generate_content.py`
- 所有文档 → `creative/docs/`

## 更新的文件

### Shell脚本
- `scrape.sh`: 更新路径为 `scripts/scraper/novel_scraper.py`
- `migrate.sh`: 更新路径为 `scripts/utils/migrate_novels.py`

### Python脚本
- `rewrite_novel.py`: 更新导入路径
- `ai_analyzer.py`: 更新TensorFlow模型导入路径
- `train_model.py`: 更新导入路径

## 新的目录结构

```
scripts/
├── scraper/          # 爬取脚本
├── utils/            # 工具脚本
├── ai/               # AI脚本
│   ├── analyzers/    # AI分析器
│   └── models/       # AI模型
├── creative/         # 创意处理
│   ├── processors/   # 文本处理器
│   ├── transformers/ # 格式转换器
│   ├── generators/   # 内容生成器
│   └── docs/         # 文档
└── README.md         # 说明文档
```

## 使用方式

所有使用方式保持不变，脚本会自动处理导入路径。

### 爬取小说
```bash
./scrape.sh <URL>
# 或
python3 scripts/scraper/novel_scraper.py <URL>
```

### 改写小说
```bash
python3 scripts/creative/rewrite_novel.py <文件> [选项]
```

### 训练模型
```bash
python3 scripts/ai/models/train_model.py <数据文件>
```

## 优势

1. **清晰分类**: 按功能分类，易于查找
2. **模块化**: 每个模块职责明确
3. **可维护**: 结构清晰，便于维护和扩展
4. **兼容性**: 保持原有使用方式不变

