# 工作流程问题分析与修复报告

## 问题总结

### 1. 目录结构不匹配问题 ⚠️

#### 问题描述
- **novels目录结构**: `网站/类型/小说名/小说名.txt`
- **processed目录结构**: `类型/小说名.txt`（由DataOrganizer生成）
- **TrainingDataGenerator期望**: `网站/类型/小说名/小说名.txt`

#### 影响
- 当使用processed目录生成训练数据时，生成器无法找到文件
- 导致生成0条样本，训练失败

#### 解决方案
- 让 `TrainingDataGenerator` 支持两种目录结构
- 自动检测目录结构并适配

### 2. 数据流程不清晰 ⚠️

#### 问题描述
- 数据整理后的目录结构与原始结构不一致
- 训练数据生成器无法自动适配
- 需要手动回退到novels目录

#### 解决方案
- 统一目录结构规范
- 或者让生成器支持多种结构

### 3. 错误处理不完善 ⚠️

#### 问题描述
- 当生成0条样本时，没有明确的错误提示
- 没有自动回退机制

#### 解决方案
- 添加样本数量检查
- 自动回退到备用目录

## 完整工作流程

### 阶段1: 数据爬取
```
爬虫 → novels/网站/类型/小说名/小说名.txt
```

**工具**: `scripts/scraper/multi_site_scraper.py`

**输出结构**:
```
data/training/novels/
└── <网站名>/
    └── <类型>/
        └── <小说名>/
            ├── <小说名>.txt
            └── <小说名>.json
```

### 阶段2: 数据整理（可选）
```
novels → processed/类型/小说名.txt
```

**工具**: `scripts/utils/data_organizer.py`

**输出结构**:
```
data/training/processed/
└── <类型>/
    └── <小说名>.txt
```

**注意**: 整理后的结构丢失了网站信息，但简化了目录层级

### 阶段3: 数据分析
```
分析小说特征 → analysis.json
```

**工具**: `scripts/scraper/novel_analyzer.py`

**输出**: 
- `data/training/processed/analysis.json`
- 包含：字符数、章节数、质量评分等

### 阶段4: 训练数据生成
```
小说文本 → 训练样本（文本块 + 改写）
```

**工具**: `scripts/core/training_data_generator.py`

**输入**: 
- 支持 `novels/` 结构（网站/类型/小说名/）
- 支持 `processed/` 结构（类型/小说名.txt）

**处理步骤**:
1. 文本拆分（滑动窗口，保持上下文）
2. 数据增强（同义词替换、回译模拟）
3. 数据集平衡

**输出**:
- `data/training/processed/training_data.txt`
- `data/training/processed/training_stats.json`

### 阶段5: 模型训练
```
训练数据 → TensorFlow模型
```

**工具**: `scripts/ai/models/train_model.py`

**输出**:
- `models/text_rewriter/`
- 检查点文件
- 模型权重

## 修复方案

### 1. 增强TrainingDataGenerator的目录结构适配

```python
def _detect_directory_structure(self, base_dir: str) -> str:
    """
    检测目录结构类型
    
    Returns:
        'novels' 或 'processed'
    """
    # 检查是否有网站层级
    for item in os.listdir(base_dir):
        item_path = os.path.join(base_dir, item)
        if os.path.isdir(item_path):
            # 检查是否是网站目录（包含类型子目录）
            for sub_item in os.listdir(item_path):
                sub_path = os.path.join(item_path, sub_item)
                if os.path.isdir(sub_path):
                    # 检查是否包含txt文件（processed结构）
                    # 或包含小说目录（novels结构）
                    if any(f.endswith('.txt') for f in os.listdir(sub_path)):
                        # 可能是processed结构（类型/小说名.txt）
                        # 或novels结构（类型/小说名/小说名.txt）
                        for novel_item in os.listdir(sub_path):
                            novel_path = os.path.join(sub_path, novel_item)
                            if os.path.isdir(novel_path):
                                return 'novels'
                            elif novel_item.endswith('.txt'):
                                return 'processed'
    return 'unknown'
```

