#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于深度学习的AI内容生成器
使用深度学习模型生成新内容，保持逻辑一致性
"""

import os
import sys
from typing import Dict, List, Optional, Tuple

# 导入AI模块
try:
    from ...ai.integration import UnifiedRewriter, CreativeAIEngine
    from ...ai.context_manager import NovelContextManager
    from ...ai.consistency_checker import ConsistencyChecker
except ImportError:
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'ai'))
        from integration import UnifiedRewriter, CreativeAIEngine
        from context_manager import NovelContextManager
        from consistency_checker import ConsistencyChecker
    except ImportError:
        UnifiedRewriter = None
        CreativeAIEngine = None
        NovelContextManager = None
        ConsistencyChecker = None


class AIContentGenerator:
    """基于AI的内容生成器"""
    
    def __init__(self, 
                 ai_type: str = "tensorflow",
                 ai_model_path: Optional[str] = None):
        """
        初始化AI内容生成器
        
        Args:
            ai_type: AI类型
            ai_model_path: 模型路径
        """
        self.ai_type = ai_type
        self.ai_model_path = ai_model_path
        
        # 初始化AI引擎
        if CreativeAIEngine:
            try:
                self.engine = CreativeAIEngine(
                    ai_type=ai_type,
                    ai_model_path=ai_model_path
                )
            except Exception as e:
                print(f"⚠️  无法初始化AI引擎: {e}")
                self.engine = None
        else:
            self.engine = None
        
        # 初始化上下文管理器
        if NovelContextManager:
            self.context_manager = NovelContextManager()
        else:
            self.context_manager = None
        
        # 初始化一致性检查器
        if ConsistencyChecker:
            self.consistency_checker = ConsistencyChecker()
        else:
            self.consistency_checker = None
    
    def generate_new_chapter(self,
                            previous_chapters: List[str],
                            chapter_num: int,
                            title: Optional[str] = None,
                            style: str = "延续",
                            maintain_consistency: bool = True) -> Dict:
        """
        生成新章节（基于深度学习，保持逻辑一致性）
        
        Args:
            previous_chapters: 之前的章节列表
            chapter_num: 章节号
            title: 章节标题
            style: 生成风格
            maintain_consistency: 是否保持逻辑一致性
        
        Returns:
            生成的章节字典
        """
        if not self.engine:
            print("⚠️  AI引擎不可用，无法生成内容")
            return {'num': chapter_num, 'title': title or f"第{chapter_num}章", 'content': ''}
        
        print(f"🤖 使用AI生成第{chapter_num}章...")
        
        # 构建上下文
        full_context = '\n\n'.join(previous_chapters[-3:]) if previous_chapters else ""  # 使用最近3章作为上下文
        
        # 如果启用一致性检查，分析已有内容
        if maintain_consistency and self.context_manager and previous_chapters:
            try:
                novel_context = self.context_manager.build_context(
                    '\n\n'.join(previous_chapters),
                    previous_chapters
                )
            except Exception as e:
                print(f"⚠️  上下文构建失败: {e}")
                novel_context = None
        else:
            novel_context = None
        
        # 生成章节开头（基于前文）
        if full_context:
            # 使用前文的结尾作为提示
            last_paragraphs = full_context.split('\n\n')[-3:]
            prompt = '\n\n'.join(last_paragraphs)
            
            # 使用AI继续生成
            try:
                if self.engine.rewriter:
                    # 生成延续内容
                    generated_content = self.engine.rewriter.rewrite(
                        text=prompt,
                        style=style,
                        context=full_context[:2000],  # 限制上下文长度
                        use_ai=True,
                        novel_context=novel_context,
                        chapter_num=chapter_num
                    )
                    
                    # 如果生成的内容太短，继续生成
                    if len(generated_content) < 500:
                        # 基于生成的内容继续
                        continuation = self.engine.rewriter.rewrite(
                            text=generated_content[-200:],
                            style=style,
                            context=generated_content,
                            use_ai=True,
                            novel_context=novel_context,
                            chapter_num=chapter_num
                        )
                        generated_content += "\n\n" + continuation
                    
                    # 检查一致性
                    if maintain_consistency and self.consistency_checker and previous_chapters:
                        is_consistent, issues = self.consistency_checker.check_consistency(
                            previous_chapters[-1] if previous_chapters else "",
                            generated_content,
                            novel_context
                        )
                        if not is_consistent:
                            print(f"⚠️  生成的内容存在逻辑问题: {', '.join(issues[:3])}")
                            # 可以在这里进行修复或重新生成
                    
                    return {
                        'num': chapter_num,
                        'title': title or f"第{chapter_num}章",
                        'content': generated_content,
                        'consistent': is_consistent if maintain_consistency else True,
                        'issues': issues if maintain_consistency and not is_consistent else []
                    }
            except Exception as e:
                print(f"⚠️  AI生成失败: {e}")
                import traceback
                traceback.print_exc()
        
        # 降级到简单生成
        return {
            'num': chapter_num,
            'title': title or f"第{chapter_num}章",
            'content': f"第{chapter_num}章内容（AI生成失败，使用模板）",
            'consistent': True,
            'issues': []
        }
    
    def expand_content(self,
                      original_content: str,
                      expansion_type: str = "细节",
                      context: Optional[str] = None,
                      maintain_consistency: bool = True) -> str:
        """
        扩展内容（基于深度学习）
        
        Args:
            original_content: 原始内容
            expansion_type: 扩展类型（细节/对话/描写/情节）
            context: 上下文信息
            maintain_consistency: 是否保持逻辑一致性
        
        Returns:
            扩展后的内容
        """
        if not self.engine or not self.engine.rewriter:
            return original_content
        
        print(f"🤖 使用AI扩展内容（类型: {expansion_type}）...")
        
        try:
            # 根据扩展类型选择不同的提示
            expansion_prompts = {
                '细节': '请为以下内容添加更多细节描写，包括环境、心理活动等：',
                '对话': '请为以下内容添加角色之间的对话：',
                '描写': '请为以下内容添加更丰富的场景和人物描写：',
                '情节': '请为以下内容添加新的情节发展：',
            }
            
            prompt = expansion_prompts.get(expansion_type, '请扩展以下内容：')
            
            # 构建完整的提示
            full_prompt = f"{prompt}\n\n{original_content}"
            if context:
                full_prompt = f"{context}\n\n{full_prompt}"
            
            # 使用AI扩展
            expanded = self.engine.rewriter.rewrite(
                text=original_content,
                style="延续",  # 保持原有风格
                context=full_prompt,
                use_ai=True
            )
            
            # 检查一致性
            if maintain_consistency and self.consistency_checker:
                is_consistent, issues = self.consistency_checker.check_consistency(
                    original_content,
                    expanded
                )
                if not is_consistent:
                    print(f"⚠️  扩展内容存在逻辑问题: {', '.join(issues[:3])}")
            
            return expanded if expanded else original_content
            
        except Exception as e:
            print(f"⚠️  AI扩展失败: {e}")
            return original_content
    
    def continue_story(self,
                      current_content: str,
                      direction: str = "自然发展",
                      length: int = 1000,
                      maintain_consistency: bool = True) -> str:
        """
        继续故事（基于深度学习）
        
        Args:
            current_content: 当前内容
            direction: 发展方向（自然发展/转折/高潮/结尾）
            length: 生成长度
            maintain_consistency: 是否保持逻辑一致性
        
        Returns:
            继续的内容
        """
        if not self.engine or not self.engine.rewriter:
            return ""
        
        print(f"🤖 使用AI继续故事（方向: {direction}）...")
        
        try:
            # 根据方向选择提示
            direction_prompts = {
                '自然发展': '请自然地继续以下故事：',
                '转折': '请为以下故事添加一个转折：',
                '高潮': '请为以下故事发展高潮：',
                '结尾': '请为以下故事写一个结尾：',
            }
            
            prompt = direction_prompts.get(direction, '请继续以下故事：')
            full_prompt = f"{prompt}\n\n{current_content[-500:]}"  # 使用最后500字符作为上下文
            
            # 生成内容
            generated = ""
            current_text = current_content[-200:]  # 从最后200字符开始
            
            while len(generated) < length:
                chunk = self.engine.rewriter.rewrite(
                    text=current_text,
                    style="延续",
                    context=full_prompt,
                    use_ai=True
                )
                
                if not chunk or chunk == current_text:
                    break
                
                generated += chunk
                current_text = chunk[-200:]  # 更新当前文本
                
                if len(generated) >= length:
                    break
            
            # 检查一致性
            if maintain_consistency and self.consistency_checker:
                is_consistent, issues = self.consistency_checker.check_consistency(
                    current_content,
                    generated
                )
                if not is_consistent:
                    print(f"⚠️  生成内容存在逻辑问题: {', '.join(issues[:3])}")
            
            return generated[:length]  # 限制长度
            
        except Exception as e:
            print(f"⚠️  AI继续故事失败: {e}")
            return ""

