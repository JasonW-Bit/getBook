# 数据存储结构说明

## 数据组织原则

所有爬取的小说数据按照以下结构组织：

```
data/training/novels/
└── <网站名>/              # 第一层：按网站分类
    └── <类型>/            # 第二层：按类型分类
        └── <小说名>/      # 第三层：按小说名分类
            ├── <小说名>.txt
            └── <小说名>.json
```

## 完整示例

```
data/training/novels/
└── m.shuhaige.net/
    ├── 都市/
    │   ├── 重生香江之金融帝国/
    │   │   ├── 重生香江之金融帝国.txt
    │   │   └── 重生香江之金融帝国.json
    │   ├── 魔道祖师/
    │   │   ├── 魔道祖师.txt
    │   │   └── 魔道祖师.json
    │   └── 开局被甩？系统奖励根本停不下来/
    │       ├── 开局被甩？系统奖励根本停不下来.txt
    │       └── 开局被甩？系统奖励根本停不下来.json
    └── 玄幻/
        └── ...
```

## 文件说明

### TXT文件
- 包含完整的小说内容
- 格式：标题、作者、简介、章节内容
- 用于阅读和训练

### JSON文件
- 包含小说元数据
- 字段：title, author, description, url, site, category, chapters, total_chars等
- 用于数据管理和统计

## 数据迁移

如果数据不符合新结构，可以使用迁移工具：

```bash
# 预览迁移
python3 scripts/utils/migrate_to_new_structure.py data/training/novels --site m.shuhaige.net

# 执行迁移
python3 scripts/utils/migrate_to_new_structure.py data/training/novels --site m.shuhaige.net --execute
```

## 清理空文件夹

定期清理空文件夹，保持目录结构整洁：

```bash
# 预览要删除的空文件夹
python3 scripts/utils/cleanup_empty_folders.py data/training/novels

# 实际删除
python3 scripts/utils/cleanup_empty_folders.py data/training/novels --execute
```

## 一键整理

使用便捷脚本一键完成清理和迁移：

```bash
./scripts/utils/cleanup_and_migrate.sh
```

## 优势

1. **清晰的组织**: 三层结构，易于查找和管理
2. **避免冲突**: 不同网站、类型的小说互不干扰
3. **便于扩展**: 添加新网站或类型只需创建新目录
4. **易于统计**: 可以按网站、类型、小说进行统计

