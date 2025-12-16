# 配置中心文档

## 概述

配置中心（ConfigCenter）是一个动态配置管理系统，用于管理所有关键词、特征、规则等配置。支持从训练分析中自动学习新关键词，不断丰富配置库。

## 功能特性

### 1. 动态配置管理 ✅

- 所有关键词不再硬编码
- 配置文件存储在 `data/config/` 目录
- 支持运行时修改和更新

### 2. 自动学习机制 ✅

- 从分析结果中自动提取新关键词
- 从文本中自动学习关键词
- 自动更新配置文件

### 3. 手动管理 ✅

- 支持手动添加关键词
- 支持移除关键词
- 支持导入/导出配置

## 配置文件

所有配置文件存储在 `data/config/` 目录：

- `personality_keywords.json` - 性格关键词
- `emotion_keywords.json` - 情感关键词
- `genre_keywords.json` - 类型关键词
- `appearance_keywords.json` - 外貌关键词
- `action_keywords.json` - 动作关键词
- `scene_keywords.json` - 场景关键词
- `rhetorical_devices.json` - 修辞手法
- `speaking_style_keywords.json` - 说话风格关键词
- `behavior_patterns.json` - 行为模式
- `tone_words.json` - 语气词

## 使用方法

### 自动学习

配置中心会在以下情况自动学习：

1. **从分析结果学习**
   ```python
   from scripts.core.config_center import ConfigCenter
   from scripts.core.intelligent_analyzer import IntelligentAnalyzer
   
   config = ConfigCenter()
   analyzer = IntelligentAnalyzer(config_center=config)
   
   # 分析小说
   analysis = analyzer.analyze_novel_structure(content)
   
   # 自动学习新关键词
   config.learn_from_analysis(analysis)
   ```

2. **从文本学习**
   ```python
   config = ConfigCenter()
   config.learn_from_text(text, category='都市')
   ```

### 手动管理

#### 添加关键词

```python
from scripts.core.config_center import ConfigCenter

config = ConfigCenter()

# 添加性格关键词
config.add_keyword('personality', '乐观', '开朗')

# 添加情感关键词
config.add_keyword('emotion', '兴奋', '积极')

# 添加场景关键词
config.add_keyword('scene', '咖啡厅')

# 添加语气词
config.add_keyword('tone', '哇')
```

#### 移除关键词

```python
config.remove_keyword('personality', '乐观', '开朗')
config.remove_keyword('scene', '咖啡厅')
```

#### 查看配置

```python
# 获取性格关键词
keywords = config.get_personality_keywords()
print(keywords)

# 获取特定性格类型的关键词
keywords = config.get_personality_keywords('开朗')
print(keywords)

# 获取统计信息
stats = config.get_statistics()
print(stats)
```

### 命令行工具

使用 `config_manager.py` 进行命令行管理：

```bash
# 查看统计信息
python3 scripts/core/config_manager.py stats

# 列出所有性格关键词
python3 scripts/core/config_manager.py list --category personality

# 列出特定性格类型的关键词
python3 scripts/core/config_manager.py list --category personality --subcategory 开朗

# 添加关键词
python3 scripts/core/config_manager.py add --category personality --subcategory 开朗 --keyword 阳光

# 移除关键词
python3 scripts/core/config_manager.py remove --category personality --subcategory 开朗 --keyword 阳光

# 导出配置
python3 scripts/core/config_manager.py export --file config_backup.json

# 导入配置
python3 scripts/core/config_manager.py import --file config_backup.json
```

## 集成到工作流

配置中心已集成到以下模块：

1. **IntelligentAnalyzer** - 使用配置中心的关键词进行分析
2. **DataProcessor** - 在结构化处理时自动学习新关键词
3. **EnhancedTrainingDataGenerator** - 使用配置中心的关键词生成训练数据

## 工作流程

```
1. 爬取数据
   ↓
2. 结构化处理
   - 智能分析（使用配置中心的关键词）
   - 从分析结果中学习新关键词
   - 自动更新配置文件
   ↓
3. 生成训练数据
   - 使用更新后的关键词
   - 更丰富的特征提取
   ↓
4. 训练模型
   - 使用包含丰富特征的训练数据
   - 模型性能提升
```

## 配置格式示例

### personality_keywords.json

```json
{
  "开朗": ["笑", "开心", "快乐", "高兴", "愉快", "活泼", "乐观", "阳光"],
  "内向": ["沉默", "安静", "少言", "内向", "害羞", "腼腆"],
  "勇敢": ["勇敢", "无畏", "大胆", "果断", "坚决", "坚定"]
}
```

### emotion_keywords.json

```json
{
  "积极": ["开心", "高兴", "快乐", "兴奋", "满足", "满意", "喜欢", "爱"],
  "消极": ["难过", "悲伤", "痛苦", "愤怒", "失望", "沮丧", "讨厌", "恨"],
  "紧张": ["紧张", "焦虑", "担心", "害怕", "恐惧", "不安"]
}
```

### scene_keywords.json

```json
["房间", "街道", "学校", "公司", "餐厅", "公园", "医院", "商场", "家", "办公室"]
```

## 优势

1. **动态更新** - 不再需要修改代码，只需更新配置文件
2. **自动学习** - 从训练数据中自动提取新关键词
3. **持续优化** - 关键词库不断丰富，模型性能持续提升
4. **易于管理** - 支持命令行和编程接口
5. **可扩展** - 易于添加新的配置类别

## 注意事项

1. 配置文件使用UTF-8编码
2. 修改配置后会自动保存
3. 建议定期备份配置文件
4. 导入配置会覆盖现有配置

## 相关文件

- `scripts/core/config_center.py` - 配置中心核心模块
- `scripts/core/config_manager.py` - 命令行管理工具
- `data/config/` - 配置文件目录

