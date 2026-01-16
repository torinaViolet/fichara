# 🎭 FiChara

一个强大的 Python 库，用于解析和管理 SillyTavern 角色卡。

## ✨ 特性

- 📦 完整的角色卡支持（V2/V3）
- 🌍 强大的世界书管理
- 🔧 数据验证和自动修复
- 📤 多种导出格式（JSON、Markdown、PNG）
- 🔄 灵活的变量替换系统（支持宏套宏）
- 🎯 专业的提示词构建器

## 🚀 快速开始

### 安装

```bash
pip install Pillow pydantic
```

### 基础用法

```python
from fichara import load_card_data, parse_character_card

# 加载角色卡
card_data = load_card_data("character.png")
card = parse_character_card(card_data)

print(f"角色名: {card.name}")
print(f"描述: {card.description}")
```

### 验证和修复

```python
from fichara import CharacterCardValidator

is_valid, errors = CharacterCardValidator.validate(card)
if not is_valid:
    fixed_card = CharacterCardValidator.auto_fix(card)
```

### 世界书管理

```python
from fichara import LorebookManager

manager = LorebookManager(card.data.character_book)
manager.print_statistics()

# 搜索
results = manager.find_by_keyword("魔法")
```

### 提示词构建

```python
from fichara import PromptBuilder

builder = PromptBuilder(card=card, user_name="Alice")

messages = builder.build_messages_dict(
    chat_history=[
        {"role": "user", "content": "你好！"},
        {"role": "assistant", "content": "你好呀！"}
    ],
    user_message="介绍一下你自己"
)
```

## 📚 主要模块

- **png_handler** - PNG 元数据读写
- **models** - 数据模型（V2/V3）
- **validator** - 数据验证
- **exporter** - 多格式导出
- **lorebook_handler** - 独立世界书
- **lorebook_manager** - 世界书管理
- **variable_replacer** - 变量替换
- **prompt_builder** - 提示词组装

## 📄 许可证

MIT License

## 🙏 致谢

感谢 [SillyTavern](https://github.com/SillyTavern/SillyTavern) 项目