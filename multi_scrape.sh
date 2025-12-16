#!/bin/bash
# 多网站批量爬取便捷脚本（推荐）

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# 切换到项目根目录
cd "$SCRIPT_DIR"

# 检查Python环境
if command -v python3 &> /dev/null
then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null
then
    PYTHON_CMD="python"
else
    echo "错误: 未找到Python环境。请安装Python 3。"
    exit 1
fi

# 解析命令
case "$1" in
    --register|register)
        if [ $# -lt 2 ]; then
            echo "使用方法: ./multi_scrape.sh register <网站URL>"
            echo "示例: ./multi_scrape.sh register https://m.shuhaige.net"
            exit 1
        fi
        "$PYTHON_CMD" scripts/scraper/multi_site_scraper.py --register "$2"
        ;;
    --list|list)
        "$PYTHON_CMD" scripts/scraper/multi_site_scraper.py --list-sites
        ;;
    --scrape|scrape)
        if [ $# -lt 4 ]; then
            echo "使用方法: ./multi_scrape.sh scrape <网站名> <类型> <数量> [选项]"
            echo ""
            echo "参数:"
            echo "  网站名: 已注册的网站名称（如：m.shuhaige.net）"
            echo "  类型: 小说类型（都市、玄幻、言情等）"
            echo "  数量: 爬取数量"
            echo ""
            echo "选项:"
            echo "  --no-filter-completed  不筛选，爬取所有小说"
            echo "  --generate-data        生成训练数据"
            echo ""
            echo "示例:"
            echo "  ./multi_scrape.sh scrape m.shuhaige.net 都市 10"
            echo "  ./multi_scrape.sh scrape m.shuhaige.net 都市 10 --generate-data"
            exit 1
        fi
        SITE="$2"
        CATEGORY="$3"
        COUNT="$4"
        shift 4
        "$PYTHON_CMD" scripts/scraper/multi_site_scraper.py \
            --site "$SITE" \
            --category "$CATEGORY" \
            --count "$COUNT" \
            "$@"
        ;;
    *)
        echo "多网站批量爬取工具"
        echo ""
        echo "使用方法:"
        echo "  ./multi_scrape.sh <命令> [参数]"
        echo ""
        echo "命令:"
        echo "  register <URL>        注册新网站"
        echo "  list                  列出已注册的网站"
        echo "  scrape <网站> <类型> <数量> [选项]  爬取小说"
        echo ""
        echo "示例:"
        echo "  ./multi_scrape.sh register https://m.shuhaige.net"
        echo "  ./multi_scrape.sh list"
        echo "  ./multi_scrape.sh scrape m.shuhaige.net 都市 10"
        exit 1
        ;;
esac