### 2. 支持两种目录结构的文件查找

```python
def _find_novel_files(self, base_dir: str) -> List[Tuple[str, str]]:
    """
    查找所有小说文件
    
    Returns:
        [(文件路径, 小说名), ...]
    """
    structure = self._detect_directory_structure(base_dir)
    files = []
    
    if structure == 'novels':
        # novels结构：网站/类型/小说名/小说名.txt
        for site_name in os.listdir(base_dir):
            site_dir = os.path.join(base_dir, site_name)
            if not os.path.isdir(site_dir):
                continue
            for category in os.listdir(site_dir):
                category_dir = os.path.join(site_dir, category)
                if not os.path.isdir(category_dir):
                    continue
                for novel_name in os.listdir(category_dir):
                    novel_dir = os.path.join(category_dir, novel_name)
                    if not os.path.isdir(novel_dir):
                        continue
                    for file_name in os.listdir(novel_dir):
                        if file_name.endswith('.txt'):
                            files.append((
                                os.path.join(novel_dir, file_name),
                                novel_name
                            ))
    
    elif structure == 'processed':
        # processed结构：类型/小说名.txt
        for category in os.listdir(base_dir):
            category_dir = os.path.join(base_dir, category)
            if not os.path.isdir(category_dir):
                continue
            for file_name in os.listdir(category_dir):
                if file_name.endswith('.txt'):
                    novel_name = file_name[:-4]  # 移除.txt后缀
                    files.append((
                        os.path.join(category_dir, file_name),
                        novel_name
                    ))
    
    return files
```

### 3. 添加样本数量验证和自动回退

```python
def generate_from_novels(self, use_ai: bool = False, enhance: bool = True, 
                        balance: bool = True, fallback_dir: Optional[str] = None) -> str:
    """
    生成训练数据，支持自动回退
    """
    # 尝试从当前目录生成
    samples = self._generate_samples(use_ai, enhance, balance)
    
    # 如果样本数为0且提供了回退目录，尝试回退
    if len(samples) == 0 and fallback_dir and os.path.exists(fallback_dir):
        print(f"   ⚠️  当前目录生成了0条样本，尝试回退到: {fallback_dir}")
        original_dir = self.novels_dir
        self.novels_dir = fallback_dir
        samples = self._generate_samples(use_ai, enhance, balance)
        self.novels_dir = original_dir
    
    if len(samples) == 0:
        print(f"   ❌ 无法生成训练样本，请检查数据目录结构")
        return None
    
    # 保存训练数据
    return self._save_training_data(samples)
```

## 完善后的工作流程

### 推荐流程1: 直接使用novels目录（推荐）

```bash
# 1. 爬取数据
python3 scripts/scraper/multi_site_scraper.py --site m.shuhaige.net --category 都市 --count 10

# 2. 生成训练数据（跳过整理步骤）
python3 scripts/core/pipeline.py --skip scrape,organize --epochs 20

# 3. 训练模型
# （已包含在上一步）
```

**优点**:
- 保持完整的目录结构（包含网站信息）
- 不需要数据整理步骤
- 训练数据生成器原生支持

### 推荐流程2: 使用processed目录（需要修复）

```bash
# 1. 爬取数据
python3 scripts/scraper/multi_site_scraper.py --site m.shuhaige.net --category 都市 --count 10

# 2. 整理数据
python3 scripts/core/pipeline.py --skip scrape --organize

# 3. 生成训练数据（需要修复生成器以支持processed结构）
python3 scripts/core/pipeline.py --skip scrape,organize --epochs 20
```

**优点**:
- 数据已清理和整理
- 目录结构更简洁

**缺点**:
- 丢失网站信息
- 需要修复生成器

## 建议

1. **优先使用novels目录**: 保持完整信息，避免结构转换
2. **修复生成器**: 支持两种目录结构，提高兼容性
3. **添加验证**: 在生成训练数据前验证目录结构
4. **完善错误提示**: 当生成0条样本时，给出明确的错误原因

