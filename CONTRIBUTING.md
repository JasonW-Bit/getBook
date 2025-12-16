# 贡献指南

## 项目结构

项目已按功能分类整理，结构清晰：

```
getBook/
├── scripts/
│   ├── scraper/      # 爬取相关
│   ├── utils/        # 工具脚本
│   ├── ai/           # AI相关
│   └── creative/     # 创意处理
├── data/             # 数据目录
├── models/           # 模型文件
├── novels/           # 小说文件
└── docs/             # 文档
```

## 代码规范

### Python代码
- 使用UTF-8编码
- 遵循PEP 8规范
- 添加适当的注释和文档字符串

### 文件命名
- Python脚本：`snake_case.py`
- 文档文件：`UPPER_CASE.md`
- Shell脚本：`lowercase.sh`

## 提交规范

### 提交信息格式
```
类型: 简短描述

详细说明（可选）
```

类型：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `refactor`: 代码重构
- `test`: 测试相关

## 开发流程

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 文档更新

修改代码时，请同步更新相关文档：
- README.md
- 对应的功能文档
- 代码注释

