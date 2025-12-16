# 项目整理说明

## 整理完成时间

2025-12-13

## 整理内容

### 1. 文档结构统一

- ✅ 更新主README，反映多网站系统
- ✅ 更新项目总览（PROJECT_OVERVIEW.md）
- ✅ 更新项目结构文档（docs/PROJECT_STRUCTURE.md）
- ✅ 更新文档索引（docs/INDEX.md）
- ✅ 更新快速参考（QUICK_REFERENCE.md）

### 2. 代码组织

- ✅ 创建网站适配器架构（adapters/）
- ✅ 实现多网站爬取系统（multi_site_scraper.py）
- ✅ 创建网站管理器（site_manager.py）
- ✅ 统一训练数据生成（generate_training_data.py）

### 3. 便捷脚本

- ✅ 创建多网站爬取脚本（multi_scrape.sh）
- ✅ 保留旧版脚本（兼容性）

### 4. 数据组织

- ✅ 按网站分类：`data/training/novels/<网站名>/`
- ✅ 按类型分类：`data/training/novels/<网站名>/<类型>/`
- ✅ 网站配置：`data/sites/sites.json`

## 项目结构

```
getBook/
├── scripts/
│   ├── scraper/
│   │   ├── adapters/              # 网站适配器（新增）
│   │   ├── multi_site_scraper.py  # 多网站爬取器（新增，推荐）
│   │   ├── site_manager.py        # 网站管理器（新增）
│   │   └── generate_training_data.py  # 训练数据生成（新增）
│   ├── creative/                  # 创意处理
│   ├── ai/                        # AI模块
│   └── utils/                     # 工具脚本
├── data/
│   ├── sites/                     # 网站配置（新增）
│   └── training/
│       ├── novels/                # 按网站/类型分类（新结构）
│       └── processed/             # 处理后的数据
├── models/                        # 模型文件
├── novels/                        # 单本爬取的小说
├── docs/                          # 项目文档
├── multi_scrape.sh                # 多网站爬取脚本（新增）
├── scrape.sh                      # 单本爬取脚本
├── batch_scrape.sh                # 批量爬取脚本（旧版）
└── organize_and_train.sh          # 整理训练脚本
```

## 主要改进

### 1. 多网站支持

- 每个网站对应一个适配器
- 自动发现和解析新网站
- 灵活的网站管理

### 2. 数据组织优化

- 按网站和类型分类存放
- 清晰的目录结构
- 便于管理和查找

### 3. 文档完善

- 统一文档结构
- 更新所有文档
- 添加快速开始指南

### 4. 脚本优化

- 新增多网站爬取脚本
- 保留旧版脚本（兼容性）
- 改进错误处理

## 使用建议

### 新用户

1. 阅读 [README.md](README.md)
2. 查看 [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
3. 使用多网站系统：`./multi_scrape.sh`

### 老用户

1. 迁移到多网站系统
2. 使用新的数据组织方式
3. 查看 [MULTI_SITE_README.md](scripts/scraper/MULTI_SITE_README.md)

## 兼容性

- ✅ 保留旧版脚本（batch_scraper.py）
- ✅ 保留旧版数据格式支持
- ✅ 向后兼容

## 下一步

1. 添加更多网站适配器
2. 优化训练数据生成
3. 改进AI模型性能

