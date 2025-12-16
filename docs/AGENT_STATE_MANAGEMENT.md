# Agent 状态管理指南

## 📋 概述

Agent 状态管理系统允许你保存完整的对话历史、工作状态和配置，并在另一台电脑上恢复，实现无缝继续工作。

## 🎯 功能特性

- ✅ **对话历史保存**：自动保存所有用户和助手的对话
- ✅ **工作流状态**：记录工作进度和已完成步骤
- ✅ **上下文管理**：保存项目上下文和当前任务信息
- ✅ **配置管理**：保存 Agent 配置和偏好设置
- ✅ **导出/导入**：支持将状态导出为单个文件，便于迁移

## 🚀 快速开始

### 1. 在当前电脑上保存状态

#### 方法一：自动保存（推荐）

在代码中使用 `AgentSession`，对话会自动保存：

```python
from scripts.core.agent_session import AgentSession

# 创建会话
session = AgentSession(session_name="my_work")

# 开始任务
session.start_task("优化代码结构")

# 添加对话（会自动保存）
session.add_user_message("检查一下当前工程")
session.add_assistant_message("正在检查...")

# 更新工作文件
session.update_working_files(["pipeline.py", "train_model.py"])

# 保存工作流进度
session.save_workflow_progress("代码检查", "completed", {"files_checked": 10})
```

#### 方法二：手动保存

```python
from scripts.core.agent_state_manager import AgentStateManager

manager = AgentStateManager()

# 保存对话
manager.save_conversation("user", "你好")
manager.save_conversation("assistant", "收到")

# 保存配置
manager.save_agent_config({
    "model_type": "huggingface",
    "model_path": "models/pretrained/Qwen",
    "preferences": {"language": "zh"}
})

# 保存上下文
manager.save_context({
    "current_task": "训练模型",
    "working_files": ["train_model.py"]
})
```

### 2. 导出状态（用于迁移到其他电脑）

```bash
# 使用命令行工具导出
python3 scripts/core/agent_state_manager.py --export data/agent_state/export.json

# 或在代码中导出
session = AgentSession()
export_path = session.export_session("data/agent_state/my_work_export.json")
print(f"状态已导出到: {export_path}")
```

### 3. 在新电脑上恢复状态

#### 步骤 1：克隆项目

```bash
git clone https://github.com/YOUR_USERNAME/getBook.git
cd getBook
```

#### 步骤 2：安装依赖

```bash
pip install -r requirements.txt
pip install -r requirements_models.txt
```

#### 步骤 3：恢复 Agent 状态

**方法一：从导出文件恢复**

```bash
# 将导出文件复制到新电脑
# 然后运行恢复脚本
python3 scripts/restore_agent.py --import data/agent_state/export.json
```

**方法二：如果状态已提交到 Git**

```bash
# 状态文件在 data/agent_state/ 目录中
# 直接运行恢复脚本
python3 scripts/restore_agent.py
```

#### 步骤 4：继续工作

```python
from scripts.core.agent_session import AgentSession

# 加载会话（会自动恢复之前的状态）
session = AgentSession(session_name="my_work")

# 查看会话信息
session.print_session_info()

# 继续工作，对话会自动保存
session.add_user_message("继续之前的工作")
```

## 📁 文件结构

```
data/agent_state/
├── default/                    # 默认会话
│   ├── conversation_history.json  # 对话历史
│   ├── agent_config.json         # Agent 配置
│   ├── context.pkl               # 上下文（二进制）
│   └── workflow_state.json       # 工作流状态
├── my_work/                     # 命名会话
│   └── ...
└── export.json                   # 导出的状态文件
```

## 🔧 高级用法

### 创建多个会话

```python
# 为不同项目创建不同会话
work_session = AgentSession(session_name="work_project")
personal_session = AgentSession(session_name="personal_project")

# 每个会话独立保存状态
work_session.start_task("工作项目")
personal_session.start_task("个人项目")
```

### 查看状态摘要

```bash
python3 scripts/core/agent_state_manager.py --summary
```

### 清空状态

```bash
python3 scripts/core/agent_state_manager.py --clear
```

### 在代码中集成

```python
from scripts.core.agent_session import get_session, save_conversation

# 使用全局会话
session = get_session()

# 快速保存对话
save_conversation("user", "用户消息")
save_conversation("assistant", "助手回复")
```

## 📤 导出到 GitHub

### 1. 更新 .gitignore

确保 `data/agent_state/` 目录被正确管理：

```gitignore
# Agent 状态（可选：是否提交到 Git）
# 如果包含敏感信息，不要提交
# data/agent_state/*/agent_config.json  # 包含 API 密钥
data/agent_state/*/context.pkl          # 二进制文件，通常不提交
data/agent_state/*/conversation_history.json  # 可以提交（不含敏感信息）
```

### 2. 提交状态文件

```bash
# 只提交对话历史（不含敏感信息）
git add data/agent_state/*/conversation_history.json
git add data/agent_state/*/workflow_state.json

# 提交
git commit -m "Add agent conversation history"
git push
```

### 3. 在新电脑上恢复

```bash
git pull
python3 scripts/restore_agent.py
```

## ⚠️ 注意事项

1. **敏感信息**：
   - `agent_config.json` 可能包含 API 密钥
   - 不要将包含敏感信息的配置文件提交到 Git
   - 使用环境变量或加密存储敏感信息

2. **文件大小**：
   - 对话历史可能很大
   - 定期清理旧对话或使用压缩

3. **兼容性**：
   - 确保新电脑的 Python 版本兼容
   - 检查依赖包是否已安装

4. **备份**：
   - 定期导出状态文件作为备份
   - 重要工作前先备份状态

## 🔄 工作流程示例

### 完整的工作流程

```python
from scripts.core.agent_session import AgentSession

# 1. 创建会话
session = AgentSession(session_name="project_optimization")

# 2. 开始任务
session.start_task("优化项目结构", {"priority": "high"})

# 3. 记录对话
session.add_user_message("检查代码结构")
session.add_assistant_message("正在分析...")

# 4. 更新工作文件
session.update_working_files(["pipeline.py", "train_model.py"])

# 5. 保存进度
session.save_workflow_progress("代码分析", "completed")
session.save_workflow_progress("结构优化", "in_progress")

# 6. 导出状态（用于迁移）
export_path = session.export_session()

# 7. 在新电脑上恢复
# python3 scripts/restore_agent.py --import export_path
```

## 🐛 故障排除

### 问题：状态文件损坏

```bash
# 从备份恢复
python3 scripts/restore_agent.py --import backup/export.json
```

### 问题：导入失败

- 检查文件路径是否正确
- 确保 JSON 格式正确
- 检查文件权限

### 问题：上下文无法恢复

- `context.pkl` 包含 Python 对象，需要相同的 Python 版本
- 如果失败，会使用 JSON 格式的简化上下文

## 📚 相关文档

- [项目结构](PROJECT_STRUCTURE.md)
- [快速开始](QUICK_START.md)
- [GitHub 上传指南](../GITHUB_UPLOAD.md)

## 💡 最佳实践

1. **定期导出**：重要工作节点导出状态
2. **命名会话**：为不同项目使用不同会话名
3. **清理旧数据**：定期清理不需要的对话历史
4. **版本控制**：将对话历史纳入版本控制（不含敏感信息）
5. **环境检查**：在新环境先运行 `--check-env`

