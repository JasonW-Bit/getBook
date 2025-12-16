#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理器
提供命令行工具来管理配置中心的关键词
"""

import sys
import argparse
from config_center import ConfigCenter


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='配置中心管理工具')
    parser.add_argument('action', choices=['list', 'add', 'remove', 'stats', 'export', 'import'],
                       help='操作类型')
    parser.add_argument('--category', help='类别（personality, emotion, genre, scene, tone）')
    parser.add_argument('--subcategory', help='子类别（如性格类型、情感类型等）')
    parser.add_argument('--keyword', help='关键词')
    parser.add_argument('--file', help='文件路径（用于导入/导出）')
    
    args = parser.parse_args()
    
    config = ConfigCenter()
    
    if args.action == 'list':
        # 列出配置
        if args.category:
            if args.category == 'personality':
                keywords = config.get_personality_keywords()
                if args.subcategory:
                    print(f"\n{args.subcategory} 性格关键词:")
                    for kw in keywords.get(args.subcategory, []):
                        print(f"  - {kw}")
                else:
                    print("\n性格关键词:")
                    for trait, kws in keywords.items():
                        print(f"  {trait}: {len(kws)} 个关键词")
            elif args.category == 'emotion':
                keywords = config.get_emotion_keywords()
                if args.subcategory:
                    print(f"\n{args.subcategory} 情感关键词:")
                    for kw in keywords.get(args.subcategory, []):
                        print(f"  - {kw}")
                else:
                    print("\n情感关键词:")
                    for emotion, kws in keywords.items():
                        print(f"  {emotion}: {len(kws)} 个关键词")
            elif args.category == 'scene':
                keywords = config.get_scene_keywords()
                print(f"\n场景关键词 ({len(keywords)} 个):")
                for kw in keywords:
                    print(f"  - {kw}")
            elif args.category == 'tone':
                keywords = config.get_tone_words()
                print(f"\n语气词 ({len(keywords)} 个):")
                for kw in keywords:
                    print(f"  - {kw}")
        else:
            # 显示统计信息
            stats = config.get_statistics()
            print("\n配置统计:")
            print(f"  性格类型: {stats['personality_traits']} 种")
            print(f"  性格关键词: {stats['personality_keywords_total']} 个")
            print(f"  情感类型: {stats['emotion_types']} 种")
            print(f"  情感关键词: {stats['emotion_keywords_total']} 个")
            print(f"  小说类型: {stats['genres']} 种")
            print(f"  类型关键词: {stats['genre_keywords_total']} 个")
            print(f"  场景关键词: {stats['scene_keywords']} 个")
            print(f"  语气词: {stats['tone_words']} 个")
    
    elif args.action == 'add':
        # 添加关键词
        if not args.category or not args.keyword:
            print("❌ 需要指定 --category 和 --keyword")
            return
        
        if config.add_keyword(args.category, args.keyword, args.subcategory):
            print(f"✅ 已添加关键词: {args.keyword} 到 {args.category}" + 
                  (f"/{args.subcategory}" if args.subcategory else ""))
        else:
            print(f"❌ 添加失败")
    
    elif args.action == 'remove':
        # 移除关键词
        if not args.category or not args.keyword:
            print("❌ 需要指定 --category 和 --keyword")
            return
        
        if config.remove_keyword(args.category, args.keyword, args.subcategory):
            print(f"✅ 已移除关键词: {args.keyword}")
        else:
            print(f"❌ 移除失败")
    
    elif args.action == 'stats':
        # 显示统计信息
        stats = config.get_statistics()
        print("\n配置统计:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    elif args.action == 'export':
        # 导出配置
        output_file = args.file or 'config_export.json'
        config.export_config(output_file)
        print(f"✅ 配置已导出到: {output_file}")
    
    elif args.action == 'import':
        # 导入配置
        input_file = args.file
        if not input_file:
            print("❌ 需要指定 --file")
            return
        
        config.import_config(input_file)
        print(f"✅ 配置已从 {input_file} 导入")


if __name__ == '__main__':
    main()

