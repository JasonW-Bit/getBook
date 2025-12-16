# 多网站爬取系统 - 快速开始

## 快速开始

### 1. 注册网站（首次使用）

```bash
python3 scripts/scraper/multi_site_scraper.py --register https://m.shuhaige.net
```

### 2. 查看已注册的网站

```bash
python3 scripts/scraper/multi_site_scraper.py --list-sites
```

### 3. 爬取小说

```bash
# 爬取都市类已完结小说10本
python3 scripts/scraper/multi_site_scraper.py \
  --site m.shuhaige.net \
  --category 都市 \
  --count 10 \
  --filter-completed
```

### 4. 生成训练数据

```bash
python3 scripts/scraper/generate_training_data.py --output data/training
```

## 数据存放位置

```
data/training/
├── novels/
│   └── m.shuhaige.net/      # 网站名
│       └── 都市/            # 类型
│           ├── 小说1.txt
│           └── 小说1.json
└── processed/
    └── training_data.txt    # 训练数据
```

## 完整示例

```bash
# 1. 注册网站
python3 scripts/scraper/multi_site_scraper.py --register https://m.shuhaige.net

# 2. 爬取都市类小说
python3 scripts/scraper/multi_site_scraper.py \
  --site m.shuhaige.net \
  --category 都市 \
  --count 10

# 3. 爬取玄幻类小说
python3 scripts/scraper/multi_site_scraper.py \
  --site m.shuhaige.net \
  --category 玄幻 \
  --count 5

# 4. 生成训练数据
python3 scripts/scraper/generate_training_data.py

# 5. 训练模型
python3 scripts/ai/models/train_model.py \
  --data data/training/processed/training_data.txt
```

## 支持的网站

- ✅ m.shuhaige.net (书海阁)

## 添加新网站

1. 创建适配器文件：`scripts/scraper/adapters/new_site_adapter.py`
2. 在 `adapters/__init__.py` 中注册
3. 注册网站：`--register https://new-site.com`

详见 `MULTI_SITE_README.md`

