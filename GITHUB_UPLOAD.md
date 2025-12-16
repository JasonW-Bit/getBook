# 上传项目到 GitHub 指南

## 📋 前置条件

1. **GitHub 账号**：确保你有一个 GitHub 账号
2. **Git 已配置**：确保本地 Git 已配置用户名和邮箱

## 🚀 上传步骤

### 1. 检查 Git 配置（如果还没配置）

```bash
git config --global user.name "你的用户名"
git config --global user.email "你的邮箱"
```

### 2. 在 GitHub 上创建新仓库

1. 登录 GitHub
2. 点击右上角的 `+` 号，选择 `New repository`
3. 填写仓库信息：
   - **Repository name**: `getBook` (或你喜欢的名字)
   - **Description**: `多网站小说爬取与AI改写系统`
   - **Visibility**: 选择 `Public` 或 `Private`
   - **⚠️ 重要**: **不要**勾选 "Initialize this repository with a README"（因为我们已经有了）
4. 点击 `Create repository`

### 3. 连接本地仓库到 GitHub

GitHub 创建仓库后会显示一个页面，复制其中的命令。或者使用以下命令：

```bash
# 进入项目目录
cd /Users/jackchen/Documents/getBook

# 添加远程仓库（将 YOUR_USERNAME 替换为你的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/getBook.git

# 或者使用 SSH（如果你配置了 SSH key）
# git remote add origin git@github.com:YOUR_USERNAME/getBook.git
```

### 4. 推送代码到 GitHub

```bash
# 重命名分支为 main（GitHub 默认使用 main）
git branch -M main

# 推送代码
git push -u origin main
```

### 5. 验证上传

访问 `https://github.com/YOUR_USERNAME/getBook` 查看你的仓库。

## 📝 后续更新

以后每次修改代码后，使用以下命令更新 GitHub：

```bash
# 查看修改
git status

# 添加修改的文件
git add .

# 提交修改
git commit -m "描述你的修改"

# 推送到 GitHub
git push
```

## ⚠️ 注意事项

1. **大文件已排除**：模型文件（.h5, .ckpt 等）和训练数据已通过 `.gitignore` 排除，不会上传
2. **敏感信息**：确保没有在代码中硬编码 API 密钥、密码等敏感信息
3. **许可证**：考虑添加 LICENSE 文件（如 MIT、Apache 2.0 等）

## 🔧 如果遇到问题

### 问题：推送被拒绝（push rejected）

```bash
# 如果远程仓库有内容（比如 README），先拉取
git pull origin main --allow-unrelated-histories

# 解决冲突后再次推送
git push -u origin main
```

### 问题：需要更新远程仓库地址

```bash
# 查看当前远程地址
git remote -v

# 更新远程地址
git remote set-url origin https://github.com/YOUR_USERNAME/getBook.git
```

## 📦 已排除的文件

以下文件/目录不会上传到 GitHub（已在 `.gitignore` 中配置）：

- 模型文件：`models/text_rewriter_model/*.h5`, `models/pretrained/`
- 训练数据：`data/training/novels/`, `data/training/processed/`
- 临时文件：`*.log`, `*.tmp`, `/tmp/`
- Python 缓存：`__pycache__/`, `*.pyc`
- IDE 配置：`.vscode/`, `.idea/`

## ✅ 完成！

上传成功后，你的项目就可以在 GitHub 上被访问了。记得定期提交和推送你的更改！

