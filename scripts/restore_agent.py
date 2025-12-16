#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent 恢复脚本
在新环境中恢复 Agent 状态和对话历史
"""

import os
import sys
import json
from pathlib import Path

# 添加项目路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from scripts.core.agent_state_manager import AgentStateManager
from scripts.core.agent_session import AgentSession


def restore_agent_state(export_file: str = None, state_dir: str = "data/agent_state"):
    """
    恢复 Agent 状态
    
    Args:
        export_file: 导出的状态文件路径（如果从其他电脑导入）
        state_dir: 状态目录
    """
    print("="*60)
    print("🔄 Agent 状态恢复")
    print("="*60)
    
    # 如果提供了导出文件，先导入
    if export_file and os.path.exists(export_file):
        print(f"\n📥 从文件导入状态: {export_file}")
        manager = AgentStateManager(state_dir=state_dir)
        manager.import_state(export_file)
        print("✅ 状态导入完成")
    elif export_file:
        print(f"⚠️  导出文件不存在: {export_file}")
        print("   将使用本地保存的状态")
    
    # 加载状态
    manager = AgentStateManager(state_dir=state_dir)
    
    # 显示恢复的状态
    print("\n📊 恢复的状态:")
    print(f"   - 对话记录: {len(manager.conversation_history)} 条")
    print(f"   - Agent 配置: {len(manager.agent_config)} 项")
    print(f"   - 工作流状态: {len(manager.workflow_state.get('completed_steps', []))} 步")
    
    # 显示最近的对话
    if manager.conversation_history:
        print("\n💬 最近的对话记录:")
        recent = manager.conversation_history[-5:]
        for i, msg in enumerate(recent, 1):
            role_icon = "👤" if msg.get("role") == "user" else "🤖"
            content_preview = msg.get("content", "")[:100]
            if len(msg.get("content", "")) > 100:
                content_preview += "..."
            print(f"   {i}. {role_icon} [{msg.get('role', 'unknown')}]: {content_preview}")
    
    # 显示工作流进度
    if manager.workflow_state.get("completed_steps"):
        print("\n🔄 工作流进度:")
        for step in manager.workflow_state["completed_steps"][-5:]:
            status_icon = "✅" if step.get("status") == "completed" else "⏳"
            print(f"   {status_icon} {step.get('step', 'unknown')}")
    
    # 创建会话实例
    session = AgentSession(state_dir=state_dir)
    session.print_session_info()
    
    print("\n✅ Agent 状态恢复完成！")
    print("   你现在可以继续之前的工作了。")
    print("="*60)
    
    return manager, session


def check_environment():
    """检查环境是否就绪"""
    print("\n🔍 检查环境...")
    
    issues = []
    
    # 检查 Python 版本
    if sys.version_info < (3, 7):
        issues.append("Python 版本需要 3.7+")
    
    # 检查必要的目录
    required_dirs = [
        "scripts",
        "data/config",
        "data/agent_state"
    ]
    
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            issues.append(f"缺少目录: {dir_path}")
            os.makedirs(dir_path, exist_ok=True)
            print(f"   ✅ 已创建: {dir_path}")
    
    # 检查配置文件
    config_files = [
        "data/config/personality_keywords.json",
        "data/config/emotion_keywords.json"
    ]
    
    for config_file in config_files:
        if not os.path.exists(config_file):
            issues.append(f"缺少配置文件: {config_file}")
    
    if issues:
        print("⚠️  发现以下问题:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("✅ 环境检查通过")
    
    return len(issues) == 0


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="恢复 Agent 状态")
    parser.add_argument("--import", dest="import_file", type=str, 
                       help="从导出文件导入状态")
    parser.add_argument("--state-dir", type=str, default="data/agent_state",
                       help="状态目录")
    parser.add_argument("--check-env", action="store_true",
                       help="检查环境")
    
    args = parser.parse_args()
    
    # 检查环境
    if args.check_env:
        check_environment()
        return
    
    # 恢复状态
    try:
        manager, session = restore_agent_state(
            export_file=args.import_file,
            state_dir=args.state_dir
        )
        
        # 交互式提示
        print("\n💡 提示:")
        print("   - 使用 AgentSession 继续工作")
        print("   - 对话会自动保存")
        print("   - 使用 export_session() 导出状态")
        
    except Exception as e:
        print(f"\n❌ 恢复失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

