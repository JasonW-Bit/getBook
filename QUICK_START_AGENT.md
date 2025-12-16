# Agent 状态管理快速指南

## 🎯 目标

保存当前电脑上的 Agent 对话和工作状态，在另一台电脑上通过 GitHub 下载项目后继续工作。

## 📋 步骤

### 在当前电脑上

#### 1. 保存当前对话和工作状态

```python
# 方法一：使用会话管理器（推荐）
from scripts.core.agent_session import AgentSession

session = AgentSession(session_name="my_work")
session.start_task("当前任务描述")
session.add_user_message("你的问题")
session.add_assistant_message("助手的回复")

# 导出状态
export_path = session.export_session("data/agent_state/my_work_export.json")
print(f"状态已导出: {export_path}")
```

#### 2. 提交到 Git（可选）

```bash
# 只提交对话历史（不含敏感信息）
git add data/agent_state/*/conversation_history.json
git add data/agent_state/*/workflow_state.json
git commit -m "Save agent conversation history"
git push
```

### 在新电脑上

#### 1. 克隆项目

```bash
git clone https://github.com/YOUR_USERNAME/getBook.git
cd getBook
```

#### 2. 安装依赖

```bash
pip install -r requirements.txt
pip install -r requirements_models.txt
```

#### 3. 恢复 Agent 状态

**方法一：从导出文件恢复**

```bash
# 将导出文件复制到新电脑，然后：
python3 scripts/restore_agent.py --import data/agent_state/my_work_export.json
```

**方法二：从 Git 恢复（如果已提交）**

```bash
# 直接运行恢复脚本
python3 scripts/restore_agent.py
```

#### 4. 继续工作

```python
from scripts.core.agent_session import AgentSession

# 加载会话（自动恢复状态）
session = AgentSession(session_name="my_work")

# 查看恢复的状态
session.print_session_info()

# 继续对话（自动保存）
session.add_user_message("继续之前的工作")
```

## 🔧 命令行工具

### 导出状态

```bash
python3 scripts/core/agent_state_manager.py --export data/agent_state/export.json
```

### 导入状态

```bash
python3 scripts/core/agent_state_manager.py --import data/agent_state/export.json
```

### 查看状态摘要

```bash
python3 scripts/core/agent_state_manager.py --summary
```

### 运行示例

```bash
python3 scripts/example_agent_usage.py
```

## 📁 文件位置

- **状态文件**: `data/agent_state/[session_name]/`
- **导出文件**: `data/agent_state/export.json`
- **文档**: `docs/AGENT_STATE_MANAGEMENT.md`

## ⚠️ 注意事项

1. **敏感信息**: `agent_config.json` 可能包含 API 密钥，不要提交到 Git
2. **文件大小**: 对话历史可能很大，定期清理
3. **兼容性**: 确保新电脑的 Python 版本兼容

## 💡 最佳实践

1. **定期导出**: 重要工作节点导出状态
2. **命名会话**: 为不同项目使用不同会话名
3. **版本控制**: 将对话历史纳入版本控制（不含敏感信息）
4. **环境检查**: 在新环境先运行 `python3 scripts/restore_agent.py --check-env`

## 📚 详细文档

查看完整文档: [docs/AGENT_STATE_MANAGEMENT.md](docs/AGENT_STATE_MANAGEMENT.md)

