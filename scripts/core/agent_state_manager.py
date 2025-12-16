#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent 状态管理器
保存和恢复 Agent 的完整状态，包括对话历史、配置、上下文等
"""

import os
import json
import pickle
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class AgentStateManager:
    """Agent 状态管理器"""
    
    def __init__(self, state_dir: str = "data/agent_state"):
        """
        初始化状态管理器
        
        Args:
            state_dir: 状态保存目录
        """
        self.state_dir = state_dir
        os.makedirs(state_dir, exist_ok=True)
        
        # 状态文件路径
        self.conversation_file = os.path.join(state_dir, "conversation_history.json")
        self.agent_config_file = os.path.join(state_dir, "agent_config.json")
        self.context_file = os.path.join(state_dir, "context.pkl")
        self.workflow_state_file = os.path.join(state_dir, "workflow_state.json")
        
        # 状态数据
        self.conversation_history: List[Dict] = []
        self.agent_config: Dict = {}
        self.context: Dict = {}
        self.workflow_state: Dict = {}
        
        # 加载已有状态
        self.load_all()
    
    def save_conversation(self, role: str, content: str, metadata: Optional[Dict] = None):
        """
        保存对话记录
        
        Args:
            role: 角色 ('user' 或 'assistant')
            content: 对话内容
            metadata: 元数据（时间戳、文件路径等）
        """
        entry = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.conversation_history.append(entry)
        
        # 保存到文件
        self._save_json(self.conversation_file, self.conversation_history)
        print(f"💬 已保存对话记录 ({role})")
    
    def save_agent_config(self, config: Dict):
        """
        保存 Agent 配置
        
        Args:
            config: 配置字典，包含：
                - model_type: 使用的模型类型
                - model_path: 模型路径
                - api_keys: API 密钥（加密存储）
                - preferences: 用户偏好设置
                - system_prompt: 系统提示词
        """
        self.agent_config = config.copy()
        self.agent_config["last_updated"] = datetime.now().isoformat()
        
        # 敏感信息加密（简单示例，实际应使用更安全的加密方法）
        if "api_keys" in self.agent_config:
            # 这里可以添加加密逻辑
            pass
        
        self._save_json(self.agent_config_file, self.agent_config)
        print("⚙️  已保存 Agent 配置")
    
    def save_context(self, context: Dict):
        """
        保存上下文信息
        
        Args:
            context: 上下文字典，包含：
                - current_task: 当前任务
                - working_files: 正在处理的文件
                - project_state: 项目状态
                - analysis_results: 分析结果
        """
        self.context = context.copy()
        self.context["last_updated"] = datetime.now().isoformat()
        
        # 使用 pickle 保存复杂对象
        try:
            with open(self.context_file, 'wb') as f:
                pickle.dump(self.context, f)
            print("📦 已保存上下文信息")
        except Exception as e:
            print(f"⚠️  保存上下文失败: {e}")
    
    def save_workflow_state(self, workflow_state: Dict):
        """
        保存工作流状态
        
        Args:
            workflow_state: 工作流状态，包含：
                - current_step: 当前步骤
                - completed_steps: 已完成的步骤
                - pending_tasks: 待处理任务
                - errors: 错误记录
                - progress: 进度信息
        """
        self.workflow_state = workflow_state.copy()
        self.workflow_state["last_updated"] = datetime.now().isoformat()
        
        self._save_json(self.workflow_state_file, self.workflow_state)
        print("🔄 已保存工作流状态")
    
    def load_all(self):
        """加载所有保存的状态"""
        # 加载对话历史
        self.conversation_history = self._load_json(self.conversation_file, [])
        
        # 加载 Agent 配置
        self.agent_config = self._load_json(self.agent_config_file, {})
        
        # 加载上下文
        if os.path.exists(self.context_file):
            try:
                with open(self.context_file, 'rb') as f:
                    self.context = pickle.load(f)
            except Exception as e:
                print(f"⚠️  加载上下文失败: {e}")
                self.context = {}
        else:
            self.context = {}
        
        # 加载工作流状态
        self.workflow_state = self._load_json(self.workflow_state_file, {})
        
        print(f"📂 已加载 Agent 状态:")
        print(f"   - 对话记录: {len(self.conversation_history)} 条")
        print(f"   - 配置项: {len(self.agent_config)} 个")
        print(f"   - 上下文键: {len(self.context)} 个")
        print(f"   - 工作流步骤: {len(self.workflow_state.get('completed_steps', []))} 个")
    
    def export_state(self, export_path: str) -> str:
        """
        导出完整状态到单个文件（用于备份或迁移）
        
        Args:
            export_path: 导出文件路径
            
        Returns:
            导出文件路径
        """
        export_data = {
            "export_time": datetime.now().isoformat(),
            "version": "1.0",
            "conversation_history": self.conversation_history,
            "agent_config": self.agent_config,
            "workflow_state": self.workflow_state,
            # 注意：context 中的复杂对象可能需要特殊处理
        }
        
        # 如果 context 包含可序列化的数据，也导出
        try:
            export_data["context"] = self._serialize_context(self.context)
        except:
            export_data["context"] = {}
            print("⚠️  上下文包含不可序列化对象，已跳过")
        
        self._save_json(export_path, export_data)
        print(f"✅ 状态已导出到: {export_path}")
        return export_path
    
    def import_state(self, import_path: str):
        """
        从导出文件导入状态
        
        Args:
            import_path: 导入文件路径
        """
        if not os.path.exists(import_path):
            raise FileNotFoundError(f"导入文件不存在: {import_path}")
        
        import_data = self._load_json(import_path, {})
        
        if "conversation_history" in import_data:
            self.conversation_history = import_data["conversation_history"]
            self._save_json(self.conversation_file, self.conversation_history)
        
        if "agent_config" in import_data:
            self.agent_config = import_data["agent_config"]
            self._save_json(self.agent_config_file, self.agent_config)
        
        if "workflow_state" in import_data:
            self.workflow_state = import_data["workflow_state"]
            self._save_json(self.workflow_state_file, self.workflow_state)
        
        if "context" in import_data:
            self.context = import_data["context"]
            try:
                with open(self.context_file, 'wb') as f:
                    pickle.dump(self.context, f)
            except Exception as e:
                print(f"⚠️  导入上下文失败: {e}")
        
        print(f"✅ 状态已从 {import_path} 导入")
    
    def get_conversation_summary(self) -> Dict:
        """获取对话摘要"""
        return {
            "total_messages": len(self.conversation_history),
            "user_messages": sum(1 for msg in self.conversation_history if msg.get("role") == "user"),
            "assistant_messages": sum(1 for msg in self.conversation_history if msg.get("role") == "assistant"),
            "first_message_time": self.conversation_history[0]["timestamp"] if self.conversation_history else None,
            "last_message_time": self.conversation_history[-1]["timestamp"] if self.conversation_history else None,
        }
    
    def clear_state(self, confirm: bool = False):
        """清空所有状态（谨慎使用）"""
        if not confirm:
            print("⚠️  请确认是否清空所有状态（这不可恢复）")
            return
        
        self.conversation_history = []
        self.agent_config = {}
        self.context = {}
        self.workflow_state = {}
        
        # 删除文件
        for file_path in [self.conversation_file, self.agent_config_file, 
                         self.context_file, self.workflow_state_file]:
            if os.path.exists(file_path):
                os.remove(file_path)
        
        print("🗑️  所有状态已清空")
    
    def _save_json(self, file_path: str, data: Any):
        """保存 JSON 文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️  保存文件失败 {file_path}: {e}")
    
    def _load_json(self, file_path: str, default: Any) -> Any:
        """加载 JSON 文件"""
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  加载文件失败 {file_path}: {e}")
                return default
        return default
    
    def _serialize_context(self, context: Dict) -> Dict:
        """序列化上下文（将复杂对象转换为可序列化的格式）"""
        serialized = {}
        for key, value in context.items():
            try:
                # 尝试 JSON 序列化
                json.dumps(value)
                serialized[key] = value
            except (TypeError, ValueError):
                # 如果无法序列化，转换为字符串
                serialized[key] = str(value)
        return serialized


def main():
    """命令行工具"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Agent 状态管理器")
    parser.add_argument("--export", type=str, help="导出状态到文件")
    parser.add_argument("--import", dest="import_file", type=str, help="从文件导入状态")
    parser.add_argument("--summary", action="store_true", help="显示状态摘要")
    parser.add_argument("--clear", action="store_true", help="清空所有状态")
    
    args = parser.parse_args()
    
    manager = AgentStateManager()
    
    if args.export:
        manager.export_state(args.export)
    elif args.import_file:
        manager.import_state(args.import_file)
    elif args.summary:
        summary = manager.get_conversation_summary()
        print("\n📊 Agent 状态摘要:")
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    elif args.clear:
        confirm = input("⚠️  确认清空所有状态？(yes/no): ")
        manager.clear_state(confirm.lower() == "yes")
    else:
        print("使用 --help 查看帮助信息")


if __name__ == "__main__":
    main()

