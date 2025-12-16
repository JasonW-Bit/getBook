#!/bin/bash
# 完整工作流程执行脚本

cd "$(dirname "$0")/../.."

echo "============================================================"
echo "🚀 开始执行完整工作流程"
echo "============================================================"
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

# 执行完整流程
python3 scripts/core/run_full_workflow.py 2>&1 | tee /tmp/workflow_execution.log

EXIT_CODE=$?

# 检查结果
if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "============================================================"
    echo "✅ 工作流程执行成功！"
    echo "============================================================"
    
    # 显示模型文件
    if [ -f "models/text_rewriter_model/best_model.h5" ]; then
        echo ""
        echo "📁 生成的模型文件:"
        ls -lh models/text_rewriter_model/*.h5 models/text_rewriter_model/*.json 2>/dev/null | awk '{print "   " $9 " (" $5 ")"}'
    fi
else
    echo ""
    echo "============================================================"
    echo "❌ 工作流程执行失败"
    echo "============================================================"
    echo "查看日志: tail -100 /tmp/workflow_execution.log"
fi

exit $EXIT_CODE

