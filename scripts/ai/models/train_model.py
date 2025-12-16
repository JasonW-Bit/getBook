#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
训练TensorFlow文本改写模型
"""

import os
import sys
import json
from typing import List, Tuple
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from tensorflow_model import TensorFlowTextRewriter


def prepare_training_data(data_file: str) -> Tuple[List[str], List[str], List[int]]:
    """准备训练数据"""
    print("📚 准备训练数据...")
    
    original_texts = []
    rewritten_texts = []
    styles = []
    
    if os.path.exists(data_file):
        print(f"   从文件加载: {data_file}")
        with open(data_file, 'r', encoding='utf-8') as f:
            line_count = 0
            error_count = 0
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # 支持TSV格式：原始文本<TAB>改写文本<TAB>风格ID<TAB>上下文JSON（可选）
                parts = line.split('\t')
                if len(parts) >= 3:
                    try:
                        # 数据验证：检查原始文本和改写文本长度
                        if len(parts[0].strip()) < 10 or len(parts[1].strip()) < 10:
                            error_count += 1
                            if error_count <= 5:
                                print(f"   ⚠️  第{line_num}行数据过短，跳过")
                            continue
                        
                        # 数据验证：检查风格ID
                        style_id = int(parts[2])
                        if style_id < 0 or style_id > 20:
                            error_count += 1
                            if error_count <= 5:
                                print(f"   ⚠️  第{line_num}行风格ID无效: {style_id}")
                            continue
                        
                        # 解析上下文信息（如果存在）
                        context_info = {}
                        if len(parts) >= 4:
                            try:
                                context_info = json.loads(parts[3])
                            except json.JSONDecodeError:
                                pass  # 上下文解析失败不影响主数据
                        
                        # 数据验证通过，添加到训练数据
                        orig = parts[0].strip()
                        rew = parts[1].strip()
                        style = int(parts[2].strip())
                        context = parts[3].strip() if len(parts) >= 4 else ""  # 可选的上下文
                        
                        # 验证数据（提高最小长度要求）
                        if orig and rew and len(orig) > 50 and len(rew) > 50:  # 从10增加到50
                            # 如果有上下文，可以合并到原始文本（用于训练）
                            if context:
                                # 将上下文信息添加到训练数据中
                                orig = f"[上下文: {context[:200]}] {orig}"  # 限制上下文长度
                            
                            original_texts.append(orig)
                            rewritten_texts.append(rew)
                            styles.append(style)
                            line_count += 1
                        else:
                            error_count += 1
                            if error_count <= 5:  # 只显示前5个错误
                                print(f"   ⚠️  第{line_num}行数据太短，跳过（要求至少50字符）")
                    except (ValueError, IndexError) as e:
                        error_count += 1
                        if error_count <= 5:
                            print(f"   ⚠️  第{line_num}行格式错误，跳过: {e}")
                        continue
            
            if error_count > 5:
                print(f"   ⚠️  还有 {error_count - 5} 行数据被跳过")
        
        print(f"   ✅ 成功加载 {line_count} 条有效数据")
    else:
        print(f"⚠️  训练数据文件不存在: {data_file}")
        print("   将使用示例数据（仅用于测试）")
        # 示例数据
        examples = [
            ("陈旭说：好的，我明白了。", "陈旭在都市的咖啡厅里，轻松地笑着说：好的，我明白了。", 18),  # 都市幽默
            ("他很高兴。", "他超级高兴。", 6),  # 幽默
            ("她走在街上。", "她穿梭在都市的街道上。", 11),  # 都市
            ("今天天气很好。", "今天天气超级棒。", 6),  # 幽默
            ("他在思考问题。", "他在都市的咖啡厅里思考问题。", 11),  # 都市
        ]
        
        for orig, rew, style in examples:
            original_texts.append(orig)
            rewritten_texts.append(rew)
            styles.append(style)
        
        print(f"   使用 {len(examples)} 条示例数据")
    
    if len(original_texts) == 0:
        print("❌ 没有可用的训练数据")
        return [], [], []
    
    # 数据统计
    style_counts = {}
    for style in styles:
        style_counts[style] = style_counts.get(style, 0) + 1
    
    print(f"\n📊 数据统计:")
    print(f"   总数据量: {len(original_texts)}")
    print(f"   风格分布: {dict(sorted(style_counts.items()))}")
    
    return original_texts, rewritten_texts, styles


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("=" * 60)
        print("TensorFlow文本改写模型训练工具")
        print("=" * 60)
        print("\n使用方法:")
        print("  python3 train_model.py <训练数据文件> [选项]")
        print("\n参数:")
        print("  训练数据文件: TSV格式，每行包含 原始文本<TAB>改写文本<TAB>风格ID")
        print("\n选项:")
        print("  --model-path=路径     模型保存路径（默认: models/text_rewriter_model）")
        print("  --epochs=数量         训练轮数（默认: 20）")
        print("  --batch-size=数量     批次大小（默认: 16）")
        print("  --validation-split=比例  验证集比例（默认: 0.2）")
        print("\n示例:")
        print("  python3 train_model.py data/training/training_data.txt")
        print("  python3 train_model.py data/training/training_data.txt --epochs=50 --batch-size=32")
        print("\n数据格式示例:")
        print("  原始文本\\t改写文本\\t风格ID")
        print("  陈旭说：好的。\\t陈旭在都市的咖啡厅里笑着说：好的。\\t18")
        print("\n详细说明请查看: data/training/README.md")
        sys.exit(1)
    
    data_file = sys.argv[1]
    model_path = "models/text_rewriter_model"
    epochs = 20
    batch_size = 16
    validation_split = 0.2
    
    # 解析参数
    for arg in sys.argv[2:]:
        if arg.startswith('--model-path='):
            model_path = arg.split('=')[1]
        elif arg.startswith('--epochs='):
            epochs = int(arg.split('=')[1])
        elif arg.startswith('--batch-size='):
            batch_size = int(arg.split('=')[1])
        elif arg.startswith('--validation-split='):
            validation_split = float(arg.split('=')[1])
    
    print("=" * 60)
    print("开始训练TensorFlow文本改写模型")
    print("=" * 60)
    print(f"\n配置:")
    print(f"  训练数据: {data_file}")
    print(f"  模型路径: {model_path}")
    print(f"  训练轮数: {epochs}")
    print(f"  批次大小: {batch_size}")
    print(f"  验证集比例: {validation_split}")
    print()
    
    # 准备数据
    original_texts, rewritten_texts, styles = prepare_training_data(data_file)
    
    if len(original_texts) == 0:
        print("\n❌ 没有训练数据，退出")
        sys.exit(1)
    
    # 检查数据量
    if len(original_texts) < 10:
        print("\n⚠️  警告: 训练数据量较少，建议至少100条数据以获得较好效果")
        # 非交互模式下自动继续
        if sys.stdin.isatty():
            response = input("是否继续? (y/n): ")
            if response.lower() != 'y':
                sys.exit(0)
        else:
            print("   非交互模式，自动继续训练...")
    
    # 创建改写器
    print("\n" + "=" * 60)
    rewriter = TensorFlowTextRewriter(model_path=model_path)
    
    # 构建词汇表
    print("\n📚 构建词汇表...")
    all_texts = original_texts + rewritten_texts
    rewriter.build_tokenizer(all_texts)
    
    # 构建模型（可配置参数）
    print("\n🏗️  构建模型...")
    # 根据数据量调整模型复杂度和学习率
    if len(original_texts) > 10000:
        num_layers = 4
        num_heads = 8
        learning_rate = 0.0008
    elif len(original_texts) > 1000:
        num_layers = 3
        num_heads = 6
        learning_rate = 0.001
    else:
        num_layers = 2
        num_heads = 4
        learning_rate = 0.002
    
    print(f"   模型配置: {num_layers}层, {num_heads}个注意力头")
    rewriter.build_model(num_layers=num_layers, num_heads=num_heads)
    
    # 训练模型
    print("\n🚀 开始训练...")
    print("=" * 60)
    
    # 如果提供了验证数据文件，使用它
    validation_data_file = data_file.replace('training_data.txt', 'validation_data.txt')
    validation_texts = None
    validation_rewritten = None
    validation_styles = None
    
    if os.path.exists(validation_data_file):
        print(f"   发现验证集文件: {validation_data_file}")
        validation_texts, validation_rewritten, validation_styles = prepare_training_data(validation_data_file)
        validation_split = 0.0  # 使用独立验证集，不使用分割
    
    try:
        history = rewriter.train(
            original_texts=original_texts,
            rewritten_texts=rewritten_texts,
            styles=styles,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            validation_data=(validation_texts, validation_rewritten, validation_styles) if validation_texts else None,
            learning_rate=learning_rate
        )
        
        print("\n" + "=" * 60)
        print("✅ 模型训练完成！")
        print("=" * 60)
        print(f"\n📁 模型文件:")
        print(f"   {model_path}/best_model.h5")
        print(f"   {model_path}/final_model.h5")
        print(f"   {model_path}/vocab.json")
        print(f"\n💡 使用方法:")
        print(f"   python3 scripts/creative/rewrite_novel.py novel.txt \\")
        print(f"     --use-ai --ai-type=tensorflow --style=都市幽默")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  训练被用户中断")
        print("   已保存的模型文件可以使用")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 训练过程中出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

