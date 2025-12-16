#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent 状态管理使用示例
演示如何保存和恢复 Agent 状态
"""

import os
import sys

# 添加项目路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from scripts.core.agent_session import AgentSession, save_conversation


def example_basic_usage():
    """基本使用示例"""
    print("="*60)
    print("示例 1: 基本使用")
    print("="*60)
    
    # 创建会话
    session = AgentSession(session_name="example_session")
    
    # 开始任务
    session.start_task("示例任务：代码优化", {
        "project": "getBook",
        "priority": "high"
    })
    
    # 记录对话
    session.add_user_message("请检查代码结构")
    session.add_assistant_message("正在检查代码结构...")
    session.add_user_message("优化 pipeline.py")
    session.add_assistant_message("已完成优化")
    
    # 更新工作文件
    session.update_working_files([
        "scripts/core/pipeline.py",
        "scripts/core/training_data_generator.py"
    ])
    
    # 保存工作流进度
    session.save_workflow_progress("代码检查", "completed", {
        "files_checked": 5,
        "issues_found": 2
    })
    session.save_workflow_progress("代码优化", "completed", {
        "files_optimized": 3
    })
    
    # 显示会话信息
    session.print_session_info()
    
    # 导出状态
    export_path = session.export_session()
    print(f"\n✅ 状态已导出到: {export_path}")


def example_quick_save():
    """快速保存示例"""
    print("\n" + "="*60)
    print("示例 2: 快速保存对话")
    print("="*60)
    
    # 使用全局函数快速保存
    save_conversation("user", "快速保存用户消息")
    save_conversation("assistant", "快速保存助手回复")
    
    # 获取会话查看
    session = AgentSession()
    session.print_session_info()


def example_restore():
    """恢复示例"""
    print("\n" + "="*60)
    print("示例 3: 恢复状态")
    print("="*60)
    
    # 创建新会话（会自动加载已有状态）
    session = AgentSession(session_name="example_session")
    
    # 查看恢复的状态
    session.print_session_info()
    
    # 继续工作
    session.add_user_message("继续之前的工作")
    session.add_assistant_message("好的，继续处理")
    
    print("✅ 状态已恢复，可以继续工作")


def example_multiple_sessions():
    """多会话示例"""
    print("\n" + "="*60)
    print("示例 4: 多会话管理")
    print("="*60)
    
    # 创建多个会话
    work_session = AgentSession(session_name="work_project")
    personal_session = AgentSession(session_name="personal_project")
    
    # 分别记录
    work_session.start_task("工作项目任务")
    work_session.add_user_message("处理工作相关任务")
    
    personal_session.start_task("个人项目任务")
    personal_session.add_user_message("处理个人相关任务")
    
    # 查看各自的状态
    print("\n工作会话:")
    work_session.print_session_info()
    
    print("\n个人会话:")
    personal_session.print_session_info()


def main():
    """运行所有示例"""
    print("\n🚀 Agent 状态管理使用示例\n")
    
    try:
        example_basic_usage()
        example_quick_save()
        example_restore()
        example_multiple_sessions()
        
        print("\n" + "="*60)
        print("✅ 所有示例运行完成")
        print("="*60)
        print("\n💡 提示:")
        print("   - 状态文件保存在: data/agent_state/")
        print("   - 使用 restore_agent.py 在新环境恢复")
        print("   - 查看 docs/AGENT_STATE_MANAGEMENT.md 获取详细文档")
        
    except Exception as e:
        print(f"\n❌ 示例运行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

