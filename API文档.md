# FiChara API 文档

完整的 API 参考文档，包含所有模块、类和函数的详细说明。

---

## 📑 目录

- [安装](#安装)
- [快速开始](#快速开始)
- [核心模块](#核心模块)
  - [png_handler](#png_handler---png-处理)
  - [models](#models---数据模型)
  - [validator](#validator---数据验证)
  - [exporter](#exporter---导出工具)
  - [lorebook_handler](#lorebook_handler---独立世界书)
  - [lorebook_manager](#lorebook_manager---世界书管理)
  - [variable_replacer](#variable_replacer---变量替换)
  - [prompt_builder](#prompt_builder---提示词构建)

---

## 🚀 安装

```bash
pip install Pillow pydantic
```

```python
# 导入 FiChara
from fichara import *
```

---

## ⚡ 快速开始

### 基础示例

```python
from fichara import load_card_data, parse_character_card

# 1. 加载角色卡
card_data = load_card_data("character.png")

# 2. 解析为对象
card = parse_character_card(card_data)

# 3. 访问数据
print(f"角色名: {card.name}")
print(f"描述: {card.description}")
```

---

## 📦 核心模块

---

## png_handler - PNG 处理

处理 PNG 图片中的角色卡元数据。

### 函数

#### `load_card_data(image_path: str) -> dict`

从 PNG 图片中读取角色卡数据。

**参数：**

- `image_path` (str): PNG 图片路径

**返回：**

- `dict`: 角色卡数据字典

**异常：**

- `ValueError`: 图片中未找到角色卡数据
- `FileNotFoundError`: 文件不存在

**示例：**

```python
from fichara import load_card_data

# 读取角色卡
card_data = load_card_data("character.png")

# 访问数据
print(card_data['name'])
print(card_data['description'])
```

---

#### `save_card_data(image_path: str, output_path: str, card_data: dict)`

将角色卡数据写入 PNG 图片。

**参数：**

- `image_path` (str): 源图片路径
- `output_path` (str): 输出图片路径
- `card_data` (dict): 角色卡数据

**异常：**

- `FileNotFoundError`: 源图片不存在
- `IOError`: 写入失败

**示例：**

```python
from fichara import load_card_data, save_card_data

# 读取
card_data = load_card_data("original.png")

# 修改
card_data['name'] = "新名字"

# 保存
save_card_data("original.png", "modified.png", card_data)
```

---

## models - 数据模型

定义角色卡的数据结构。

### 类

#### `CharacterCardV2`

SillyTavern V2 格式角色卡。

**属性：**

| 属性                          | 类型            | 说明                     |
| --------------------------- | ------------- | ---------------------- |
| `spec`                      | str           | 格式标识 ("chara_card_v2") |
| `spec_version`              | str           | 版本号 ("2.0")            |
| `name`                      | str           | 角色名称                   |
| `description`               | str           | 角色描述                   |
| `personality`               | str           | 角色性格                   |
| `scenario`                  | str           | 情���设定                 |
| `first_mes`                 | str           | 第一条消息                  |
| `mes_example`               | str           | 对话示例                   |
| `creator_notes`             | str           | 作者注释                   |
| `system_prompt`             | str           | 系统提示词                  |
| `post_history_instructions` | str           | 历史后指令                  |
| `alternate_greetings`       | List[str]     | 额外开场白                  |
| `character_book`            | CharacterBook | 世界书                    |
| `tags`                      | List[str]     | 标签                     |
| `creator`                   | str           | 作者名                    |
| `character_version`         | str           | 角色版本                   |
| `extensions`                | dict          | 扩展字段                   |

**示例：**

```python
from fichara import CharacterCardV2

# 创建 V2 角色卡
card = CharacterCardV2(
    name="小明",
    description="一个友好的AI助手",
    personality="热情、乐于助人",
    scenario="在图书馆相遇",
    first_mes="你好！我是小明！",
    tags=["助手", "友好"]
)

# 访问属性
print(card.name)
print(card.description)
```

---

#### `CharacterCardV3`

SillyTavern V3 格式角色卡。

**属性：**

| 属性             | 类型              | 说明                     |
| -------------- | --------------- | ---------------------- |
| `spec`         | str             | 格式标识 ("chara_card_v3") |
| `spec_version` | str             | 版本号 ("3.0")            |
| `name`         | str             | 角色名称                   |
| `description`  | str             | 角色描述                   |
| `personality`  | str             | 角色性格                   |
| `scenario`     | str             | 情景设定                   |
| `first_mes`    | str             | 第一条消息                  |
| `mes_example`  | str             | 对话示例                   |
| `data`         | CharacterDataV3 | V3 数据对象                |
| `tags`         | List[str]       | 标签                     |
| `create_date`  | str             | 创建日期                   |

**V3 特有字段（在 data 中）：**

- `system_prompt`: 系统提示词
- `post_history_instructions`: 历史后指令
- `alternate_greetings`: 额外开场白
- `group_only_greetings`: 群聊专用开场白
- `character_book`: 世界书
- `extensions`: 扩展字段

**示例：**

```python
from fichara import CharacterCardV3, CharacterDataV3

# 创建 V3 角色卡
card = CharacterCardV3(
    name="小红",
    description="一个聪明的学生",
    data=CharacterDataV3(
        name="小红",
        description="一个聪明的学生",
        personality="好奇、爱学习",
        scenario="在教室里",
        first_mes="你好！",
        system_prompt="You are a helpful student.",
        tags=["学生", "聪明"]
    )
)
```

---

#### `WorldBookEntry`

世界书条目。

**属性：**

| 属性                | 类型                       | 说明       |
| ----------------- | ------------------------ | -------- |
| `id`              | int                      | 条目 ID    |
| `keys`            | List[str]                | 主关键词     |
| `secondary_keys`  | List[str]                | 次要关键词    |
| `comment`         | str                      | 注释       |
| `content`         | str                      | 内容       |
| `constant`        | bool                     | 是否常驻（蓝灯） |
| `selective`       | bool                     | 是否选择性触发  |
| `enabled`         | bool                     | 是否启用     |
| `insertion_order` | int                      | 插入顺序     |
| `position`        | str                      | 插入位置     |
| `use_regex`       | bool                     | 是否使用正则   |
| `extensions`      | WorldBookEntryExtensions | 扩展字段     |

**示例：**

```python
from fichara import WorldBookEntry, WorldBookEntryExtensions

# 创建世界书条目
entry = WorldBookEntry(
    id=0,
    keys=["魔法", "法术"],
    comment="魔法系统",
    content="这个世界有强大的魔法系统...",
    constant=False,  # 绿灯（关键词触发）
    position="before_char",
    extensions=WorldBookEntryExtensions(
        depth=4,
        probability=100
    )
)
```

---

#### `CharacterBook`

角色世界书。

**属性：**

| 属性                   | 类型                   | 说明       |
| -------------------- | -------------------- | -------- |
| `name`               | str                  | 世界书名称    |
| `description`        | str                  | 描述       |
| `scan_depth`         | int                  | 扫描深度     |
| `token_budget`       | int                  | Token 预算 |
| `recursive_scanning` | bool                 | 递归扫描     |
| `entries`            | List[WorldBookEntry] | 条目列表     |

**示例：**

```python
from fichara import CharacterBook, WorldBookEntry

# 创建世界书
lorebook = CharacterBook(
    name="奇幻世界",
    description="一个充满魔法的世界",
    entries=[
        WorldBookEntry(
            id=0,
            keys=["魔法"],
            content="魔法系统说明..."
        ),
        WorldBookEntry(
            id=1,
            keys=["龙"],
            content="龙的设定..."
        )
    ]
)

# 访问条目
for entry in lorebook.entries:
    print(f"{entry.comment}: {entry.content}")
```

---

### 函数

#### `parse_character_card(data: dict) -> CharacterCardV2 | CharacterCardV3`

智能解析角色卡数据。

**参数：**

- `data` (dict): 角色卡数据字典

**返回：**

- `CharacterCardV2` 或 `CharacterCardV3`: 解析后的角色卡对象

**示例：**

```python
from fichara import load_card_data, parse_character_card

# 加载并解析
card_data = load_card_data("character.png")
card = parse_character_card(card_data)

# 检查版本
if isinstance(card, CharacterCardV3):
    print("这是 V3 格式")
    print(card.data.system_prompt)
else:
    print("这是 V2 格式")
    print(card.system_prompt)
```

---

## validator - 数据验证

验证和修复角色卡数据。

### 类

#### `ValidationError`

验证错误信息。

**属性：**

- `level` (str): 错误级别 ("error" 或 "warning")
- `field` (str): 出错字段
- `message` (str): 错误描述

---

#### `CharacterCardValidator`

角色卡验证器。

### 方法

#### `validate(card) -> Tuple[bool, List[ValidationError]]`

验证角色卡。

**参数：**

- `card`: 角色卡对象

**返回：**

- `bool`: 是否通过验证
- `List[ValidationError]`: 错误列表

**示例：**

```python
from fichara import CharacterCardValidator, load_card_data, parse_character_card

# 加载角色卡
card_data = load_card_data("character.png")
card = parse_character_card(card_data)

# 验证
is_valid, errors = CharacterCardValidator.validate(card)

if is_valid:
    print("✅ 验证通过！")
else:
    print(f"❌ 发现 {len(errors)} 个问题：")
    for error in errors:
        print(f"  {error}")
```

---

#### `auto_fix(card) -> card`

自动修复常见问题。

**参数：**

- `card`: 角色卡对象

**返回：**

- 修复后的角色卡对象

**示例：**

```python
from fichara import CharacterCardValidator

# 验证
is_valid, errors = CharacterCardValidator.validate(card)

# 如果有问题，自动修复
if not is_valid:
    print("正在修复...")
    fixed_card = CharacterCardValidator.auto_fix(card)

    # 再次验证
    is_valid_after, errors_after = CharacterCardValidator.validate(fixed_card)
    print(f"修复后: {'✅ 通过' if is_valid_after else '❌ 仍有问题'}")
```

---

## exporter - 导出工具

导出角色卡为多种格式。

### 类

#### `CharacterCardExporter`

角色卡导出器。

### 方法

#### `to_json(card, output_path: str, indent: int = 2)`

导出为 JSON 文件。

**参数：**

- `card`: 角色卡对象
- `output_path` (str): 输出路径
- `indent` (int): 缩进空格数

**示例：**

```python
from fichara import CharacterCardExporter

# 导出为 JSON
CharacterCardExporter.to_json(card, "output.json")

# 自定义缩进
CharacterCardExporter.to_json(card, "output.json", indent=4)
```

---

#### `to_markdown(card) -> str`

导出为 Markdown 格式。

**参数：**

- `card`: 角色卡对象

**返回：**

- `str`: Markdown 文本

**示例：**

```python
from fichara import CharacterCardExporter

# 生成 Markdown
markdown = CharacterCardExporter.to_markdown(card)
print(markdown)

# 保存为文件
with open("output.md", "w", encoding="utf-8") as f:
    f.write(markdown)
```

---

#### `save_markdown(card, output_path: str)`

保存为 Markdown 文件。

**参数：**

- `card`: 角色卡对象
- `output_path` (str): 输出路径

**示例：**

```python
from fichara import CharacterCardExporter

CharacterCardExporter.save_markdown(card, "character.md")
```

---

#### `to_png(card, image_path: str, output_path: str)`

将角色卡写入 PNG 图片。

**参数：**

- `card`: 角色卡对象
- `image_path` (str): 源图片路径
- `output_path` (str): 输出路径

**示例：**

```python
from fichara import CharacterCardExporter

# 修改角色卡后保存
card.name = "新名字"
CharacterCardExporter.to_png(card, "original.png", "modified.png")
```

---

#### `change_image(original_png: str, new_image: str, output_path: str)`

更换角色卡图片（保留数据）。

**参数：**

- `original_png` (str): 原角色卡 PNG
- `new_image` (str): 新图片
- `output_path` (str): 输出路径

**示例：**

```python
from fichara import CharacterCardExporter

# 只换图片，保留数据
CharacterCardExporter.change_image(
    "old_card.png",
    "new_beautiful_image.png",
    "updated_card.png"
)
```

---

#### `from_json_to_png(json_path: str, image_path: str, output_path: str)`

从 JSON 创建 PNG 角色卡。

**参数：**

- `json_path` (str): JSON 文件路径
- `image_path` (str): 图片路径
- `output_path` (str): 输出路径

**示例：**

```python
from fichara import CharacterCardExporter

# 从 JSON 备份恢复
CharacterCardExporter.from_json_to_png(
    "backup.json",
    "image.png",
    "restored.png"
)
```

---

#### `create_default_image(output_path: str, width: int = 512, height: int = 512)`

创建默认占位图片。

**参数：**

- `output_path` (str): 输出路径
- `width` (int): 宽度
- `height` (int): 高度

**返回：**

- `str`: 图片路径

**示例：**

```python
from fichara import CharacterCardExporter

# 创建占位图
img_path = CharacterCardExporter.create_default_image("placeholder.png")
```

---

## lorebook_handler - 独立世界书

处理 SillyTavern 独立导出的世界书。

### 类

#### `LorebookHandler`

独立世界书处理器。

### 方法

#### `load_standalone_lorebook(json_path: str) -> CharacterBook`

加载独立世界书 JSON。

**参数：**

- `json_path` (str): JSON 文件路径

**返回：**

- `CharacterBook`: 世界书对象

**示例：**

```python
from fichara import LorebookHandler

# 加载独立世界书
lorebook = LorebookHandler.load_standalone_lorebook("world.json")

print(f"世界书: {lorebook.name}")
print(f"条目数: {len(lorebook.entries)}")
```

---

#### `save_standalone_lorebook(book: CharacterBook, output_path: str)`

保存为独立世界书格式。

**参数：**

- `book` (CharacterBook): 世界书对象
- `output_path` (str): 输出路径

**示例：**

```python
from fichara import LorebookHandler

# 保存为独立格式
LorebookHandler.save_standalone_lorebook(lorebook, "exported.json")
```

---

#### `merge_into_character(book: CharacterBook, card_book: CharacterBook, strategy: str = "keep_both") -> int`

合并世界书到角色卡。

**参数：**

- `book` (CharacterBook): 要合并的世界书
- `card_book` (CharacterBook): 角色卡的世界书
- `strategy` (str): 合并策略
  - `"keep_both"`: 保留两者（重新分配 ID）
  - `"keep_original"`: 保留原有的
  - `"keep_new"`: 使用新的覆盖

**返回：**

- `int`: 新增的条目数

**示例：**

```python
from fichara import LorebookHandler, load_card_data, parse_character_card

# 加载独立世界书
standalone = LorebookHandler.load_standalone_lorebook("world.json")

# 加载角色卡
card_data = load_card_data("character.png")
card = parse_character_card(card_data)

# 合并
added = LorebookHandler.merge_into_character(
    standalone,
    card.data.character_book,
    strategy="keep_both"
)

print(f"新增 {added} 个条目")
```

---

## lorebook_manager - 世界书管理

强大的世界书管理工具。

### 类

#### `LorebookManager`

世界书管理器。

**初始化：**

```python
from fichara import LorebookManager

manager = LorebookManager(character_book)
```

### 方法

#### 基础操作

##### `add_entry(entry: WorldBookEntry) -> int`

添加条目。

**返回：**

- `int`: 新条目的 ID

**示例：**

```python
from fichara import LorebookManager, WorldBookEntry

manager = LorebookManager(lorebook)

# 创建新条目
new_entry = WorldBookEntry(
    id=None,  # 自动分配
    keys=["魔法", "法术"],
    comment="魔法系统",
    content="详细的魔法设定..."
)

# 添加
entry_id = manager.add_entry(new_entry)
print(f"新条目 ID: {entry_id}")
```

---

##### `remove_entry(entry_id: int) -> bool`

删除条目。

**返回：**

- `bool`: 是否成功

**示例：**

```python
# 删除条目
success = manager.remove_entry(5)
if success:
    print("删除成功")
```

---

##### `get_entry(entry_id: int) -> Optional[WorldBookEntry]`

获取条目。

**返回：**

- `WorldBookEntry` 或 `None`

**示例：**

```python
# 获取条目
entry = manager.get_entry(3)
if entry:
    print(f"找到: {entry.comment}")
```

---

##### `update_entry(entry_id: int, **kwargs) -> bool`

更新条目。

**参数：**

- `entry_id` (int): 条目 ID
- `**kwargs`: 要更新的字段

**返回：**

- `bool`: 是否成功

**示例：**

```python
# 更新条目
manager.update_entry(
    3,
    content="新内容",
    keys=["新关键词"],
    depth=5
)
```

---

##### `duplicate_entry(entry_id: int) -> Optional[int]`

复制条目。

**返回：**

- `int`: 新条目 ID，失败返回 None

**示例：**

```python
# 复制条目
new_id = manager.duplicate_entry(3)
print(f"复制后的新 ID: {new_id}")
```

---

#### 查询功能

##### `find_by_keyword(keyword: str, case_sensitive: bool = False) -> List[WorldBookEntry]`

根据关键词查找。

**示例：**

```python
# 查找包含"魔法"的条目
results = manager.find_by_keyword("魔法")
print(f"找到 {len(results)} 个条目")

for entry in results:
    print(f"- {entry.comment}")
```

---

##### `find_by_type(entry_type: str) -> List[WorldBookEntry]`

根据类型查找。

**参数：**

- `entry_type` (str): "green"（关键词）、"blue"（常驻）、"vector"（向量）

**示例：**

```python
# 查找所有蓝灯条目
blue_entries = manager.find_by_type("blue")
print(f"蓝灯条目: {len(blue_entries)} 个")

# 查找所有绿灯条目
green_entries = manager.find_by_type("green")
print(f"绿灯条目: {len(green_entries)} 个")
```

---

##### `find_by_position(position: int) -> List[WorldBookEntry]`

根据插入位置查找。

**示例：**

```python
# 查找"角色定义之前"的条目
before_char = manager.find_by_position(0)
```

---

##### `find_by_role(role: int) -> List[WorldBookEntry]`

根据角色类型查找。

**参数：**

- `role` (int): 0=System, 1=User, 2=Assistant

**示例：**

```python
# 查找系统角色的条目
system_entries = manager.find_by_role(0)
```

---

##### `find_by_depth(min_depth: int = None, max_depth: int = None) -> List[WorldBookEntry]`

根据深度范围查找。

**示例：**

```python
# 查找深度 4-6 的条目
entries = manager.find_by_depth(4, 6)
```

---

##### `find_empty_entries() -> List[WorldBookEntry]`

查找空内容条目。

**示例：**

```python
# 查找空条目
empty = manager.find_empty_entries()
if empty:
    print(f"⚠️ 发现 {len(empty)} 个空条目")
```

---

##### `find_no_keywords_entries() -> List[WorldBookEntry]`

查找没有关键词的绿灯条目。

**示例：**

```python
# 查找问题条目
no_kw = manager.find_no_keywords_entries()
if no_kw:
    print(f"⚠️ {len(no_kw)} 个绿灯条目没有关键词")
```

---

##### `find_by_filter(filter_func) -> List[WorldBookEntry]`

自定义过滤。

**参数：**

- `filter_func`: 过滤函数，接受 WorldBookEntry，返回 bool

**示例：**

```python
# 查找深度大于 5 且已启用的条目
results = manager.find_by_filter(
    lambda e: e.extensions.depth > 5 and e.enabled
)

# 查找包含特定关键词的蓝灯条目
results = manager.find_by_filter(
    lambda e: e.constant and "魔法" in e.keys
)
```

---

#### 批量操作

##### `batch_update(entry_ids: List[int], **kwargs) -> int`

批量更新。

**示例：**

```python
# 批量修改深度
manager.batch_update([1, 2, 3], depth=5)

# 批量禁用
manager.batch_update([4, 5, 6], enabled=False)
```

---

##### `batch_delete(entry_ids: List[int]) -> int`

批量删除。

**示例：**

```python
# 删除多个条目
deleted = manager.batch_delete([7, 8, 9])
print(f"删除了 {deleted} 个条目")
```

---

##### `enable_all()` / `disable_all()`

启用/禁用所有条目。

**示例：**

```python
# 禁用所有
manager.disable_all()

# 启用所有
manager.enable_all()
```

---

##### `enable_by_type(entry_type: str)` / `disable_by_type(entry_type: str)`

按类型启用/禁用。

**示例：**

```python
# 只启用蓝灯条目
manager.disable_all()
manager.enable_by_type("blue")

# 禁用所有绿灯条目
manager.disable_by_type("green")
```

---

#### 排序功能

##### `sort_entries(by: str = "display_index", reverse: bool = False)`

排序条目。

**参数：**

- `by` (str): 排序依据
  - `"id"`: 按 ID
  - `"display_index"`: 按显示顺序
  - `"insertion_order"`: 按插入顺序
  - `"depth"`: 按深度
  - `"comment"`: 按注释
- `reverse` (bool): 是否倒序

**示例：**

```python
# 按深度排序
manager.sort_entries(by="depth")

# 按 ID 倒序
manager.sort_entries(by="id", reverse=True)
```

---

##### `reindex_display_order()`

重新分配显示顺序。

**示例：**

```python
# 重新编号（0, 1, 2, ...）
manager.reindex_display_order()
```

---

#### 合并功能

##### `merge_with(other_book: CharacterBook, conflict_strategy: str = "keep_both") -> int`

合并另一个世界书。

**参数：**

- `other_book` (CharacterBook): 要合并的世界书
- `conflict_strategy` (str): 冲突策略

**返回：**

- `int`: 新增条目数

**示例：**

```python
# 加载另一个世界书
other = LorebookHandler.load_standalone_lorebook("other.json")

# 合并
added = manager.merge_with(other, strategy="keep_both")
print(f"合并了 {added} 个新条目")
```

---

#### 统计功能

##### `get_statistics() -> Dict`

获取统计信息。

**返回：**

- `dict`: 统计数据

**示例：**

```python
stats = manager.get_statistics()

print(f"总条目: {stats['total']}")
print(f"绿灯: {stats['by_type']['green']}")
print(f"蓝灯: {stats['by_type']['blue']}")
print(f"向量: {stats['by_type']['vector']}")
print(f"已启用: {stats['by_status']['enabled']}")
print(f"空条目: {stats['issues']['empty_entries']}")
```

---

##### `print_statistics()`

打印统计信息。

**示例：**

```python
# 打印详细统计
manager.print_statistics()
```

输出：

```
==================================================
📚 世界书统计信息
==================================================

📊 总条目数: 25

🎨 按类型:
  🟢 关键词触发: 18
  🔵 常驻触发: 5
  🔗 向量触发: 2

⚡ 按状态:
  ✅ 已启用: 23
  ❌ 已禁用: 2

...
==================================================
```

---

##### `export_summary() -> str`

导出简要摘要。

**示例：**

```python
summary = manager.export_summary()
print(summary)
# 输出: "世界书: 奇幻世界 | 总条目: 25 (🟢18 🔵5 🔗2) | 状态: ✅23 ❌2"
```

---

#### 辅助方法

##### `create_entry(...) -> WorldBookEntry`

快速创建条目。

```markdown
**参数：**
- `comment` (str): 注释
- `content` (str): 内容
- `keys` (List[str]): 关键词列表
- `entry_type` (str): 类型 ("green", "blue", "vector")
- `position` (str): 插入位置 ("before_char", "after_char")
- `depth` (int): 深度
- `role` (int): 角��类型 (0=System, 1=User, 2=Assistant)

**返回：**
- `WorldBookEntry`: 新创建的条目

**示例：**

```python
# 快速创建绿灯条目
entry = manager.create_entry(
    comment="魔法系统",
    content="这个世界有强大的魔法...",
    keys=["魔法", "法术"],
    entry_type="green",
    position="before_char",
    depth=4
)

# 添加到世界书
manager.add_entry(entry)
```

---

##### `clear_all()`

清空所有条目（危险操作）。

**示例：**

```python
# 清空世界书
manager.clear_all()
```

---

## variable_replacer - 变量替换

灵活的变量替换系统，支持宏套宏。

### 类

#### `VariableReplacer`

变量替换器。

**初始化：**

```python
from fichara import VariableReplacer

replacer = VariableReplacer(
    user_name="Alice",
    char_name="小明"
)
```

### 内置变量

| 变量             | 说明         | 示例                  |
| -------------- | ---------- | ------------------- |
| `{{user}}`     | 用户名        | Alice               |
| `{{char}}`     | 角色名        | 小明                  |
| `{{time}}`     | 当前时间       | 14:30               |
| `{{date}}`     | 当前日期       | 2025-01-16          |
| `{{datetime}}` | 日期时间       | 2025-01-16 14:30:00 |
| `{{random}}`   | 随机数(1-100) | 42                  |
| `{{newline}}`  | 换行符        | \n                  |

### 方法

#### `register_variable(var_name: str, callback: Callable)`

注册自定义变量。

**参数：**

- `var_name` (str): 变量名（不含 {{}}）
- `callback` (Callable): 回调函数，接受上下文字典，返回字符串

**示例：**

```python
from fichara import VariableReplacer

replacer = VariableReplacer(user_name="Alice", char_name="Bob")

# 简单变量
replacer.register_variable("weather", lambda ctx: "sunny")

# 使用上下文的变量
replacer.register_variable(
    "location",
    lambda ctx: ctx.get("current_location", "unknown")
)

# 复杂逻辑
def get_greeting(ctx):
    from datetime import datetime
    hour = datetime.now().hour
    if hour < 12:
        return "早上好"
    elif hour < 18:
        return "下午好"
    else:
        return "晚上好"

replacer.register_variable("greeting", get_greeting)
```

---

#### `unregister_variable(var_name: str)`

注销变量。

**示例：**

```python
replacer.unregister_variable("weather")
```

---

#### `replace(text: str, context: Optional[Dict] = None) -> str`

替换文本中的变量。

**参数：**

- `text` (str): 原始文本
- `context` (dict): 上下文字典（可选）

**返回：**

- `str`: 替换后的文本

**示例：**

```python
# 基础替换
text = "你好，{{user}}！我是{{char}}。"
result = replacer.replace(text)
# 输出: "你好，Alice！我是Bob。"

# 使用上下文
text = "你在{{location}}，天气{{weather}}。"
result = replacer.replace(text, context={
    "location": "图书馆",
    "weather": "晴朗"
})
# 输出: "你在图书馆，天气晴朗。"
```

---

#### `list_variables()`

列出所有已注册的变量。

**示例：**

```python
replacer.list_variables()
```

输出：

```
============================================================
📋 已注册的变量
============================================================

🔧 内置变量:
  {{char}}
  {{date}}
  {{datetime}}
  {{random}}
  {{time}}
  {{user}}

✏️ 自定义变量:
  {{greeting}}
  {{location}}
  {{weather}}
============================================================
```

---

#### `test_variable(var_name: str, context: Optional[Dict] = None)`

测试单个变量。

**示例：**

```python
# 测试变量
replacer.test_variable("user")
# 输出: {{user}} = Alice

replacer.test_variable("location", context={"location": "咖啡厅"})
# 输出: {{location}} = 咖啡厅
```

---

### 宏套宏示例

```python
from fichara import VariableReplacer

replacer = VariableReplacer(user_name="Alice", char_name="Bob")

# 注册嵌套变量
replacer.register_variable("name", lambda ctx: "{{user}}")
replacer.register_variable("greeting", lambda ctx: "Hello, {{name}}!")
replacer.register_variable("message", lambda ctx: "{{greeting}} How are you?")

# 替换（会递归展开）
text = "{{message}}"
result = replacer.replace(text)
# 第1次: "{{greeting}} How are you?"
# 第2次: "Hello, {{name}}! How are you?"
# 第3次: "Hello, {{user}}! How are you?"
# 第4次: "Hello, Alice! How are you?"
print(result)
# 输出: "Hello, Alice! How are you?"
```

---

## prompt_builder - 提示词构建

专业的提示词组装器，支持角色分离和变量替换。

### 类

#### `Message`

消息对象。

**属性：**

- `role` (str): 角色 ("system", "user", "assistant")
- `content` (str): 内容
- `name` (str): 可选的名称字段

---

#### `PromptBuilder`

提示词构建器。

**初始化：**

```python
from fichara import PromptBuilder

builder = PromptBuilder(
    card=card,                              # 角色卡对象
    main_prompt=None,                       # 自定义主提示词（可选）
    enhance_definitions=None,               # 自定义增强定义（可选）
    auxiliary_prompt=None,                  # 自定义辅助提示词（可选）
    post_history_instructions=None,         # 自定义历史后指令（可选）
    persona_description="",                 # 用户人设描述
    user_name="User",                       # 用户名
    enable_variable_replacement=True,       # 是否启用变量替换
    max_variable_depth=5                    # 最大变量嵌套深度
)
```

**参数说明：**

| 参数                            | 类型            | 说明                              |
| ----------------------------- | ------------- | ------------------------------- |
| `card`                        | CharacterCard | 角色卡对象（必需）                       |
| `main_prompt`                 | str           | 主提示词（None=使用角色卡的 system_prompt） |
| `enhance_definitions`         | str           | 增强定义（可自定义）                      |
| `auxiliary_prompt`            | str           | 辅助提示词（可自定义）                     |
| `post_history_instructions`   | str           | 历史后指令（None=使用角色卡的）              |
| `persona_description`         | str           | 用户人设描述                          |
| `user_name`                   | str           | 用户名（用于变量替换）                     |
| `enable_variable_replacement` | bool          | 是否启用变量替换                        |
| `max_variable_depth`          | int           | 最大变量嵌套深度（防止无限递归）                |

---

### 方法

#### `register_variable(var_name: str, callback: Callable)`

注册自定义变量。

**示例：**

```python
# 注册变量
builder.register_variable("weather", lambda ctx: "sunny")
builder.register_variable("mood", lambda ctx: "happy")
```

---

#### `build_messages(chat_history, user_message, ...) -> List[Message]`

构建消息列表（Message 对象）。

**参数：**

- `chat_history` (List[Dict]): 聊天历史
- `user_message` (str): 当前用户消息
- `include_world_info` (bool): 是否包含世界书
- `include_examples` (bool): 是否包含对话示例
- `max_history_messages` (int): 最大历史消息数

**返回：**

- `List[Message]`: 消息对象列表

**示例：**

```python
from fichara import PromptBuilder

builder = PromptBuilder(card=card, user_name="Alice")

# 构建消息
messages = builder.build_messages(
    chat_history=[
        {"role": "user", "content": "你好！"},
        {"role": "assistant", "content": "你好呀！"}
    ],
    user_message="介绍一下你自己",
    include_world_info=True,
    include_examples=True,
    max_history_messages=20
)

# 访问消息
for msg in messages:
    print(f"{msg.role}: {msg.content}")
```

---

#### `build_messages_dict(...) -> List[Dict[str, str]]`

构建消息字典列表（标准 API 格式）。

**返回：**

- `List[Dict]`: 标准格式的消息列表

**示例：**

```python
# 构建标准格式
messages = builder.build_messages_dict(
    chat_history=[
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你好！"}
    ],
    user_message="告诉我一个故事"
)

# 直接用于 OpenAI API
import openai
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=messages
)
```

输出格式：

```python
[
    {
        "role": "system",
        "content": "You are a helpful assistant..."
    },
    {
        "role": "user",
        "content": "你好"
    },
    {
        "role": "assistant",
        "content": "你好！"
    },
    {
        "role": "user",
        "content": "告诉我一个故事"
    }
]
```

---

#### `get_total_tokens(messages: List[Message]) -> int`

计算总 Token 数（估算）。

**示例：**

```python
messages = builder.build_messages(...)
total = builder.get_total_tokens(messages)
print(f"总 Token 数: ~{total}")
```

---

#### `print_messages(messages: List[Message])`

打印消息列表（用于调试）。

**示例：**

```python
messages = builder.build_messages(...)
builder.print_messages(messages)
```

输出：

```
================================================================================
📨 消息列表
================================================================================

⚙️ 消息 #1 [system] (~150 tokens)
--------------------------------------------------------------------------------
You are a helpful AI assistant.

角色描述...

👤 消息 #2 [user] (~10 tokens)
--------------------------------------------------------------------------------
你好！

🤖 消息 #3 [assistant] (~15 tokens)
--------------------------------------------------------------------------------
你好呀！

👤 消息 #4 [user] (~8 tokens)
--------------------------------------------------------------------------------
介绍一下你自己

================================================================================
📊 总计: 4 条消息, ~183 tokens
================================================================================
```

---

#### `get_triggered_entries(user_message: str) -> Dict`

获取会被触发的世界书条目（用于调试）。

**返回：**

- `dict`: {"before_char": [...], "after_char": [...]}

**示例：**

```python
# 查看哪些世界书条目会被触发
triggered = builder.get_triggered_entries("告诉我关于魔法的事情")

print(f"角色定义之前: {len(triggered['before_char'])} 个条目")
print(f"角色定义之后: {len(triggered['after_char'])} 个条目")

for entry in triggered['before_char']:
    print(f"  - {entry.comment}")
```

---

#### `print_triggered_entries(user_message: str)`

打印触发的世界书条目。

**示例：**

```python
builder.print_triggered_entries("告诉我关于魔法的事情")
```

输出：

```
================================================================================
🔍 世界书触发分析: "告诉我关于魔法的事情"
================================================================================

📍 角色定义之前: 2 个条目

  🔵 [常驻] 世界观设定
  🟢 [关键词] 魔法系统
     匹配关键词: 魔法

📍 角色定义之后: 1 个条目

  🟢 [关键词] 魔法学院
     匹配关键词: 魔法
================================================================================
```

---

### 提示词插入顺序

PromptBuilder 按照 SillyTavern 的标准顺序组装提示词：

1. **Main Prompt** - 主提示词
2. **World Info (before)** - 世界书（角色定义之前）
3. **Persona Description** - 用户人设
4. **Char Description** - 角色描述
5. **Char Personality** - 角色性格
6. **Scenario** - 情景设定
7. **Enhance Definitions** - 增强定义
8. **Auxiliary Prompt** - 辅助提示词
9. **World Info (after)** - 世界书（角色定义之后）
10. **Chat Examples** - 对话示例
11. **Chat History** - 聊天历史
12. **Post-History Instructions** - 历史后指令

---

### 完整示例

```python
from fichara import (
    load_card_data, 
    parse_character_card, 
    PromptBuilder
)

# 1. 加载角色卡
card_data = load_card_data("character.png")
card = parse_character_card(card_data)

# 2. 创建 PromptBuilder
builder = PromptBuilder(
    card=card,
    user_name="Alice",
    persona_description="{{user}} is a {{user_type}} who loves {{hobby}}."
)

# 3. 注册自定义变量
builder.register_variable("user_type", lambda ctx: "student")
builder.register_variable("hobby", lambda ctx: "reading")
builder.register_variable("greeting", lambda ctx: "Hello, {{user}}!")

# 4. 构建消息
messages = builder.build_messages_dict(
    chat_history=[
        {"role": "user", "content": "{{greeting}}"},
        {"role": "assistant", "content": "Hi {{user}}! How are you?"}
    ],
    user_message="Tell me about yourself.",
    include_world_info=True,
    include_examples=True
)

# 5. 使用消息
import openai
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=messages
)

print(response.choices[0].message.content)
```

---

## 🎯 完整工作流示例

### 示例 1：基础使用

```python
from fichara import *

# 加载
card_data = load_card_data("character.png")
card = parse_character_card(card_data)

# 验证
is_valid, errors = CharacterCardValidator.validate(card)
if not is_valid:
    card = CharacterCardValidator.auto_fix(card)

# 导出
CharacterCardExporter.to_json(card, "backup.json")
CharacterCardExporter.save_markdown(card, "character.md")

print(f"✅ 处理完成: {card.name}")
```

---

### 示例 2：世界书管理

```python
from fichara import *

# 加载角色卡
card_data = load_card_data("character.png")
card = parse_character_card(card_data)

# 创建管理器
manager = LorebookManager(card.data.character_book)

# 统计
manager.print_statistics()

# 查找空条目
empty = manager.find_empty_entries()
if empty:
    print(f"发现 {len(empty)} 个空条目")
    # 删除空条目
    manager.batch_delete([e.id for e in empty])

# 添加新条目
new_entry = manager.create_entry(
    comment="新设定",
    content="详细内容...",
    keys=["关键词1", "关键词2"],
    entry_type="green"
)
manager.add_entry(new_entry)

# 保存
output_data = card.model_dump(by_alias=True, exclude_none=True)
save_card_data("character.png", "updated.png", output_data)
```

---

### 示例 3：提示词构建

```python
from fichara import *

# 加载角色卡
card_data = load_card_data("character.png")
card = parse_character_card(card_data)

# 创建构建器
builder = PromptBuilder(
    card=card,
    user_name="Alice",
    persona_description="{{user}} is curious and friendly."
)

# 注册变量
builder.register_variable("weather", lambda ctx: "sunny")

# 构建消息
messages = builder.build_messages_dict(
    chat_history=[
        {"role": "user", "content": "你好！"},
        {"role": "assistant", "content": "你好，{{user}}！"}
    ],
    user_message="今天天气{{weather}}，我们聊聊吧！"
)

# 使用
import openai
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=messages
)
```

---

### 示例 4：批量处理

```python
from fichara import *
import os

def process_character_card(png_path):
    """处理单个角色卡"""
    try:
        # 加载
        card_data = load_card_data(png_path)
        card = parse_character_card(card_data)

        # 验证
        is_valid, errors = CharacterCardValidator.validate(card)

        # 统计
        result = {
            "name": card.name,
            "valid": is_valid,
            "errors": len(errors),
            "has_lorebook": bool(
                card.data.character_book if isinstance(card, CharacterCardV3)
                else card.character_book
            )
        }

        return result
    except Exception as e:
        return {"error": str(e)}

# 批量处理
folder = "characters/"
results = []

for filename in os.listdir(folder):
    if filename.endswith(".png"):
        path = os.path.join(folder, filename)
        result = process_character_card(path)
        results.append(result)
        print(f"✅ {filename}: {result}")

# 汇总
print(f"\n总计处理: {len(results)} 个角色卡")
valid_count = sum(1 for r in results if r.get("valid"))
print(f"有效: {valid_count}")
print(f"有问题: {len(results) - valid_count}")
```

---

## 🔧 高级技巧

### 技巧 1：链式操作

```python
from fichara import *

# 链式处理
(
    load_card_data("character.png")
    |> parse_character_card
    |> CharacterCardValidator.auto_fix
    |> (lambda card: CharacterCardExporter.to_json(card, "output.json"))
)
```

---

### 技巧 2：上下文管理器

```python
from fichara import *
from contextlib import contextmanager

@contextmanager
def character_card_context(png_path):
    """角色卡上下文管理器"""
    card_data = load_card_data(png_path)
    card = parse_character_card(card_data)
    try:
        yield card
    finally:
        # 自动保存
        output_data = card.model_dump(by_alias=True, exclude_none=True)
        save_card_data(png_path, png_path, output_data)

# 使用
with character_card_context("character.png") as card:
    card.name = "新名字"
    card.description = "新描述"
    # 退出时自动保存
```

---

### 技巧 3：自定义验证规则

```python
from fichara import CharacterCardValidator, ValidationError

class MyValidator(CharacterCardValidator):
    """自定义验证器"""

    @staticmethod
    def validate_custom(card):
        """自定义验证规则"""
        errors = []

        # 检查名称长度
        if len(card.name) < 2:
            errors.append(ValidationError(
                "error",
                "name",
                "名称太短"
            ))

        # 检查标签数量
        if len(card.tags) > 10:
            errors.append(ValidationError(
                "warning",
                "tags",
                "标签过多"
            ))

        return errors

# 使用
errors = MyValidator.validate_custom(card)
```

---

## 📚 更多资源

- **GitHub**: https://github.com/torinaViolet/fichara

---

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

**最后更新**: 2026-01-16
**版本**: 0.1.0
