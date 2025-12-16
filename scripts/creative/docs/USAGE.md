# 创意脚本使用指南

## 快速开始

### 1. 改写脚本 (rewrite_novel.py)

**功能**：改写小说风格、转换人称视角、修改语言风格

**基本用法**：
```bash
python3 scripts/creative/rewrite_novel.py <输入文件> [输出文件] [选项]
```

**选项**：
- `--perspective=第一人称/第三人称` - 转换人称视角
- `--style=现代/古典/简洁/华丽` - 修改语言风格

**示例**：
```bash
# 转换为第三人称，简洁风格
python3 scripts/creative/rewrite_novel.py novels/小说标题/小说标题.txt \
  --perspective=第三人称 --style=简洁

# 转换为第一人称，华丽风格
python3 scripts/creative/rewrite_novel.py novel.txt output.txt \
  --perspective=第一人称 --style=华丽
```

---

### 2. 创意处理 (creative_process.py)

**功能**：添加创意元素、生成新内容、内容重组

**基本用法**：
```bash
python3 scripts/creative/creative_process.py <输入文件> [输出文件] [选项]
```

**选项**：
- `--action=add_elements/generate/reorganize` - 处理动作
- `--method=时间顺序/倒序/打乱/主题分组` - 重组方法（用于reorganize）
- `--elements=悬疑,反转,伏笔` - 创意元素（用于add_elements）
- `--chapter=10` - 章节号（用于generate）

**示例**：
```bash
# 按倒序重组章节
python3 scripts/creative/creative_process.py novel.txt \
  --action=reorganize --method=倒序

# 添加创意元素
python3 scripts/creative/creative_process.py novel.txt \
  --action=add_elements --elements=悬疑,反转

# 为第10章生成新内容
python3 scripts/creative/creative_process.py novel.txt \
  --action=generate --chapter=10 --content_type=扩展
```

---

### 3. 文本转换 (transform_format.py)

**功能**：格式转换、编码转换、结构重组

**基本用法**：
```bash
python3 scripts/creative/transform_format.py <输入文件> [输出文件] [选项]
```

**选项**：
- `--action=encoding/txt2json/json2txt/restructure` - 转换动作
- `--encoding=gbk/utf-8` - 目标编码（用于encoding）
- `--structure=章节分离/合并/重新编号` - 重组类型（用于restructure）

**示例**：
```bash
# TXT转JSON
python3 scripts/creative/transform_format.py novel.txt \
  --action=txt2json

# JSON转TXT
python3 scripts/creative/transform_format.py novel.json \
  --action=json2txt

# 转换编码为GBK
python3 scripts/creative/transform_format.py novel.txt \
  --action=encoding --encoding=gbk

# 结构重组
python3 scripts/creative/transform_format.py novel.txt \
  --action=restructure --structure=章节分离
```

---

### 4. 内容生成 (generate_content.py)

**功能**：生成新章节、内容扩展、创意生成

**基本用法**：
```bash
python3 scripts/creative/generate_content.py [输入文件] [输出文件] [选项]
```

**选项**：
- `--action=chapter/expand/creative` - 生成动作
- `--chapter=10` - 章节号（用于chapter和expand）
- `--title="章节标题"` - 章节标题（用于chapter）
- `--style=延续/转折/新起点` - 生成风格（用于chapter）
- `--type=细节/对话/描写/情节` - 扩展类型（用于expand）
- `--theme=冒险/爱情/悬疑/科幻` - 主题（用于creative）
- `--length=2000` - 生成长度（字符数，用于creative）

**示例**：
```bash
# 生成新章节（基于现有小说）
python3 scripts/creative/generate_content.py novel.txt \
  --action=chapter --chapter=10 --title="新的开始" --style=延续

# 扩展第5章的内容
python3 scripts/creative/generate_content.py novel.txt \
  --action=expand --chapter=5 --type=细节

# 创意生成（无需输入文件）
python3 scripts/creative/generate_content.py \
  --action=creative --theme=冒险 --length=2000

# 生成爱情主题的故事
python3 scripts/creative/generate_content.py output.txt \
  --action=creative --theme=爱情 --length=3000
```

---

## 工作流程示例

### 完整的小说处理流程

```bash
# 1. 爬取小说
python3 scripts/novel_scraper.py https://example.com/novel/123

# 2. 改写风格（转换为第三人称，简洁风格）
python3 scripts/creative/rewrite_novel.py \
  novels/小说标题/小说标题.txt \
  --perspective=第三人称 --style=简洁

# 3. 扩展内容（为第1章添加细节）
python3 scripts/creative/generate_content.py \
  novels/小说标题/小说标题.txt \
  --action=expand --chapter=1 --type=细节

# 4. 生成新章节
python3 scripts/creative/generate_content.py \
  novels/小说标题/小说标题.txt \
  --action=chapter --chapter=11 --title="续写章节"

# 5. 转换为JSON格式（便于进一步处理）
python3 scripts/creative/transform_format.py \
  novels/小说标题/小说标题.txt \
  --action=txt2json
```

---

## 注意事项

1. **备份文件**：处理前建议备份原始文件
2. **编码问题**：确保文件使用UTF-8编码，或使用transform_format.py转换
3. **文件路径**：可以使用相对路径或绝对路径
4. **输出文件**：如果不指定输出文件，会自动生成带后缀的文件名

---

## 扩展开发

这些脚本提供了基础框架，可以根据需要扩展：

- 集成AI生成模型（如GPT、Claude等）
- 添加更复杂的文本处理算法
- 实现更智能的内容分析
- 添加批量处理功能

