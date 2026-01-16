# lorebook_handler.py
"""
独立世界书处理器
支持 SillyTavern 独立导出的世界书格式
"""

import json
from typing import Dict, Any, List
from models import CharacterBook, WorldBookEntry, WorldBookEntryExtensions


class LorebookHandler:
    """独立世界书处理器"""

    @staticmethod
    def load_standalone_lorebook(json_path: str) -> CharacterBook:
        """
        加载独立世界书JSON文件

        Args:
            json_path: JSON文件路径

        Returns:
            CharacterBook 对象
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return LorebookHandler.parse_standalone_lorebook(data)

    @staticmethod
    def parse_standalone_lorebook(data: Dict[str, Any]) -> CharacterBook:
        """
        解析独立世界书数据

        Args:
            data: 独立世界书数据字典

        Returns:
            CharacterBook 对象
        """
        entries_dict = data.get('entries', {})
        entries = []

        # 转换每个条目
        for uid_str, entry_data in entries_dict.items():
            entry = LorebookHandler._convert_entry(entry_data)
            entries.append(entry)

        # 创建 CharacterBook
        book = CharacterBook(
            name=data.get('name'),
            description=data.get('description'),
            entries=entries
        )

        print(f"✅ 已加载独立世界书: {len(entries)} 个条目")
        return book

    @staticmethod
    def _convert_entry(entry_data: Dict[str, Any]) -> WorldBookEntry:
        """
        转换单个条目从独立格式到角色卡格式

        Args:
            entry_data: 独立格式的条目数据

        Returns:
            WorldBookEntry 对象
        """

        # 辅助函数：安全获取值
        def get_bool(key: str, default: bool = False) -> bool:
            """获取布尔值，None 转为默认值"""
            value = entry_data.get(key)
            return default if value is None else bool(value)

        def get_int(key: str, default: int = 0) -> int:
            """获取整数值，None 转为默认值"""
            value = entry_data.get(key)
            return default if value is None else int(value)

        def get_str(key: str, default: str = '') -> str:
            """获取字符串值，None 转为默认值"""
            value = entry_data.get(key)
            return default if value is None else str(value)

        # 基础字段
        entry_dict = {
            'id': get_int('uid', 0),
            'keys': entry_data.get('key', []),
            'secondary_keys': entry_data.get('keysecondary', []),
            'comment': get_str('comment', ''),
            'content': get_str('content', ''),
            'constant': get_bool('constant', False),
            'selective': get_bool('selective', True),
            'enabled': not get_bool('disable', False),  # 注意反向
            'insertion_order': get_int('order', 100),
            'use_regex': True,
        }

        # 转换 position
        position_map = {
            0: 'before_char',
            1: 'after_char',
            2: 'after_char',
            3: 'after_char',
            4: 'after_char',
            5: 'after_char',
            6: 'after_char',
            7: 'after_char',
        }
        entry_dict['position'] = position_map.get(get_int('position', 0), 'before_char')

        # Extensions 字段
        extensions_dict = {
            'position': get_int('position', 0),
            'display_index': get_int('displayIndex', 0),
            'depth': get_int('depth', 4),
            'probability': get_int('probability', 100),
            'useProbability': get_bool('useProbability', True),
            'selectiveLogic': get_int('selectiveLogic', 0),
            'exclude_recursion': get_bool('excludeRecursion', False),
            'prevent_recursion': get_bool('preventRecursion', False),
            'delay_until_recursion': get_int('delayUntilRecursion', 0),
            'scan_depth': entry_data.get('scanDepth'),
            'match_whole_words': entry_data.get('matchWholeWords'),
            'case_sensitive': entry_data.get('caseSensitive'),
            'use_group_scoring': get_bool('useGroupScoring', False),
            'outlet_name': get_str('outletName', ''),
            'group': get_str('group', ''),
            'group_override': get_bool('groupOverride', False),
            'group_weight': get_int('groupWeight', 100),
            'automation_id': get_str('automationId', ''),
            'role': get_int('role', 0),
            'vectorized': get_bool('vectorized', False),
            'sticky': entry_data.get('sticky'),
            'cooldown': entry_data.get('cooldown'),
            'delay': entry_data.get('delay'),
            'match_persona_description': get_bool('matchPersonaDescription', False),
            'match_character_description': get_bool('matchCharacterDescription', False),
            'match_character_personality': get_bool('matchCharacterPersonality', False),
            'match_character_depth_prompt': get_bool('matchCharacterDepthPrompt', False),
            'match_scenario': get_bool('matchScenario', False),
            'match_creator_notes': get_bool('matchCreatorNotes', False),
            'triggers': entry_data.get('triggers', []),
            'ignore_budget': get_bool('ignoreBudget', False),
        }

        entry_dict['extensions'] = WorldBookEntryExtensions(**extensions_dict)

        return WorldBookEntry(**entry_dict)

    @staticmethod
    def save_standalone_lorebook(book: CharacterBook, output_path: str):
        """
        保存为独立世界书JSON格式

        Args:
            book: CharacterBook 对象
            output_path: 输出文件路径
        """
        data = LorebookHandler.to_standalone_format(book)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✅ 已保存独立世界书: {output_path}")

    @staticmethod
    def to_standalone_format(book: CharacterBook) -> Dict[str, Any]:
        """
        转换为独立世界书格式

        Args:
            book: CharacterBook 对象

        Returns:
            独立格式的字典
        """
        entries_dict = {}

        for entry in book.entries:
            uid = str(entry.id)
            entries_dict[uid] = LorebookHandler._convert_entry_to_standalone(entry)

        return {
            'entries': entries_dict
        }

    @staticmethod
    def _convert_entry_to_standalone(entry: WorldBookEntry) -> Dict[str, Any]:
        """
        转换单个条目到独立格式

        Args:
            entry: WorldBookEntry 对象

        Returns:
            独立格式的字典
        """
        return {
            'uid': entry.id,
            'key': entry.keys,
            'keysecondary': entry.secondary_keys,
            'comment': entry.comment,
            'content': entry.content,
            'constant': entry.constant,
            'vectorized': entry.extensions.vectorized,
            'selective': entry.selective,
            'selectiveLogic': entry.extensions.selectiveLogic,
            'addMemo': False,
            'order': entry.insertion_order,
            'position': entry.extensions.position,
            'disable': not entry.enabled,
            'ignoreBudget': entry.extensions.ignore_budget,
            'excludeRecursion': entry.extensions.exclude_recursion,
            'preventRecursion': entry.extensions.prevent_recursion,
            'matchPersonaDescription': entry.extensions.match_persona_description,
            'matchCharacterDescription': entry.extensions.match_character_description,
            'matchCharacterPersonality': entry.extensions.match_character_personality,
            'matchCharacterDepthPrompt': entry.extensions.match_character_depth_prompt,
            'matchScenario': entry.extensions.match_scenario,
            'matchCreatorNotes': entry.extensions.match_creator_notes,
            'delayUntilRecursion': entry.extensions.delay_until_recursion,
            'probability': entry.extensions.probability,
            'useProbability': entry.extensions.useProbability,
            'depth': entry.extensions.depth,
            'outletName': entry.extensions.outlet_name,
            'group': entry.extensions.group,
            'groupOverride': entry.extensions.group_override,
            'groupWeight': entry.extensions.group_weight,
            'scanDepth': entry.extensions.scan_depth,
            'caseSensitive': entry.extensions.case_sensitive,
            'matchWholeWords': entry.extensions.match_whole_words,
            'useGroupScoring': entry.extensions.use_group_scoring,
            'automationId': entry.extensions.automation_id,
            'role': entry.extensions.role,
            'sticky': entry.extensions.sticky,
            'cooldown': entry.extensions.cooldown,
            'delay': entry.extensions.delay,
            'triggers': entry.extensions.triggers,
            'displayIndex': entry.extensions.display_index,
            'characterFilter': {
                'isExclude': False,
                'names': [],
                'tags': []
            }
        }

    @staticmethod
    def merge_into_character(book: CharacterBook,
                             card_book: CharacterBook,
                             strategy: str = "keep_both") -> int:
        """
        将独立世界书合并到角色卡的世界书中

        Args:
            book: 独立世界书
            card_book: 角色卡的世界书
            strategy: 合并策略

        Returns:
            合并的条目数
        """
        from lorebook_manager import LorebookManager

        manager = LorebookManager(card_book)
        return manager.merge_with(book, strategy)


# ============ 使用示例 ============

if __name__ == '__main__':
    print("=" * 60)
    print("独立世界书处理器测试")
    print("=" * 60)

    # 1. 加载独立世界书
    print("\n1. 加载独立世界书...")
    standalone_book = LorebookHandler.load_standalone_lorebook(
        r"C:\Users\Violet\Downloads\测试世界书（角色）.json"
    )

    print(f"条目数: {len(standalone_book.entries)}")

    # 2. 显示统计
    from lorebook_manager import LorebookManager

    manager = LorebookManager(standalone_book)
    manager.print_statistics()

    # 3. 保存为独立格式
    print("\n2. 保存为独立世界书格式...")
    LorebookHandler.save_standalone_lorebook(
        standalone_book,
        "output_standalone.json"
    )

    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)
