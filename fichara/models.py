# models.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any, Literal
from enum import IntEnum


# ============ 枚举类型 ============

class EntryRole(IntEnum):
    """条目角色类型"""
    SYSTEM = 0
    USER = 1
    ASSISTANT = 2


class EntryPosition(IntEnum):
    """条目插入位置（extensions.position）"""
    BEFORE_CHAR = 0
    AFTER_CHAR = 1
    BEFORE_AUTHOR_NOTE = 2
    AFTER_AUTHOR_NOTE = 3
    AT_DEPTH = 4
    BEFORE_EXAMPLES = 5
    AFTER_EXAMPLES = 6
    OUTLET = 7


# ============ 世界书扩展 ============

class WorldBookEntryExtensions(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    """世界书条目扩展字段"""
    position: int = 0
    display_index: int = 0
    depth: int = 4
    scan_depth: Optional[int] = None
    probability: int = 100
    useProbability: bool = True
    selectiveLogic: int = 0
    exclude_recursion: bool = False
    prevent_recursion: bool = False
    delay_until_recursion: int = 0
    group: str = ""
    group_override: bool = False
    group_weight: int = 100
    use_group_scoring: bool = False
    match_whole_words: Optional[bool] = None
    case_sensitive: Optional[bool] = None
    role: int = 0
    outlet_name: str = ""
    vectorized: bool = False
    sticky: Optional[int] = None
    cooldown: Optional[int] = None
    delay: Optional[int] = None
    automation_id: str = ""
    match_persona_description: bool = False
    match_character_description: bool = False
    match_character_personality: bool = False
    match_character_depth_prompt: bool = False
    match_scenario: bool = False
    match_creator_notes: bool = False
    triggers: List[Any] = []
    ignore_budget: bool = False


class WorldBookEntry(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    """世界书条目"""
    id: int
    keys: List[str] = []
    secondary_keys: List[str] = []
    comment: str = ""
    content: str = ""
    constant: bool = False
    selective: bool = True
    enabled: bool = True
    insertion_order: int = 100
    position: Literal["before_char", "after_char"] = "before_char"
    use_regex: bool = True
    extensions: WorldBookEntryExtensions = Field(default_factory=WorldBookEntryExtensions)


class CharacterBook(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    """角色世界书"""
    name: Optional[str] = None
    description: Optional[str] = None
    scan_depth: Optional[int] = Field(None, alias="scanDepth")
    token_budget: Optional[int] = Field(None, alias="tokenBudget")
    recursive_scanning: Optional[bool] = Field(None, alias="recursiveScanning")
    entries: List[WorldBookEntry] = []


# ============ 深度提示词 ============

class DepthPrompt(BaseModel):
    """深度提示词配置"""
    prompt: str = ""
    depth: int = 4
    role: str = "system"


# ============ V3数据扩展 ============

class CharacterDataExtensions(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="allow")

    """V3 data.extensions 字段"""
    talkativeness: Optional[str] = None
    fav: bool = False
    world: Optional[str] = None
    depth_prompt: Optional[DepthPrompt] = None


# ============ V3数据对象 ============

class CharacterDataV3(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    """V3 的 data 对象"""
    name: str
    description: str = ""
    personality: str = ""
    scenario: str = ""
    first_mes: str = ""
    mes_example: str = ""
    creator_notes: str = ""
    system_prompt: str = ""
    post_history_instructions: str = ""
    alternate_greetings: List[str] = []
    group_only_greetings: List[str] = []
    tags: List[str] = []
    creator: str = ""
    character_version: str = ""
    character_book: Optional[CharacterBook] = None
    extensions: CharacterDataExtensions = Field(default_factory=CharacterDataExtensions)


# ============ V3角色卡 ============

class CharacterCardV3(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    """SillyTavern V3 角色卡"""
    spec: str = "chara_card_v3"
    spec_version: str = "3.0"
    name: str
    description: str = ""
    personality: str = ""
    scenario: str = ""
    first_mes: str = ""
    mes_example: str = ""
    creatorcomment: str = ""
    avatar: str = "none"
    talkativeness: str = "0.5"
    fav: bool = False
    tags: List[str] = []
    data: CharacterDataV3
    create_date: Optional[str] = None


# ============ V2角色卡 ============

class CharacterCardV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    """SillyTavern V2 角色卡"""
    spec: str = "chara_card_v2"
    spec_version: str = "2.0"
    name: str
    description: str = ""
    personality: str = ""
    scenario: str = ""
    first_mes: str = ""
    mes_example: str = ""
    creator_notes: str = ""
    system_prompt: str = ""
    post_history_instructions: str = ""
    alternate_greetings: List[str] = []
    character_book: Optional[CharacterBook] = None
    tags: List[str] = []
    creator: str = ""
    character_version: str = ""
    extensions: dict[str, Any] = {}


# ============ 智能解析 ============

def parse_character_card(data: dict) -> CharacterCardV3 | CharacterCardV2:
    """智能解析角色卡"""
    spec = data.get('spec', '')

    if spec == 'chara_card_v3':
        return CharacterCardV3(**data)
    elif spec == 'chara_card_v2':
        return CharacterCardV2(**data)
    else:
        return CharacterCardV2(**data)


# ============ 使用示例 ============

if __name__ == '__main__':
    from png_handler import load_card_data

    raw_data = load_card_data(r"C:\Users\Violet\Downloads\测试.png")
    card = parse_character_card(raw_data)

    print(f"版本: {card.spec} {card.spec_version}")
    print(f"角色名: {card.name}")

    if isinstance(card, CharacterCardV3):
        print(f"话痨度: {card.data.extensions.talkativeness}")
        print(f"世界书: {card.data.extensions.world}")

        if card.data.character_book:
            print(f"\n世界书条目数: {len(card.data.character_book.entries)}")

            green_entries = [e for e in card.data.character_book.entries if
                             not e.constant and not e.extensions.vectorized]
            blue_entries = [e for e in card.data.character_book.entries if e.constant]
            vector_entries = [e for e in card.data.character_book.entries if e.extensions.vectorized]

            print(f"🟢 绿灯条目: {len(green_entries)}")
            print(f"🔵 蓝灯条目: {len(blue_entries)}")
            print(f"🔗 向量条目: {len(vector_entries)}")

            for entry in card.data.character_book.entries:
                role_emoji = {0: "⚙️", 1: "👤", 2: "🤖"}.get(entry.extensions.role, "")
                entry_type = "🔵" if entry.constant else ("🔗" if entry.extensions.vectorized else "🟢")
                print(f"\n{entry_type} {role_emoji} {entry.comment}")
                print(f"  位置: {entry.position} (细分: {entry.extensions.position})")
                print(f"  深度: {entry.extensions.depth}")
