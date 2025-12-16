#!/bin/bash
# 清理空文件夹并迁移数据到新结构

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/../.." &> /dev/null && pwd )"

# 切换到项目根目录
cd "$PROJECT_DIR"

echo "🧹 步骤1: 清理空文件夹..."
python3 scripts/utils/cleanup_empty_folders.py data/training/novels --execute

echo ""
echo "🔄 步骤2: 迁移数据到新结构（网站/类型/小说名）..."
python3 scripts/utils/migrate_to_new_structure.py data/training/novels --site m.shuhaige.net --execute

echo ""
echo "🧹 步骤3: 再次清理迁移后的空文件夹..."
python3 scripts/utils/cleanup_empty_folders.py data/training/novels --execute

echo ""
echo "✅ 完成！数据已按新结构组织：网站/类型/小说名/"

