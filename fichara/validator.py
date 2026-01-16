# validator.py
"""
角色卡数据验证器
提供数据完整性检查和自动修复功能
"""

from typing import Union, List, Tuple
from models import CharacterCardV2, CharacterCardV3, WorldBookEntry


class ValidationError:
    """验证错误信息"""

    def __init__(self, level: str, field: str, message: str):
        """
        初始化验证错误

        Args:
            level: 错误级别 ('error' 或 'warning')
            field: 出错的字段名
            message: 错误描述
        """
        self.level = level
        self.field = field
        self.message = message

    def __str__(self):
        emoji = "❌" if self.level == "error" else "⚠️"
        return f"{emoji} [{self.level.upper()}] {self.field}: {self.message}"


class CharacterCardValidator:
    """角色卡验证器"""

    @staticmethod
    def validate(card: Union[CharacterCardV2, CharacterCardV3]) -> Tuple[bool, List[ValidationError]]:
        """
        验证角色卡数据完整性

        Args:
            card: 要验证的角色卡对象

        Returns:
            (是否通过验证, 错误/警告列表)
        """
        errors = []

        # 1. 验证基础字段
        errors.extend(CharacterCardValidator._validate_basic_fields(card))

        # 2. 验证世界书
        if isinstance(card, CharacterCardV3):
            if card.data.character_book:
                errors.extend(CharacterCardValidator._validate_lorebook(card.data.character_book))
        elif isinstance(card, CharacterCardV2):
            if card.character_book:
                errors.extend(CharacterCardValidator._validate_lorebook(card.character_book))

        # 3. 验证标签
        errors.extend(CharacterCardValidator._validate_tags(card))

        # 判断是否有错误（不包括警告）
        has_errors = any(e.level == "error" for e in errors)

        return not has_errors, errors

    @staticmethod
    def _validate_basic_fields(card) -> List[ValidationError]:
        """验证基础字段"""
        errors = []

        # 检查角色名
        if not card.name or card.name.strip() == "":
            errors.append(ValidationError("error", "name", "角色名称不能为空"))
        elif len(card.name) > 100:
            errors.append(ValidationError("warning", "name", "角色名称过长（>100字符）"))

        # 检查描述
        if not card.description or card.description.strip() == "":
            errors.append(ValidationError("warning", "description", "角色描述为空"))

        # 检查第一条消息
        if not card.first_mes or card.first_mes.strip() == "":
            errors.append(ValidationError("warning", "first_mes", "第一条消息为空"))

        # 检查版本号
        if card.spec not in ["chara_card_v2", "chara_card_v3"]:
            errors.append(ValidationError("error", "spec", f"不支持的版本: {card.spec}"))

        return errors

    @staticmethod
    def _validate_lorebook(lorebook) -> List[ValidationError]:
        """验证世界书"""
        errors = []

        if not lorebook.entries:
            errors.append(ValidationError("warning", "character_book", "世界书没有任何条目"))
            return errors

        # 检查重复ID
        ids = [entry.id for entry in lorebook.entries]
        duplicate_ids = [id for id in ids if ids.count(id) > 1]
        if duplicate_ids:
            errors.append(ValidationError(
                "error",
                "character_book.entries",
                f"发现重复的条目ID: {set(duplicate_ids)}"
            ))

        # 检查每个条目
        for i, entry in enumerate(lorebook.entries):
            entry_errors = CharacterCardValidator._validate_entry(entry, i)
            errors.extend(entry_errors)

        return errors

    @staticmethod
    def _validate_entry(entry: WorldBookEntry, index: int) -> List[ValidationError]:
        """验证单个世界书条目"""
        errors = []
        prefix = f"character_book.entries[{index}]"

        # 检查关键词触发条目是否有关键词
        if not entry.constant and not entry.extensions.vectorized:
            if not entry.keys and not entry.secondary_keys:
                errors.append(ValidationError(
                    "warning",
                    f"{prefix}.keys",
                    f"绿灯条目 '{entry.comment}' 没有设置关键词"
                ))

        # 检查内容
        if not entry.content or entry.content.strip() == "":
            errors.append(ValidationError(
                "warning",
                f"{prefix}.content",
                f"条目 '{entry.comment}' 内容为空"
            ))

        # 检查深度值
        if entry.extensions.depth < 0 or entry.extensions.depth > 100:
            errors.append(ValidationError(
                "warning",
                f"{prefix}.extensions.depth",
                f"条目 '{entry.comment}' 深度值异常: {entry.extensions.depth}"
            ))

        # 检查概率值
        if entry.extensions.probability < 0 or entry.extensions.probability > 100:
            errors.append(ValidationError(
                "error",
                f"{prefix}.extensions.probability",
                f"条目 '{entry.comment}' 概率值无效: {entry.extensions.probability}"
            ))

        return errors

    @staticmethod
    def _validate_tags(card) -> List[ValidationError]:
        """验证标签"""
        errors = []

        if not card.tags:
            errors.append(ValidationError("warning", "tags", "没有设置任何标签"))
        elif len(card.tags) > 20:
            errors.append(ValidationError("warning", "tags", f"标签过多（{len(card.tags)}个）"))

        return errors

    @staticmethod
    def auto_fix(card: Union[CharacterCardV2, CharacterCardV3]) -> Union[CharacterCardV2, CharacterCardV3]:
        """
        自动修复常见问题

        Args:
            card: 要修复的角色卡

        Returns:
            修复后的角色卡
        """
        # 1. 修复空字符串
        if not card.name or card.name.strip() == "":
            card.name = "未命名角色"

        if not card.description:
            card.description = ""

        if not card.first_mes:
            card.first_mes = ""

        # 2. 修复世界书
        if isinstance(card, CharacterCardV3):
            if card.data.character_book:
                CharacterCardValidator._fix_lorebook(card.data.character_book)
        elif isinstance(card, CharacterCardV2):
            if card.character_book:
                CharacterCardValidator._fix_lorebook(card.character_book)

        return card

    @staticmethod
    def _fix_lorebook(lorebook):
        """修复世界书问题"""
        # 修复重复ID
        used_ids = set()
        max_id = max([e.id for e in lorebook.entries], default=-1)

        for entry in lorebook.entries:
            if entry.id in used_ids:
                # 分配新ID
                max_id += 1
                entry.id = max_id
            used_ids.add(entry.id)

        # 修复概率值
        for entry in lorebook.entries:
            if entry.extensions.probability < 0:
                entry.extensions.probability = 0
            elif entry.extensions.probability > 100:
                entry.extensions.probability = 100

            # 修复深度值
            if entry.extensions.depth < 0:
                entry.extensions.depth = 4
            elif entry.extensions.depth > 100:
                entry.extensions.depth = 100


# ============ 使用示例 ============

if __name__ == '__main__':
    from png_handler import load_card_data
    from models import parse_character_card

    # 加载角色卡
    raw_data = load_card_data(r"C:\Users\Violet\Downloads\测试.png")
    card = parse_character_card(raw_data)

    # 验证
    is_valid, errors = CharacterCardValidator.validate(card)

    print(f"验证结果: {'✅ 通过' if is_valid else '❌ 失败'}")
    print(f"发现 {len(errors)} 个问题:\n")

    for error in errors:
        print(error)

    # 自动修复
    if not is_valid:
        print("\n正在尝试自动修复...")
        fixed_card = CharacterCardValidator.auto_fix(card)
        is_valid_after, errors_after = CharacterCardValidator.validate(fixed_card)
        print(f"修复后: {'✅ 通过' if is_valid_after else '❌ 仍有问题'}")