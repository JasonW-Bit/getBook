# 创意脚本文件夹

这个文件夹用于存放小说改写、创意处理相关的脚本。

## 用途

- 小说改写脚本
- 创意处理工具
- 文本转换工具
- 内容生成工具
- 其他创意相关的脚本

## 文件命名建议

- `rewrite_*.py` - 改写相关脚本
- `creative_*.py` - 创意处理脚本
- `transform_*.py` - 文本转换脚本
- `generate_*.py` - 内容生成脚本

## 已实现的脚本

### 1. 改写脚本 (`rewrite_novel.py`) - 增强版
**功能**：
- 🤖 **AI深度分析**：使用深度学习AI理解小说内容、人物关系、故事脉络
- 📊 **智能分析**：自动提取人物、分析情节结构、识别关键转折点
- ✍️ **风格改写**：支持8种风格（现代/古典/简洁/华丽/悬疑/浪漫/幽默/严肃）
- 👤 **视角转换**：第一人称 ↔ 第三人称
- 🔄 **姓名替换**：自动替换人物姓名
- 📈 **故事脉络分析**：识别开端、发展、高潮、结尾

**使用方法**：
```bash
# 传统方法（快速，免费）
python3 scripts/creative/rewrite_novel.py <输入文件> [选项]

# AI方法（高质量，需要API密钥）
python3 scripts/creative/rewrite_novel.py <输入文件> --use-ai [选项]
```

**示例**：
```bash
# 传统方法：转换为第三人称，简洁风格
python3 scripts/creative/rewrite_novel.py novel.txt --perspective=第三人称 --style=简洁

# AI方法：使用OpenAI进行深度分析和改写
python3 scripts/creative/rewrite_novel.py novel.txt --use-ai --ai-type=openai --style=悬疑

# 替换人物姓名
python3 scripts/creative/rewrite_novel.py novel.txt --replace-names --style=现代
```

**AI配置**：详见 [AI_SETUP.md](AI_SETUP.md)

### 2. 创意处理 (`creative_process.py`)
**功能**：
- 添加创意元素（悬疑、反转、伏笔等）
- 生成新内容（扩展、补充、续写）
- 内容重组（时间顺序/倒序/打乱/主题分组）

**使用方法**：
```bash
python3 scripts/creative/creative_process.py <输入文件> [输出文件] [--action=add_elements/generate/reorganize] [--method=倒序]
```

**示例**：
```bash
# 按倒序重组章节
python3 scripts/creative/creative_process.py novel.txt --action=reorganize --method=倒序
```

### 3. 文本转换 (`transform_format.py`)
**功能**：
- 格式转换（TXT ↔ JSON）
- 编码转换（自动检测并转换）
- 结构重组（章节分离/合并/重新编号）

**使用方法**：
```bash
python3 scripts/creative/transform_format.py <输入文件> [输出文件] [--action=encoding/txt2json/json2txt/restructure]
```

**示例**：
```bash
# TXT转JSON
python3 scripts/creative/transform_format.py novel.txt --action=txt2json

# 转换编码为GBK
python3 scripts/creative/transform_format.py novel.txt --action=encoding --encoding=gbk
```

### 4. 内容生成 (`generate_content.py`)
**功能**：
- 生成新章节（基于现有内容或全新生成）
- 内容扩展（细节/对话/描写/情节）
- 创意生成（冒险/爱情/悬疑/科幻等主题）

**使用方法**：
```bash
python3 scripts/creative/generate_content.py [输入文件] [输出文件] [--action=chapter/expand/creative] [--chapter=10] [--theme=冒险]
```

**示例**：
```bash
# 生成新章节
python3 scripts/creative/generate_content.py novel.txt --action=chapter --chapter=10 --title="新的开始"

# 扩展第5章的内容
python3 scripts/creative/generate_content.py novel.txt --action=expand --chapter=5 --type=细节

# 创意生成（无需输入文件）
python3 scripts/creative/generate_content.py --action=creative --theme=冒险 --length=2000
```

## 注意事项

- 保持脚本的独立性和可复用性
- 添加必要的注释和文档
- 遵循项目的代码规范

