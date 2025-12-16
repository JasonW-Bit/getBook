#!/bin/bash
# 数据整理与训练流水线便捷脚本

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# 切换到项目根目录
cd "$SCRIPT_DIR"

# 检查参数
if [ $# -lt 1 ]; then
    echo "使用方法: ./organize_and_train.sh <数据目录> [选项]"
    echo ""
    echo "参数:"
    echo "  数据目录: 爬取的小说数据目录（如: data/training/novels）"
    echo ""
    echo "选项:"
    echo "  --use-ai              使用AI生成改写样本"
    echo "  --epochs=数量         增量训练轮数（默认: 10）"
    echo "  --learning-rate=值    学习率（默认: 0.0001）"
    echo ""
    echo "示例:"
    echo "  ./organize_and_train.sh data/training/novels"
    echo "  ./organize_and_train.sh data/training/novels --use-ai --epochs=20"
    exit 1
fi

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

# 运行统一流水线（推荐）
echo "🚀 正在启动数据整理与训练流水线..."
echo "💡 提示: 使用统一流水线 scripts/core/pipeline.py"
"$PYTHON_CMD" scripts/core/pipeline.py --organize "$@"

