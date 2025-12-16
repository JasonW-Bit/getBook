# 快速开始指南

## 安装

1. **克隆或下载项目**
   ```bash
   cd getBook
   ```

2. **安装依赖**
   ```bash
   python3 -m pip install -r requirements.txt
   ```

## 使用

### 爬取小说

**方式一：使用便捷脚本（推荐）**
```bash
./scrape.sh https://m.shuhaige.net/350415/
```

**方式二：直接运行Python脚本**
```bash
python3 scripts/novel_scraper.py https://m.shuhaige.net/350415/
```

### 迁移旧文件

如果你有之前生成的小说文件在根目录，可以使用迁移工具：

```bash
./migrate.sh
```

或

```bash
python3 scripts/migrate_novels.py
```

## 输出位置

所有小说文件保存在 `novels/` 文件夹中，每部小说有独立的文件夹：

```
novels/
└── 小说标题/
    └── 小说标题.txt
```

## 更多信息

- 详细使用说明：查看 [README.md](../README.md)
- 错误处理：查看 [ERROR_HANDLING.md](ERROR_HANDLING.md)
- 文件迁移：查看 [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)
- 项目结构：查看 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

