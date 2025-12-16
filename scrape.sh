#!/bin/bash
# 便捷启动脚本 - 小说爬取工具

# 检查参数
if [ $# -lt 1 ]; then
    echo "使用方法: ./scrape.sh <小说URL> [json]"
    echo "示例: ./scrape.sh https://m.shuhaige.net/350415/"
    exit 1
fi

# 运行爬取脚本
python3 scripts/scraper/novel_scraper.py "$@"

