#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于TensorFlow的本地语言模型
用于文本改写和语言优化
"""

import os
import re
import json
import numpy as np
from typing import Dict, List, Optional, Tuple
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models, optimizers, callbacks


class TensorFlowTextRewriter:
    """基于TensorFlow的文本改写器"""
    
    def __init__(self, model_path: Optional[str] = None, vocab_size: int = 10000, embedding_dim: int = 256):
        """
        初始化TensorFlow文本改写器
        
        Args:
            model_path: 模型保存路径
            vocab_size: 词汇表大小
            embedding_dim: 词向量维度
        """
        self.model_path = model_path or "models/text_rewriter_model"
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.model = None
        self.tokenizer = None
        self.vocab = {}
        self.reverse_vocab = {}
        self.max_length = 1024  # 增加最大长度以支持更长的上下文
        
        # 检查是否有GPU
        self.use_gpu = len(tf.config.list_physical_devices('GPU')) > 0
        if self.use_gpu:
            print("✅ 检测到GPU，将使用GPU加速")
        else:
            print("⚠️  未检测到GPU，将使用CPU（速度较慢）")
    
    def build_tokenizer(self, texts: List[str]):
        """构建词汇表和分词器"""
        print("📚 构建词汇表...")
        
        # 简单的字符级分词（中文适合字符级）
        all_chars = set()
        for text in texts:
            all_chars.update(text)
        
        # 构建词汇表
        special_tokens = ['<PAD>', '<UNK>', '<START>', '<END>']
        vocab_list = special_tokens + sorted(list(all_chars))
        
        self.vocab = {char: idx for idx, char in enumerate(vocab_list)}
        self.reverse_vocab = {idx: char for char, idx in self.vocab.items()}
        self.vocab_size = len(self.vocab)
        
        print(f"✅ 词汇表构建完成，共 {self.vocab_size} 个字符")
    
    def text_to_sequence(self, text: str, max_length: Optional[int] = None) -> List[int]:
        """将文本转换为序列"""
        if max_length is None:
            max_length = self.max_length
        
        sequence = [self.vocab.get('<START>', 1)]
        for char in text[:max_length-2]:
            sequence.append(self.vocab.get(char, self.vocab.get('<UNK>', 2)))
        sequence.append(self.vocab.get('<END>', 3))
        
        # 填充或截断
        if len(sequence) < max_length:
            sequence.extend([self.vocab.get('<PAD>', 0)] * (max_length - len(sequence)))
        else:
            sequence = sequence[:max_length]
        
        return sequence
    
    def sequence_to_text(self, sequence: List[int]) -> str:
        """将序列转换为文本"""
        text = ""
        for idx in sequence:
            if idx == self.vocab.get('<PAD>', 0):
                continue
            if idx == self.vocab.get('<START>', 1):
                continue
            if idx == self.vocab.get('<END>', 3):
                break
            char = self.reverse_vocab.get(idx, '<UNK>')
            if char not in ['<PAD>', '<UNK>', '<START>', '<END>']:
                text += char
        return text
    
    def build_model(self, style_embedding_dim: int = 64, num_layers: int = 3, num_heads: int = 8):
        """
        构建Transformer风格的改写模型
        
        Args:
            style_embedding_dim: 风格嵌入维度
            num_layers: Transformer层数
            num_heads: 注意力头数
        """
        print("🏗️  构建深度学习模型...")
        print(f"   配置: {num_layers}层, {num_heads}个注意力头, 嵌入维度{self.embedding_dim}")
        
        # 输入层
        input_text = layers.Input(shape=(self.max_length,), name='input_text')
        input_style = layers.Input(shape=(1,), name='input_style', dtype='int32')
        
        # 文本嵌入（添加位置编码）
        text_embedding = layers.Embedding(
            self.vocab_size, 
            self.embedding_dim,
            mask_zero=True,
            name='text_embedding'
        )(input_text)
        
        # 位置编码（可学习的）
        position_encoding = layers.Embedding(
            self.max_length,
            self.embedding_dim,
            name='position_encoding'
        )(tf.range(self.max_length))
        text_embedding = text_embedding + position_encoding
        
        # 风格嵌入
        style_embedding = layers.Embedding(
            20,  # 支持20种风格
            style_embedding_dim,
            name='style_embedding'
        )(input_style)
        # Embedding输出形状: (batch_size, 1, style_embedding_dim)
        # 需要先展平为 (batch_size, style_embedding_dim) 才能用RepeatVector
        style_embedding_flat = layers.Flatten()(style_embedding)  # 展平为 (batch_size, style_embedding_dim)
        
        # 扩展风格嵌入以匹配文本长度
        # RepeatVector需要2维输入 (batch_size, features)，输出 (batch_size, timesteps, features)
        style_embedding_expanded = layers.RepeatVector(self.max_length)(style_embedding_flat)
        # 现在形状是 (batch_size, max_length, style_embedding_dim)，不需要Reshape了
        
        # 融合文本和风格嵌入
        combined = layers.Concatenate()([text_embedding, style_embedding_expanded])
        
        # Transformer编码器（可配置层数）
        x = combined
        for i in range(num_layers):
            # 多头注意力
            attention = layers.MultiHeadAttention(
                num_heads=num_heads,
                key_dim=self.embedding_dim + style_embedding_dim,
                name=f'attention_{i}'
            )(x, x)
            
            # 残差连接和层归一化
            x = layers.Add(name=f'add_{i}')([x, attention])
            x = layers.LayerNormalization(name=f'norm_{i}')(x)
            
            # 前馈网络（更深的网络）
            ffn = layers.Dense((self.embedding_dim + style_embedding_dim) * 2, activation='relu', name=f'ffn_{i}_1')(x)
            ffn = layers.Dropout(0.1, name=f'dropout_{i}')(ffn)
            ffn = layers.Dense(self.embedding_dim + style_embedding_dim, name=f'ffn_{i}_2')(ffn)
            
            # 残差连接和层归一化
            x = layers.Add(name=f'add_ffn_{i}')([x, ffn])
            x = layers.LayerNormalization(name=f'norm_ffn_{i}')(x)
        
        # 全局池化（可选）
        # x = layers.GlobalAveragePooling1D()(x)
        
        # 输出层
        output = layers.Dense(self.vocab_size, activation='softmax', name='output')(x)
        
        # 构建模型
        self.model = models.Model(
            inputs=[input_text, input_style],
            outputs=output,
            name='text_rewriter'
        )
        
        # 编译模型（使用更优化的学习率和指标）
        self.model.compile(
            optimizer=optimizers.Adam(learning_rate=0.001, beta_1=0.9, beta_2=0.999),
            loss='sparse_categorical_crossentropy',
            metrics=[
                'accuracy', 
                'sparse_top_k_categorical_accuracy',
                'sparse_categorical_crossentropy'  # 添加交叉熵作为指标
            ]
        )
        
        print("✅ 模型构建完成")
        print(f"   模型参数数量: {self.model.count_params():,}")
        
        # 显示模型结构摘要
        if self.use_gpu:
            print("   GPU加速: 已启用")
    
    def prepare_training_data(self, original_texts: List[str], rewritten_texts: List[str], styles: List[int], 
                              augment: bool = False):
        """
        准备训练数据
        
        Args:
            original_texts: 原始文本列表
            rewritten_texts: 改写文本列表
            styles: 风格ID列表
            augment: 是否进行数据增强
        """
        print("📊 准备训练数据...")
        
        X_text = []
        X_style = []
        y = []
        
        for orig, rew, style in zip(original_texts, rewritten_texts, styles):
            # 数据增强（可选）
            if augment and len(orig) > 50:
                # 轻微的数据增强：随机截取或填充
                if len(orig) > self.max_length:
                    start = np.random.randint(0, len(orig) - self.max_length + 1)
                    orig = orig[start:start + self.max_length]
            
            orig_seq = self.text_to_sequence(orig)
            rew_seq = self.text_to_sequence(rew)
            
            X_text.append(orig_seq)
            X_style.append([style])
            
            # 为每个位置创建标签（下一个字符）
            y_seq = rew_seq[1:] + [self.vocab.get('<PAD>', 0)]
            y.append(y_seq)
        
        # 转换为numpy数组
        X_text = np.array(X_text)
        X_style = np.array(X_style)
        y = np.array(y)
        
        print(f"   数据形状: X_text={X_text.shape}, X_style={X_style.shape}, y={y.shape}")
        
        return X_text, X_style, y
    
    def train(self, original_texts: List[str], rewritten_texts: List[str], styles: List[int], 
              epochs: int = 10, batch_size: int = 32, validation_split: float = 0.2,
              validation_data: Tuple[List[str], List[str], List[int]] = None,
              learning_rate: float = None):
        """
        训练模型（增强版，支持自定义学习率）
        
        Args:
            original_texts: 原始文本列表
            rewritten_texts: 改写文本列表
            styles: 风格ID列表
            epochs: 训练轮数
            batch_size: 批次大小
            validation_split: 验证集比例（如果提供了validation_data则忽略）
            validation_data: 独立验证集 (原始文本, 改写文本, 风格ID)
            learning_rate: 学习率（可选，如果提供会更新优化器）
        """
        # 如果提供了学习率，更新优化器
        if learning_rate is not None:
            self.model.compile(
                optimizer=optimizers.Adam(learning_rate=learning_rate, beta_1=0.9, beta_2=0.999),
                loss='sparse_categorical_crossentropy',
                metrics=[
                    'accuracy', 
                    'sparse_top_k_categorical_accuracy',
                    'sparse_categorical_crossentropy'
                ]
            )
        print("🚀 开始训练模型...")
        
        # 准备数据
        X_text, X_style, y = self.prepare_training_data(original_texts, rewritten_texts, styles, augment=True)
        
        # 准备验证数据
        val_data = None
        if validation_data:
            val_orig, val_rew, val_styles = validation_data
            val_X_text, val_X_style, val_y = self.prepare_training_data(val_orig, val_rew, val_styles, augment=False)
            val_data = ([val_X_text, val_X_style], val_y)
            print(f"   使用独立验证集: {len(val_orig)} 条样本")
        
        # 创建保存目录
        os.makedirs(self.model_path, exist_ok=True)
        
        # 回调函数（增强版）
        callbacks_list = [
            callbacks.ModelCheckpoint(
                os.path.join(self.model_path, 'best_model.h5'),
                save_best_only=True,
                monitor='val_loss',
                verbose=1,
                save_weights_only=False
            ),
            callbacks.EarlyStopping(
                monitor='val_loss',
                patience=5,  # 增加耐心值
                restore_best_weights=True,
                verbose=1
            ),
            callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=3,  # 增加耐心值
                min_lr=1e-6,
                verbose=1
            ),
            callbacks.TensorBoard(
                log_dir=os.path.join(self.model_path, 'logs'),
                histogram_freq=1,
                write_graph=True
            )
        ]
        
        # 训练
        fit_kwargs = {
            'epochs': epochs,
            'batch_size': batch_size,
            'callbacks': callbacks_list,
            'verbose': 1
        }
        
        if val_data:
            fit_kwargs['validation_data'] = val_data
        else:
            fit_kwargs['validation_split'] = validation_split
        
        history = self.model.fit(
            [X_text, X_style],
            y,
            **fit_kwargs
        )
        
        # 保存模型
        self.model.save(os.path.join(self.model_path, 'final_model.h5'))
        # 如果best_model不存在，复制final_model
        best_file = os.path.join(self.model_path, 'best_model.h5')
        if not os.path.exists(best_file):
            import shutil
            shutil.copy(os.path.join(self.model_path, 'final_model.h5'), best_file)
        self.save_vocab()
        
        print("✅ 模型训练完成")
        return history
    
    def save_vocab(self):
        """保存词汇表"""
        vocab_file = os.path.join(self.model_path, 'vocab.json')
        with open(vocab_file, 'w', encoding='utf-8') as f:
            json.dump({
                'vocab': self.vocab,
                'reverse_vocab': {str(k): v for k, v in self.reverse_vocab.items()},
                'vocab_size': self.vocab_size,
                'max_length': self.max_length
            }, f, ensure_ascii=False, indent=2)
    
    def load_vocab(self):
        """加载词汇表"""
        vocab_file = os.path.join(self.model_path, 'vocab.json')
        if os.path.exists(vocab_file):
            with open(vocab_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.vocab = data['vocab']
                self.reverse_vocab = {int(k): v for k, v in data['reverse_vocab'].items()}
                self.vocab_size = data['vocab_size']
                self.max_length = data.get('max_length', 1024)  # 支持更长的上下文
            print("✅ 词汇表加载完成")
            return True
        return False
    
    def load_model(self):
        """加载模型"""
        model_file = os.path.join(self.model_path, 'best_model.h5')
        if not os.path.exists(model_file):
            model_file = os.path.join(self.model_path, 'final_model.h5')
        
        if os.path.exists(model_file):
            if not self.model:
                self.build_model()
            self.model.load_weights(model_file)
            print("✅ 模型加载完成")
            return True
        return False
    
    def rewrite(self, text: str, style: int = 0, temperature: float = 0.7, max_length: Optional[int] = None) -> str:
        """
        使用模型改写文本
        
        Args:
            text: 原始文本
            style: 风格ID
            temperature: 采样温度（0.1-1.0，越小越确定，越大越随机）
            max_length: 最大生成长度
        
        Returns:
            改写后的文本
        """
        if not self.model:
            if not self.load_model():
                raise ValueError("模型未训练或未加载，请先训练模型")
        
        if max_length is None:
            max_length = min(len(text) * 2, self.max_length)
        
        # 准备输入
        input_seq = self.text_to_sequence(text)
        input_text = np.array([input_seq])
        input_style = np.array([[style]])
        
        # 生成改写文本（使用贪心解码或采样）
        output_seq = []
        current_seq = input_seq.copy()
        
        try:
            for step in range(max_length):
                # 预测下一个字符
                predictions = self.model.predict([input_text, input_style], verbose=0, batch_size=1)
                
                if step >= predictions.shape[1]:
                    break
                
                next_char_probs = predictions[0, step, :]
                
                # 应用改进的采样策略（Top-k + Nucleus采样）
                if temperature > 0:
                    # Top-k采样（选择概率最高的k个字符）
                    top_k = 50
                    top_k_indices = np.argsort(next_char_probs)[-top_k:]
                    top_k_probs = next_char_probs[top_k_indices]
                    
                    # 应用温度
                    top_k_probs = np.log(top_k_probs + 1e-10) / temperature
                    top_k_probs = np.exp(top_k_probs)
                    top_k_probs = top_k_probs / np.sum(top_k_probs)
                    
                    # Nucleus采样（可选，累积概率阈值）
                    nucleus_threshold = 0.9
                    if nucleus_threshold < 1.0:
                        sorted_probs = np.sort(top_k_probs)[::-1]
                        cumsum_probs = np.cumsum(sorted_probs)
                        cutoff = np.searchsorted(cumsum_probs, nucleus_threshold)
                        if cutoff < len(top_k_probs):
                            top_k_probs = top_k_probs[:cutoff+1]
                            top_k_probs = top_k_probs / np.sum(top_k_probs)
                            top_k_indices = top_k_indices[:cutoff+1]
                    
                    next_char_idx = np.random.choice(top_k_indices, p=top_k_probs)
                else:
                    # 贪心解码
                    next_char_idx = np.argmax(next_char_probs)
                
                # 检查结束标记
                if next_char_idx == self.vocab.get('<END>', 3):
                    break
                
                # 跳过填充标记
                if next_char_idx != self.vocab.get('<PAD>', 0):
                    output_seq.append(int(next_char_idx))
                    
                    # 更新输入序列（用于下一步预测）
                    if step + 1 < len(current_seq):
                        current_seq[step + 1] = int(next_char_idx)
                    else:
                        # 如果超出当前序列长度，需要扩展
                        current_seq = np.append(current_seq, int(next_char_idx))
                        if len(current_seq) > self.max_length:
                            current_seq = current_seq[:self.max_length]
                    
                    input_text = np.array([current_seq])
        
        except Exception as e:
            print(f"⚠️  生成过程中出错: {e}")
            # 如果生成失败，返回原始文本的简单处理
            return text
        
        # 转换为文本
        result = self.sequence_to_text(output_seq)
        
        # 如果结果为空或太短，返回原始文本
        if not result or len(result) < len(text) * 0.3:
            return text
        
        return result


class TensorFlowAnalyzer:
    """TensorFlow分析器（集成到AI分析器）"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or "models/text_rewriter_model"
        self.rewriter = TensorFlowTextRewriter(model_path=model_path)
        self.style_map = {
            '现代': 0, '古典': 1, '简洁': 2, '华丽': 3,
            '悬疑': 4, '浪漫': 5, '幽默': 6, '严肃': 7,
            '科幻': 8, '武侠': 9, '青春': 10, '都市': 11,
            '古风': 12, '诗化': 13, '口语': 14, '正式': 15,
            '网络': 16, '文艺': 17, '都市幽默': 18
        }
        self.model_loaded = False
    
    def load_model(self) -> bool:
        """加载模型"""
        if self.rewriter.load_vocab() and self.rewriter.load_model():
            self.model_loaded = True
            return True
        return False
    
    def analyze_characters(self, content: str) -> Dict[str, Dict]:
        """分析人物（简化版，使用规则）"""
        # 这里可以使用简单的规则或训练一个分类模型
        return {}
    
    def analyze_storyline(self, content: str) -> Dict:
        """分析故事脉络（简化版）"""
        return {}
    
    def analyze_plot(self, content: str) -> Dict:
        """分析情节结构"""
        return {}
    
    def rewrite_text(self, text: str, style: str, perspective: Optional[str] = None, context: Optional[str] = None) -> str:
        """使用TensorFlow模型改写文本"""
        if not self.model_loaded:
            if not self.load_model():
                print("⚠️  模型未加载，使用简单规则改写")
                return text
        
        # 获取风格ID
        style_id = self.style_map.get(style, 0)
        
        # 分段处理
        if len(text) > 500:
            # 分段处理长文本
            chunks = []
            chunk_size = 500
            for i in range(0, len(text), chunk_size):
                chunk = text[i:i+chunk_size]
                rewritten_chunk = self.rewriter.rewrite(chunk, style_id)
                chunks.append(rewritten_chunk)
            return ''.join(chunks)
        else:
            return self.rewriter.rewrite(text, style_id)

