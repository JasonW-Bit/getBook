# 推送到 GitHub 指南

## 📋 当前状态

- **远程仓库**: https://github.com/JasonW-Bit/getBook.git
- **当前分支**: main
- **待推送提交**: 多个新提交（包括 Agent 状态管理系统）

## 🚀 推送方法

### 方法 1: 使用 GitHub CLI（最简单，推荐）

```bash
# 1. 安装 GitHub CLI（如果未安装）
# macOS: brew install gh
# 其他系统: https://cli.github.com/

# 2. 登录 GitHub
gh auth login

# 3. 推送代码
git push -u origin main
```

### 方法 2: 使用 Personal Access Token

```bash
# 1. 在 GitHub 创建 Personal Access Token
#   访问: https://github.com/settings/tokens
#   点击 "Generate new token (classic)"
#   选择权限: repo (全部权限)
#   复制生成的 token

# 2. 推送时使用 token 作为密码
git push -u origin main
# 用户名: 你的 GitHub 用户名
# 密码: 粘贴你的 Personal Access Token
```

### 方法 3: 使用 SSH（最安全，推荐长期使用）

```bash
# 1. 生成 SSH 密钥（如果还没有）
ssh-keygen -t ed25519 -C "your_email@example.com"
# 按 Enter 使用默认路径
# 设置密码（可选，但推荐）

# 2. 复制公钥
cat ~/.ssh/id_ed25519.pub
# 或 macOS: pbcopy < ~/.ssh/id_ed25519.pub

# 3. 添加到 GitHub
#   访问: https://github.com/settings/keys
#   点击 "New SSH key"
#   粘贴公钥内容

# 4. 切换远程仓库到 SSH
git remote set-url origin git@github.com:JasonW-Bit/getBook.git

# 5. 测试连接
ssh -T git@github.com

# 6. 推送
git push -u origin main
```

### 方法 4: 使用 Git Credential Manager（macOS）

```bash
# macOS 会自动使用 Keychain 保存凭据
git push -u origin main
# 第一次会提示输入用户名和密码（或 token）
# 之后会自动保存
```

## 📝 待推送的内容

包括以下新功能：
- ✅ Agent 状态管理系统
- ✅ 对话历史保存
- ✅ 工作流状态管理
- ✅ 恢复脚本
- ✅ 完整文档
- ✅ 使用示例

## ⚠️ 注意事项

1. **测试文件已排除**: `data/agent_state/test_*/` 已在 `.gitignore` 中排除
2. **敏感信息**: `agent_config.json` 不会被提交（包含 API 密钥）
3. **大文件**: 模型文件（.h5）已排除，不会上传

## 🔍 验证推送

推送成功后，访问以下链接查看：
https://github.com/JasonW-Bit/getBook

## 🐛 常见问题

### 问题: Permission denied

**解决方案**: 使用 Personal Access Token 或配置 SSH 密钥

### 问题: 需要合并远程更改

```bash
# 先拉取远程更改
git pull origin main --rebase

# 解决冲突后推送
git push -u origin main
```

### 问题: 大文件推送失败

```bash
# 检查是否有大文件
git ls-files | xargs ls -lh | sort -k5 -hr | head -10

# 如果模型文件被意外添加，从 Git 中移除
git rm --cached models/text_rewriter_model/*.h5
git commit -m "Remove large model files"
```

## ✅ 推送后

推送成功后，你可以：
1. 在新电脑上克隆项目: `git clone https://github.com/JasonW-Bit/getBook.git`
2. 恢复 Agent 状态: `python3 scripts/restore_agent.py`
3. 继续工作！

