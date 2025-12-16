#!/bin/bash
# 统一的数据处理流水线入口脚本

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
    echo "❌ 错误: 未找到Python环境。请安装Python 3。"
    exit 1
fi

# 运行统一流水线
"$PYTHON_CMD" scripts/core/pipeline.py "$@"

