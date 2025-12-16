#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
训练数据生成器（统一版本）
从爬取的小说生成训练数据，支持多网站、多类型
"""

import os
import sys
import re
import json
from typing import List, Dict, Optional
from pathlib import Path

# 导入数据增强模块
try:
    from ..utils.data_enhancer import DataEnhancer
except ImportError:
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))
    from data_enhancer import DataEnhancer


class TrainingDataGenerator:
    """训练数据生成器"""
    
    # 配置参数（优化版）
    MIN_CHUNK_LENGTH = 300        # 最小文本块长度（增加以保持更多上下文）
    MAX_CHUNK_LENGTH = 3000       # 最大文本块长度（增加以保持更多上下文）
    CHUNK_OVERLAP = 200           # 文本块重叠长度（增加以保持连续性）
    MAX_SAMPLES_PER_NOVEL = 200   # 每本小说最多生成样本数（大幅增加）
    MAX_TOTAL_SAMPLES = 500000    # 总样本数限制（增加）
    CONTEXT_WINDOW = 500          # 上下文窗口大小（用于保持前后文连贯）
    
    def __init__(self, output_dir: str = "data/training"):
        """
        初始化生成器
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = output_dir
        self.novels_dir = os.path.join(output_dir, 'novels')
        self.processed_dir = os.path.join(output_dir, 'processed')
        os.makedirs(self.processed_dir, exist_ok=True)
    
    def _detect_directory_structure(self, base_dir: str) -> str:
        """
        检测目录结构类型
        
        Args:
            base_dir: 基础目录
        
        Returns:
            'novels' 或 'processed' 或 'unknown'
        """
        if not os.path.exists(base_dir):
            return 'unknown'
        
        # 检查第一层目录
        first_level_items = [item for item in os.listdir(base_dir) 
                           if os.path.isdir(os.path.join(base_dir, item))]
        
        if not first_level_items:
            return 'unknown'
        
        # 检查是否是novels结构（网站/类型/小说名/）
        # 或processed结构（类型/小说名.txt）
        for item in first_level_items[:3]:  # 检查前3个
            item_path = os.path.join(base_dir, item)
            # 检查第二层
            second_level_items = [sub_item for sub_item in os.listdir(item_path)
                                if os.path.isdir(os.path.join(item_path, sub_item))]
            
            if second_level_items:
                # 检查第三层（novels结构：类型/小说名/）
                for sub_item in second_level_items[:2]:
                    sub_path = os.path.join(item_path, sub_item)
                    third_level_items = [t_item for t_item in os.listdir(sub_path)
                                       if os.path.isdir(os.path.join(sub_path, t_item))]
                    if third_level_items:
                        return 'novels'
            
            # 检查是否是processed结构（类型/小说名.txt）
            txt_files = [f for f in os.listdir(item_path) if f.endswith('.txt')]
            if txt_files:
                return 'processed'
        
        return 'unknown'
    
    def _find_novel_files(self, base_dir: str) -> List[tuple]:
        """
        查找所有小说文件（支持两种目录结构）
        
        Args:
            base_dir: 基础目录
        
        Returns:
            [(文件路径, 小说名, 类型), ...]
        """
        structure = self._detect_directory_structure(base_dir)
        files = []
        
        if structure == 'novels':
            # novels结构：网站/类型/小说名/小说名.txt
            for site_name in os.listdir(base_dir):
                site_dir = os.path.join(base_dir, site_name)
                if not os.path.isdir(site_dir):
                    continue
                
                for category in os.listdir(site_dir):
                    category_dir = os.path.join(site_dir, category)
                    if not os.path.isdir(category_dir):
                        continue
                    
                    for novel_name in os.listdir(category_dir):
                        novel_dir = os.path.join(category_dir, novel_name)
                        if not os.path.isdir(novel_dir):
                            continue
                        
                        # 在小说目录中查找txt文件
                        for file_name in os.listdir(novel_dir):
                            if file_name.endswith('.txt'):
                                files.append((
                                    os.path.join(novel_dir, file_name),
                                    novel_name,
                                    category
                                ))
                                break
        
        elif structure == 'processed':
            # processed结构：类型/小说名.txt
            for category in os.listdir(base_dir):
                category_dir = os.path.join(base_dir, category)
                if not os.path.isdir(category_dir):
                    continue
                
                for file_name in os.listdir(category_dir):
                    if file_name.endswith('.txt'):
                        novel_name = file_name[:-4]  # 移除.txt后缀
                        files.append((
                            os.path.join(category_dir, file_name),
                            novel_name,
                            category
                        ))
        
        return files
    
    def generate_from_novels(self, use_ai: bool = False, enhance: bool = True, balance: bool = True, fallback_dir: Optional[str] = None) -> str:
        """
        从爬取的小说生成训练数据（支持两种目录结构）
        
        Args:
            use_ai: 是否使用AI生成改写样本
            enhance: 是否使用数据增强
            balance: 是否平衡数据集
            fallback_dir: 回退目录（如果当前目录生成失败）
        
        Returns:
            训练数据文件路径
        """
        print(f"\n📝 开始生成训练数据...")
        print(f"   源目录: {self.novels_dir}")
        
        if not os.path.exists(self.novels_dir):
            print(f"❌ 源目录不存在: {self.novels_dir}")
            # 尝试回退目录
            if fallback_dir and os.path.exists(fallback_dir):
                print(f"   ⚠️  尝试回退到: {fallback_dir}")
                self.novels_dir = fallback_dir
            else:
                return None
        
        # 检测目录结构
        structure = self._detect_directory_structure(self.novels_dir)
        print(f"   检测到目录结构: {structure}")
        
        if structure == 'unknown':
            print(f"   ⚠️  无法识别目录结构，尝试回退...")
            if fallback_dir and os.path.exists(fallback_dir):
                print(f"   回退到: {fallback_dir}")
                original_dir = self.novels_dir
                self.novels_dir = fallback_dir
                structure = self._detect_directory_structure(self.novels_dir)
                if structure == 'unknown':
                    self.novels_dir = original_dir
                    print(f"   ❌ 回退目录也无法识别结构")
                    return None
            else:
                print(f"   ❌ 无法识别目录结构，且无回退目录")
                return None
        
        training_samples = []
        
        # 查找所有小说文件
        novel_files = self._find_novel_files(self.novels_dir)
        
        if not novel_files:
            print(f"   ❌ 未找到任何小说文件")
            # 尝试回退
            if fallback_dir and os.path.exists(fallback_dir) and fallback_dir != self.novels_dir:
                print(f"   ⚠️  尝试回退到: {fallback_dir}")
                original_dir = self.novels_dir
                self.novels_dir = fallback_dir
                novel_files = self._find_novel_files(self.novels_dir)
                if not novel_files:
                    self.novels_dir = original_dir
                    return None
        
        print(f"   找到 {len(novel_files)} 本小说")
        
        # 按类型分组处理
        novels_by_category = {}
        for file_path, novel_name, category in novel_files:
            if category not in novels_by_category:
                novels_by_category[category] = []
            novels_by_category[category].append((file_path, novel_name))
        
        for category, novels in novels_by_category.items():
            print(f"\n   处理类型: {category} ({len(novels)} 本)")
            
            for txt_file, novel_name in novels:
                try:
                    with open(txt_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 提取章节（支持多种格式）
                    chapter_patterns = [
                        r'第\s*(\d+)\s*章[：:：]?\s*(.*?)\n',
                        r'第\s*[一二三四五六七八九十百千万]+\s*章[：:：]?\s*(.*?)\n',
                        r'Chapter\s*\d+[：:：]?\s*(.*?)\n',
                    ]
                    
                    chapter_matches = []
                    for pattern in chapter_patterns:
                        matches = list(re.finditer(pattern, content))
                        if matches:
                            chapter_matches = matches
                            break
                    
                    if not chapter_matches:
                        # 如果没有找到章节标记，按段落分割
                        paragraphs = re.split(r'\n\s*\n', content)
                        chapter_matches = [None] * len(paragraphs)
                    
                    # 为每个章节生成训练样本（增强版，包含上下文）
                    samples_generated = 0
                    novel_context = self._extract_novel_context(content)  # 提取整本小说的上下文信息
                    
                    for i, match in enumerate(chapter_matches):
                        if samples_generated >= self.MAX_SAMPLES_PER_NOVEL:
                            break
                        
                        if match:
                            chapter_start = match.end()
                            next_match = chapter_matches[i + 1] if i + 1 < len(chapter_matches) else None
                            chapter_end = next_match.start() if next_match else min(chapter_start + self.MAX_CHUNK_LENGTH, len(content))
                        else:
                            # 段落模式
                            chapter_start = 0
                            chapter_end = len(content)
                        
                        chapter_text = content[chapter_start:chapter_end].strip()
                        
                        if len(chapter_text) < self.MIN_CHUNK_LENGTH:
                            continue
                        
                        # 获取前后章节的上下文（用于保持连贯性）
                        prev_context = ""
                        if i > 0:
                            prev_start = max(0, chapter_start - self.CONTEXT_WINDOW)
                            prev_context = content[prev_start:chapter_start].strip()
                        
                        next_context = ""
                        if next_match:
                            next_end = min(len(content), chapter_end + self.CONTEXT_WINDOW)
                            next_context = content[chapter_end:next_end].strip()
                        
                        # 将章节分割成多个文本块（数据增强，包含上下文）
                        chunks = self._split_into_chunks_with_context(
                            chapter_text, 
                            prev_context, 
                            next_context,
                            novel_context
                        )
                        
                        for chunk_data in chunks:
                            chunk = chunk_data['text']
                            if len(chunk) < self.MIN_CHUNK_LENGTH:
                                continue
                            
                            # 限制长度
                            original = chunk[:self.MAX_CHUNK_LENGTH].strip()
                            
                            # 风格ID（根据category映射）
                            style_id = self._get_style_id(category)
                            
                            # 生成改写文本（使用AI改写，如果可用）
                            rewritten = self._generate_rewritten_text(
                                original, 
                                style_id, 
                                chunk_data.get('context', ''),
                                use_ai=use_ai
                            )
                            
                            # 包含上下文信息（用于训练时保持连贯性）
                            training_samples.append({
                                'original': original,
                                'rewritten': rewritten,
                                'style': style_id,
                                'source': novel_name,
                                'site': 'm.shuhaige.net',  # 添加site字段（从目录结构推断）
                                'category': category,
                                'context': chunk_data.get('context', ''),  # 上下文信息
                                'chapter_num': i + 1,  # 章节号
                            })
                            
                            samples_generated += 1
                            
                            if len(training_samples) >= self.MAX_TOTAL_SAMPLES:
                                break
                        
                        if len(training_samples) >= self.MAX_TOTAL_SAMPLES:
                            break
                
                except (OSError, IOError, UnicodeDecodeError) as e:
                    print(f"      ⚠️  处理 {novel_name} 时出错: {e}")
                    continue
                
                if len(training_samples) >= self.MAX_TOTAL_SAMPLES:
                    break
            
            if len(training_samples) >= self.MAX_TOTAL_SAMPLES:
                break
        
        # 数据增强
        if enhance and training_samples:
            print(f"\n🔄 进行数据增强...")
            original_count = len(training_samples)
            
            # 为部分样本生成变体
            enhanced_samples = []
            for sample in training_samples[:min(1000, len(training_samples))]:  # 最多增强1000个样本
                variations = DataEnhancer.generate_variations(
                    sample['original'],
                    sample['rewritten'],
                    count=1
                )
                for orig_var, rew_var in variations:
                    enhanced_samples.append({
                        **sample,
                        'original': orig_var,
                        'rewritten': rew_var
                    })
            
            training_samples.extend(enhanced_samples)
            print(f"   增强后样本数: {len(training_samples)} (增加了 {len(training_samples) - original_count} 个)")
        
        # 数据集平衡
        if balance and training_samples:
            print(f"\n⚖️  平衡数据集...")
            original_count = len(training_samples)
            training_samples = DataEnhancer.balance_dataset(training_samples)
            print(f"   平衡后样本数: {len(training_samples)}")
        
        # 检查是否有训练样本
        if not training_samples:
            print(f"\n❌ 警告: 没有生成任何训练样本！")
            print(f"   请检查:")
            print(f"   1. 小说文件是否存在")
            print(f"   2. 小说内容是否有效")
            print(f"   3. 文本块长度是否满足要求（最小{self.MIN_CHUNK_LENGTH}字符）")
            return None
        
        # 保存训练数据（TSV格式）
        training_data_file = os.path.join(self.processed_dir, 'training_data.txt')
        
        # 验证样本格式
        valid_samples = []
        invalid_count = 0
        for sample in training_samples:
            if not isinstance(sample, dict):
                invalid_count += 1
                continue
            
            orig = sample.get('original', '').strip()
            rew = sample.get('rewritten', '').strip()
            style = sample.get('style', 11)
            
            # 验证必需字段
            if not orig or not rew:
                invalid_count += 1
                continue
            
            # 验证长度
            if len(orig) < 10 or len(rew) < 10:
                invalid_count += 1
                continue
            
            # 验证风格ID
            if not isinstance(style, int):
                try:
                    style = int(style)
                except (ValueError, TypeError):
                    invalid_count += 1
                    continue
            
            valid_samples.append(sample)
        
        if invalid_count > 0:
            print(f"   ⚠️  过滤了 {invalid_count} 个无效样本")
        
        if not valid_samples:
            print(f"\n❌ 错误: 所有训练样本都无效！")
            return None
        
        # 保存有效的训练样本
        with open(training_data_file, 'w', encoding='utf-8') as f:
            for sample in valid_samples:
                orig = sample['original'].replace('\t', ' ').replace('\r', '').replace('\n', ' ').strip()
                rew = sample['rewritten'].replace('\t', ' ').replace('\r', '').replace('\n', ' ').strip()
                
                # 限制长度
                if len(orig) > 2000:
                    orig = orig[:2000]
                if len(rew) > 2000:
                    rew = rew[:2000]
                
                # 确保orig和rew不为空
                if not orig or not rew:
                    continue
                
                # 写入TSV格式：原始文本<TAB>改写文本<TAB>风格ID<TAB>上下文（可选）
                context = sample.get('context', '')
                if context:
                    context = context.replace('\t', ' ').replace('\r', '').replace('\n', ' ')[:500]  # 限制上下文长度
                    f.write(f"{orig}\t{rew}\t{sample['style']}\t{context}\n")
                else:
                    f.write(f"{orig}\t{rew}\t{sample['style']}\n")
        
        # 验证保存的文件格式
        valid_lines = 0
        with open(training_data_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 3:
                    try:
                        int(parts[2])  # 验证风格ID是整数
                        if len(parts[0]) > 10 and len(parts[1]) > 10:
                            valid_lines += 1
                    except ValueError:
                        pass
        
        print(f"\n✅ 生成完成，共 {len(valid_samples)} 条有效训练样本")
        print(f"   文件: {training_data_file}")
        print(f"   验证: {valid_lines}/{len(valid_samples)} 条格式正确")
        
        if valid_lines < len(valid_samples) * 0.9:
            print(f"   ⚠️  警告: 部分数据格式可能有问题")
        
        # 生成统计信息
        stats = {
            'total_samples': len(training_samples),
            'sites': {},
            'categories': {}
        }
        
        for sample in training_samples:
            site = sample['site']
            category = sample['category']
            
            if site not in stats['sites']:
                stats['sites'][site] = 0
            stats['sites'][site] += 1
            
            if category not in stats['categories']:
                stats['categories'][category] = 0
            stats['categories'][category] += 1
        
        stats_file = os.path.join(self.processed_dir, 'training_stats.json')
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        print(f"   统计: {stats_file}")
        
        return training_data_file
    
    def _split_into_chunks(self, text: str) -> List[str]:
        """
        将文本分割成多个块（用于数据增强）
        
        Args:
            text: 原始文本
        
        Returns:
            文本块列表
        """
        chunks = []
        
        # 按段落分割
        paragraphs = re.split(r'\n\s*\n', text)
        
        current_chunk = ""
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # 如果当前块加上新段落超过最大长度，保存当前块
            if len(current_chunk) + len(para) > self.MAX_CHUNK_LENGTH:
                if len(current_chunk) >= self.MIN_CHUNK_LENGTH:
                    chunks.append(current_chunk)
                # 开始新块（保留重叠部分）
                if self.CHUNK_OVERLAP > 0 and len(current_chunk) > self.CHUNK_OVERLAP:
                    current_chunk = current_chunk[-self.CHUNK_OVERLAP:] + "\n\n" + para
                else:
                    current_chunk = para
            else:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
        
        # 添加最后一个块
        if len(current_chunk) >= self.MIN_CHUNK_LENGTH:
            chunks.append(current_chunk)
        
        # 如果只有一个块，尝试进一步分割
        if len(chunks) == 1 and len(chunks[0]) > self.MAX_CHUNK_LENGTH:
            # 按句子分割
            sentences = re.split(r'[。！？\n]', chunks[0])
            chunks = []
            current_chunk = ""
            for sent in sentences:
                sent = sent.strip()
                if not sent:
                    continue
                if len(current_chunk) + len(sent) > self.MAX_CHUNK_LENGTH:
                    if len(current_chunk) >= self.MIN_CHUNK_LENGTH:
                        chunks.append(current_chunk)
                    current_chunk = sent
                else:
                    current_chunk += sent
        
        return chunks if chunks else [text]
    
    def _split_into_chunks_with_context(self, text: str, prev_context: str, 
                                        next_context: str, novel_context: Dict) -> List[Dict]:
        """
        将文本分割成多个块，并包含上下文信息（增强版）
        
        Args:
            text: 原始文本
            prev_context: 前文上下文
            next_context: 后文上下文
            novel_context: 整本小说的上下文信息
        
        Returns:
            包含文本和上下文的字典列表
        """
        chunks = []
        
        # 按段落分割
        paragraphs = re.split(r'\n\s*\n', text)
        
        current_chunk = ""
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # 如果当前块加上新段落超过最大长度，保存当前块
            if len(current_chunk) + len(para) > self.MAX_CHUNK_LENGTH:
                if len(current_chunk) >= self.MIN_CHUNK_LENGTH:
                    # 构建上下文信息
                    context_info = self._build_context_info(
                        current_chunk, prev_context, next_context, novel_context
                    )
                    chunks.append({
                        'text': current_chunk,
                        'context': context_info
                    })
                # 开始新块（保留重叠部分）
                if self.CHUNK_OVERLAP > 0 and len(current_chunk) > self.CHUNK_OVERLAP:
                    current_chunk = current_chunk[-self.CHUNK_OVERLAP:] + "\n\n" + para
                else:
                    current_chunk = para
            else:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
        
        # 添加最后一个块
        if len(current_chunk) >= self.MIN_CHUNK_LENGTH:
            context_info = self._build_context_info(
                current_chunk, prev_context, next_context, novel_context
            )
            chunks.append({
                'text': current_chunk,
                'context': context_info
            })
        
        # 如果只有一个块，尝试进一步分割
        if len(chunks) == 1 and len(chunks[0]['text']) > self.MAX_CHUNK_LENGTH:
            # 按句子分割
            sentences = re.split(r'[。！？\n]', chunks[0]['text'])
            chunks = []
            current_chunk = ""
            for sent in sentences:
                sent = sent.strip()
                if not sent:
                    continue
                if len(current_chunk) + len(sent) > self.MAX_CHUNK_LENGTH:
                    if len(current_chunk) >= self.MIN_CHUNK_LENGTH:
                        context_info = self._build_context_info(
                            current_chunk, prev_context, next_context, novel_context
                        )
                        chunks.append({
                            'text': current_chunk,
                            'context': context_info
                        })
                    current_chunk = sent
                else:
                    current_chunk += sent
        
        return chunks if chunks else [{'text': text, 'context': ''}]
    
    def _extract_novel_context(self, content: str) -> Dict:
        """
        提取整本小说的上下文信息（人物、情节、主题等）
        
        Args:
            content: 小说内容
        
        Returns:
            上下文信息字典
        """
        context = {
            'characters': [],
            'main_plot': '',
            'themes': [],
            'setting': ''
        }
        
        # 提取主要人物（简单方法：高频出现的2-3字词）
        import re
        from collections import Counter
        
        # 提取可能的姓名（2-3个中文字符）
        name_pattern = r'[\u4e00-\u9fa5]{2,3}'
        potential_names = re.findall(name_pattern, content[:10000])  # 只分析前10000字符
        name_counter = Counter(potential_names)
        
        # 排除常见词
        exclude_words = {'大家', '自己', '他们', '我们', '你们', '她们', '它们', 
                        '什么', '怎么', '这样', '那样', '这个', '那个', '这些', '那些',
                        '今天', '明天', '昨天', '现在', '以后', '之前', '之后'}
        
        # 获取前10个高频词作为主要人物
        for name, count in name_counter.most_common(20):
            if name not in exclude_words and count >= 5:
                context['characters'].append(name)
                if len(context['characters']) >= 10:
                    break
        
        # 提取主题关键词（简化版）
        theme_keywords = {
            '都市': ['都市', '城市', '公司', '职场'],
            '玄幻': ['修炼', '境界', '功法', '丹药'],
            '言情': ['爱情', '恋爱', '结婚', '感情'],
            '武侠': ['武功', '江湖', '门派', '剑法'],
        }
        
        # 检测主题
        for theme, keywords in theme_keywords.items():
            if any(kw in content[:5000] for kw in keywords):
                context['themes'].append(theme)
        
        return context
    
    def _build_context_info(self, text: str, prev_context: str, 
                           next_context: str, novel_context: Dict) -> str:
        """
        构建上下文信息字符串
        
        Args:
            text: 当前文本
            prev_context: 前文
            next_context: 后文
            novel_context: 小说上下文
        
        Returns:
            上下文信息字符串
        """
        context_parts = []
        
        # 添加小说级别上下文
        if novel_context.get('characters'):
            context_parts.append(f"主要人物: {', '.join(novel_context['characters'][:5])}")
        if novel_context.get('themes'):
            context_parts.append(f"主题: {', '.join(novel_context['themes'][:3])}")
        
        # 添加前文上下文（摘要）
        if prev_context:
            prev_summary = prev_context[-200:] if len(prev_context) > 200 else prev_context
            context_parts.append(f"前文: {prev_summary}")
        
        # 添加后文上下文（预览）
        if next_context:
            next_preview = next_context[:200] if len(next_context) > 200 else next_context
            context_parts.append(f"后文: {next_preview}")
        
        return " | ".join(context_parts)
    
    def _get_style_id(self, category: str) -> int:
        """
        根据分类获取风格ID
        
        Args:
            category: 小说分类
        
        Returns:
            风格ID
        """
        style_map = {
            '都市': 11,
            '玄幻': 8,
            '言情': 5,
            '武侠': 9,
            '科幻': 8,
            '悬疑': 4,
            '历史': 1,
            '军事': 7,
            '游戏': 12,
            '竞技': 13,
            '仙侠': 10,
            '其他': 11,
            '未知': 11,
        }
        return style_map.get(category, 11)
    
    def _generate_rewritten_text(self, 
                                 original: str, 
                                 style_id: int,
                                 context: str = "",
                                 use_ai: bool = False) -> str:
        """
        生成改写文本（支持AI改写）
        
        Args:
            original: 原始文本
            style_id: 风格ID
            context: 上下文信息
            use_ai: 是否使用AI改写
        
        Returns:
            改写后的文本
        """
        if not use_ai:
            # 如果不使用AI，使用规则改写
            return self._rule_based_rewrite(original, style_id)
        
        # 尝试使用AI改写
        try:
            # 导入AI模块
            import sys
            import os
            ai_path = os.path.join(os.path.dirname(__file__), '..', 'ai', 'models')
            if ai_path not in sys.path:
                sys.path.insert(0, ai_path)
            
            from tensorflow_model import TensorFlowTextRewriter
            
            # 检查模型是否存在
            model_path = "models/text_rewriter_model"
            if os.path.exists(os.path.join(model_path, 'vocab.json')):
                try:
                    rewriter = TensorFlowTextRewriter(model_path=model_path)
                    if rewriter.load_vocab() and rewriter.load_model():
                        # 使用模型改写
                        rewritten = rewriter.rewrite(
                            original, 
                            style=style_id,
                            context=context[:200] if context else None,
                            temperature=0.7
                        )
                        if rewritten and rewritten != original and len(rewritten) > len(original) * 0.5:
                            return rewritten
                except Exception:
                    # AI改写失败，使用降级方案
                    pass
        except ImportError:
            # AI模块不可用
            pass
        except Exception:
            # 其他错误
            pass
        
        # 降级方案：使用简单的规则改写（基于风格）
        return self._rule_based_rewrite(original, style_id)
    
    def _rule_based_rewrite(self, text: str, style_id: int) -> str:
        """
        基于规则的简单改写（降级方案）
        
        Args:
            text: 原始文本
            style_id: 风格ID
        
        Returns:
            改写后的文本
        """
        import re
        
        # 风格映射到规则
        style_rules = {
            11: {'城市': '都市', '地方': '都市'},  # 都市
            6: {'很': '超级', '非常': '超级', '好': '棒极了'},  # 幽默
            18: {'城市': '都市', '很': '超级', '非常': '超级'},  # 都市幽默
        }
        
        rules = style_rules.get(style_id, {})
        result = text
        
        # 应用规则（适度，避免过度替换）
        for old, new in rules.items():
            # 使用单词边界，避免部分匹配
            pattern = r'\b' + re.escape(old) + r'\b'
            # 只替换前几次，避免过度
            count = min(3, text.count(old) // 3) if text.count(old) > 0 else 0
            if count > 0:
                result = re.sub(pattern, new, result, count=count)
        
        return result if result != text else text
    
    def _escape_tsv(self, text: str) -> str:
        """
        转义TSV格式中的特殊字符
        
        Args:
            text: 原始文本
        
        Returns:
            转义后的文本
        """
        # 替换制表符和换行符
        text = text.replace('\t', ' ').replace('\r', '').replace('\n', ' ')
        # 移除多余空白
        text = re.sub(r' +', ' ', text)
        return text.strip()

