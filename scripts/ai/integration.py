#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI与创意处理模块集成
提供统一的接口，整合深度学习和改写功能
"""

from typing import Optional, Dict, List, Tuple
import os
import sys

# 导入上下文管理器和一致性检查器
try:
    from .context_manager import NovelContextManager
    from .consistency_checker import ConsistencyChecker
except ImportError:
    try:
        from scripts.ai.context_manager import NovelContextManager
        from scripts.ai.consistency_checker import ConsistencyChecker
    except ImportError:
        NovelContextManager = None
        ConsistencyChecker = None

# 添加路径以便导入
parent_dir = os.path.dirname(os.path.dirname(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# 导入AI分析器
try:
    from .analyzers.ai_analyzer import AIAnalyzerFactory
except ImportError:
    try:
        from scripts.ai.analyzers.ai_analyzer import AIAnalyzerFactory
    except ImportError:
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'analyzers'))
            from ai_analyzer import AIAnalyzerFactory
        except ImportError:
            AIAnalyzerFactory = None

# 导入传统改写器
try:
    from ..creative.processors.text_processor import NaturalStyleRewriter
except ImportError:
    try:
        from scripts.creative.processors.text_processor import NaturalStyleRewriter
    except ImportError:
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'creative', 'processors'))
            from text_processor import NaturalStyleRewriter
        except ImportError:
            NaturalStyleRewriter = None

# 导入内容生成器
try:
    from ..creative.generators.generate_content import ContentGenerator
except ImportError:
    try:
        from scripts.creative.generators.generate_content import ContentGenerator
    except ImportError:
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'creative', 'generators'))
            from generate_content import ContentGenerator
        except ImportError:
            ContentGenerator = None


class UnifiedRewriter:
    """
    统一的改写器
    整合AI分析和传统改写方法，支持逻辑一致性检查
    """
    
    def __init__(self, 
                 ai_type: str = "tensorflow",
                 ai_model_path: Optional[str] = None,
                 use_hybrid: bool = True,
                 check_consistency: bool = True):
        """
        初始化统一改写器
        
        Args:
            ai_type: AI类型 (openai/local/tensorflow/offline)
            ai_model_path: TensorFlow模型路径
            use_hybrid: 是否使用混合模式（AI + 传统方法）
            check_consistency: 是否检查逻辑一致性
        """
        self.ai_type = ai_type
        self.use_hybrid = use_hybrid
        self.check_consistency = check_consistency
        
        # 初始化上下文管理器和一致性检查器
        if NovelContextManager:
            self.context_manager = NovelContextManager()
        else:
            self.context_manager = None
        
        if ConsistencyChecker:
            self.consistency_checker = ConsistencyChecker()
        else:
            self.consistency_checker = None
        
        # 初始化AI分析器
        self.ai_analyzer = None
        if ai_type != "offline" and AIAnalyzerFactory:
            try:
                kwargs = {}
                if ai_type == "tensorflow" and ai_model_path:
                    kwargs['model_path'] = ai_model_path
                
                self.ai_analyzer = AIAnalyzerFactory.create_analyzer(
                    analyzer_type=ai_type,
                    **kwargs
                )
            except Exception as e:
                print(f"⚠️  无法初始化AI分析器: {e}")
                self.ai_analyzer = None
        
        # 初始化传统改写器
        if NaturalStyleRewriter:
            try:
                self.natural_rewriter = NaturalStyleRewriter()
            except Exception as e:
                print(f"⚠️  无法初始化传统改写器: {e}")
                self.natural_rewriter = None
        else:
            self.natural_rewriter = None
    
    def rewrite(self, 
                text: str, 
                style: str,
                perspective: Optional[str] = None,
                context: Optional[str] = None,
                use_ai: bool = True,
                novel_context: Optional[Dict] = None,
                chapter_num: int = 0) -> str:
        """
        改写文本（统一接口，支持逻辑一致性检查）
        
        Args:
            text: 原始文本
            style: 目标风格
            perspective: 视角（可选）
            context: 上下文（可选）
            use_ai: 是否使用AI
            novel_context: 整本小说的上下文信息（可选）
            chapter_num: 章节号（用于上下文管理）
        
        Returns:
            改写后的文本
        """
        if not text:
            return ""
        
        # 如果提供了小说上下文，增强上下文信息
        enhanced_context = context
        if novel_context and self.context_manager:
            try:
                novel_ctx_str = self.context_manager.get_context_for_rewrite(
                    text, chapter_num=chapter_num
                )
                if enhanced_context:
                    enhanced_context = f"{enhanced_context} | {novel_ctx_str}"
                else:
                    enhanced_context = novel_ctx_str
            except Exception as e:
                print(f"⚠️  上下文增强失败: {e}")
        
        # 如果使用AI且AI可用
        if use_ai and self.ai_analyzer:
            try:
                # 使用AI改写（传入增强的上下文）
                ai_result = self.ai_analyzer.rewrite_text(
                    text=text,
                    style=style,
                    perspective=perspective,
                    context=enhanced_context
                )
                
                # 检查逻辑一致性
                if self.check_consistency and self.consistency_checker and ai_result:
                    is_consistent, issues = self.consistency_checker.check_consistency(
                        text, ai_result, novel_context
                    )
                    if not is_consistent and len(issues) > 0:
                        print(f"⚠️  检测到逻辑一致性问题: {', '.join(issues[:3])}")
                        
                        # 尝试自动修复
                        try:
                            from .auto_fixer import AutoFixer
                            fixer = AutoFixer(context_manager=self.context_manager if hasattr(self, 'context_manager') else None)
                            fixed_result, fix_report = fixer.auto_fix(
                                text, ai_result, issues, novel_context
                            )
                            if fixed_result != ai_result:
                                print(f"✅ 自动修复完成: {', '.join(fix_report)}")
                                ai_result = fixed_result
                        except Exception as e:
                            print(f"⚠️  自动修复失败: {e}")
                            # 提供修复建议
                            try:
                                from .auto_fixer import AutoFixer
                                fixer = AutoFixer()
                                suggestions = fixer.suggest_fixes(issues, novel_context)
                                if suggestions:
                                    print(f"💡 修复建议: {suggestions[0]}")
                            except:
                                pass
                
                # 混合模式：AI改写后，再用传统方法微调
                if self.use_hybrid and self.natural_rewriter and ai_result:
                    try:
                        # 对AI结果进行微调
                        if hasattr(self.natural_rewriter, 'rewrite_naturally'):
                            final_result = self.natural_rewriter.rewrite_naturally(
                                ai_result,
                                style
                            )
                        elif hasattr(self.natural_rewriter, 'rewrite'):
                            final_result = self.natural_rewriter.rewrite(
                                ai_result,
                                style=style
                            )
                        else:
                            final_result = ai_result
                        return final_result if final_result else ai_result
                    except Exception as e:
                        print(f"⚠️  混合模式微调失败: {e}")
                        return ai_result
                
                return ai_result if ai_result else text
                
            except Exception as e:
                print(f"⚠️  AI改写失败: {e}，使用传统方法")
                # 降级到传统方法
                if self.natural_rewriter:
                    try:
                        if hasattr(self.natural_rewriter, 'rewrite_naturally'):
                            return self.natural_rewriter.rewrite_naturally(text, style)
                        elif hasattr(self.natural_rewriter, 'rewrite'):
                            return self.natural_rewriter.rewrite(text, style=style)
                    except Exception as e2:
                        print(f"⚠️  传统改写也失败: {e2}")
                return text
        
        # 使用传统方法
        if self.natural_rewriter:
            try:
                if hasattr(self.natural_rewriter, 'rewrite_naturally'):
                    return self.natural_rewriter.rewrite_naturally(text, style)
                elif hasattr(self.natural_rewriter, 'rewrite'):
                    return self.natural_rewriter.rewrite(text, style=style)
            except Exception as e:
                print(f"⚠️  传统改写失败: {e}")
        
        return text
    
    def analyze(self, content: str) -> Dict:
        """
        分析内容（统一接口）
        
        Args:
            content: 文本内容
        
        Returns:
            分析结果字典
        """
        result = {
            'characters': {},
            'storyline': {},
            'plot': {}
        }
        
        if self.ai_analyzer:
            try:
                result['characters'] = self.ai_analyzer.analyze_characters(content)
                result['storyline'] = self.ai_analyzer.analyze_storyline(content)
                result['plot'] = self.ai_analyzer.analyze_plot(content)
            except Exception as e:
                print(f"⚠️  AI分析失败: {e}")
        
        return result
    
    def generate(self, 
                 base_content: str,
                 generation_type: str = "expand",
                 **kwargs) -> str:
        """
        生成内容（统一接口）
        
        Args:
            base_content: 基础内容
            generation_type: 生成类型 (expand/continue/new_chapter/creative)
            **kwargs: 其他参数
        
        Returns:
            生成的内容
        """
        if ContentGenerator:
            try:
                generator = ContentGenerator()
                
                if generation_type == "expand":
                    # expand_content需要chapter_num参数
                    chapter_num = kwargs.get('chapter_num', 1)
                    expansion_type = kwargs.get('expansion_type', '细节')
                    return generator.expand_content(chapter_num, expansion_type)
                elif generation_type == "continue":
                    # 使用creative_generate代替continue_story
                    theme = kwargs.get('theme', '冒险')
                    length = kwargs.get('length', 1000)
                    return generator.creative_generate(theme, length)
                elif generation_type == "new_chapter":
                    chapter_num = kwargs.get('chapter_num', 1)
                    title = kwargs.get('title')
                    style = kwargs.get('style', '延续')
                    chapter_dict = generator.generate_new_chapter(chapter_num, title, style)
                    return chapter_dict.get('content', '') if isinstance(chapter_dict, dict) else str(chapter_dict)
                elif generation_type == "creative":
                    theme = kwargs.get('theme', '冒险')
                    length = kwargs.get('length', 1000)
                    return generator.creative_generate(theme, length)
                else:
                    return base_content
                    
            except Exception as e:
                print(f"⚠️  内容生成失败: {e}")
                import traceback
                traceback.print_exc()
                return base_content
        else:
            print("⚠️  内容生成器不可用")
            return base_content


class CreativeAIEngine:
    """
    创意AI引擎
    整合深度学习和创意处理功能
    """
    
    def __init__(self,
                 ai_type: str = "tensorflow",
                 ai_model_path: Optional[str] = None):
        """
        初始化创意AI引擎
        
        Args:
            ai_type: AI类型
            ai_model_path: 模型路径
        """
        self.rewriter = UnifiedRewriter(
            ai_type=ai_type,
            ai_model_path=ai_model_path,
            use_hybrid=True
        )
    
    def process_novel(self,
                     content: str,
                     style: str,
                     operations: List[str] = None) -> Dict[str, str]:
        """
        处理小说（完整流程）
        
        Args:
            content: 小说内容
            style: 目标风格
            operations: 操作列表 (analyze/rewrite/generate)
        
        Returns:
            处理结果字典
        """
        if operations is None:
            operations = ['analyze', 'rewrite']
        
        results = {}
        
        # 分析
        if 'analyze' in operations:
            results['analysis'] = self.rewriter.analyze(content)
        
        # 改写
        if 'rewrite' in operations:
            results['rewritten'] = self.rewriter.rewrite(
                content,
                style=style,
                use_ai=True
            )
        
        # 生成
        if 'generate' in operations:
            results['generated'] = self.rewriter.generate(
                content,
                generation_type='creative',
                theme='冒险',
                length=1000
            )
        
        return results


def create_engine(ai_type: str = "tensorflow",
                  ai_model_path: Optional[str] = None) -> CreativeAIEngine:
    """
    创建创意AI引擎（工厂函数）
    
    Args:
        ai_type: AI类型
        ai_model_path: 模型路径
    
    Returns:
        创意AI引擎实例
    """
    return CreativeAIEngine(
        ai_type=ai_type,
        ai_model_path=ai_model_path
    )
