#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent 会话管理器
集成 Agent 状态管理，自动保存对话和工作状态
"""

import os
import sys
from typing import Optional, Dict, Any
from .agent_state_manager import AgentStateManager


class AgentSession:
    """Agent 会话管理器"""
    
    def __init__(self, session_name: Optional[str] = None, state_dir: str = "data/agent_state"):
        """
        初始化会话
        
        Args:
            session_name: 会话名称（用于区分不同会话）
            state_dir: 状态保存目录
        """
        self.session_name = session_name or "default"
        self.state_manager = AgentStateManager(
            state_dir=os.path.join(state_dir, self.session_name)
        )
        
        # 当前会话状态
        self.current_task: Optional[str] = None
        self.working_files: list = []
        self.project_context: Dict = {}
        
        # 加载会话上下文
        if "context" in self.state_manager.context:
            self.project_context = self.state_manager.context.get("project_context", {})
            self.current_task = self.state_manager.context.get("current_task")
            self.working_files = self.state_manager.context.get("working_files", [])
    
    def start_task(self, task_description: str, metadata: Optional[Dict] = None):
        """开始新任务"""
        self.current_task = task_description
        self._save_context()
        
        # 记录任务开始
        self.state_manager.save_conversation(
            role="system",
            content=f"开始任务: {task_description}",
            metadata=metadata or {}
        )
        print(f"🚀 任务开始: {task_description}")
    
    def add_user_message(self, message: str, metadata: Optional[Dict] = None):
        """添加用户消息"""
        self.state_manager.save_conversation(
            role="user",
            content=message,
            metadata=metadata or {}
        )
    
    def add_assistant_message(self, message: str, metadata: Optional[Dict] = None):
        """添加助手消息"""
        self.state_manager.save_conversation(
            role="assistant",
            content=message,
            metadata=metadata or {}
        )
    
    def update_working_files(self, files: list):
        """更新正在处理的文件列表"""
        self.working_files = files
        self._save_context()
    
    def update_project_context(self, context: Dict):
        """更新项目上下文"""
        self.project_context.update(context)
        self._save_context()
    
    def save_workflow_progress(self, step: str, status: str, details: Optional[Dict] = None):
        """保存工作流进度"""
        workflow_state = self.state_manager.workflow_state.copy()
        
        if "completed_steps" not in workflow_state:
            workflow_state["completed_steps"] = []
        
        if "current_step" not in workflow_state:
            workflow_state["current_step"] = step
        
        if step not in [s.get("step") for s in workflow_state["completed_steps"]]:
            workflow_state["completed_steps"].append({
                "step": step,
                "status": status,
                "timestamp": self.state_manager.context.get("last_updated", ""),
                "details": details or {}
            })
        
        workflow_state["current_step"] = step
        self.state_manager.save_workflow_state(workflow_state)
    
    def _save_context(self):
        """保存当前上下文"""
        context = {
            "current_task": self.current_task,
            "working_files": self.working_files,
            "project_context": self.project_context,
            "session_name": self.session_name
        }
        self.state_manager.save_context(context)
    
    def export_session(self, export_path: Optional[str] = None) -> str:
        """导出会话（用于迁移到其他电脑）"""
        if export_path is None:
            export_path = f"data/agent_state/{self.session_name}_export.json"
        
        return self.state_manager.export_state(export_path)
    
    def get_session_info(self) -> Dict:
        """获取会话信息"""
        summary = self.state_manager.get_conversation_summary()
        return {
            "session_name": self.session_name,
            "current_task": self.current_task,
            "working_files": self.working_files,
            "conversation_summary": summary,
            "workflow_progress": len(self.state_manager.workflow_state.get("completed_steps", []))
        }
    
    def print_session_info(self):
        """打印会话信息"""
        info = self.get_session_info()
        print("\n" + "="*60)
        print(f"📋 会话信息: {info['session_name']}")
        print("="*60)
        print(f"当前任务: {info['current_task'] or '无'}")
        print(f"工作文件: {len(info['working_files'])} 个")
        print(f"对话记录: {info['conversation_summary']['total_messages']} 条")
        print(f"工作流进度: {info['workflow_progress']} 步")
        print("="*60 + "\n")


# 全局会话实例（可选）
_global_session: Optional[AgentSession] = None


def get_session(session_name: Optional[str] = None) -> AgentSession:
    """获取全局会话实例"""
    global _global_session
    if _global_session is None:
        _global_session = AgentSession(session_name=session_name)
    return _global_session


def save_conversation(role: str, content: str, metadata: Optional[Dict] = None):
    """快速保存对话（使用全局会话）"""
    session = get_session()
    if role == "user":
        session.add_user_message(content, metadata)
    elif role == "assistant":
        session.add_assistant_message(content, metadata)


if __name__ == "__main__":
    # 示例用法
    session = AgentSession(session_name="test_session")
    
    session.start_task("测试任务", {"test": True})
    session.add_user_message("你好，这是一个测试")
    session.add_assistant_message("收到，开始处理")
    session.update_working_files(["test.py", "test2.py"])
    
    session.print_session_info()
    
    export_path = session.export_session()
    print(f"会话已导出到: {export_path}")

