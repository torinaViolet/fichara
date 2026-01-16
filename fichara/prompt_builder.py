# prompt_builder.py
"""
提示词组装器
支持角色分离、变量替换（含宏套宏）
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Optional

from models import CharacterCardV2, CharacterCardV3, WorldBookEntry
from variable_replacer import VariableReplacer


@dataclass
class PromptSection:
    """提示词片段"""
    name: str  # 片段名称
    content: str  # 内容
    enabled: bool  # 是否启用
    token_count: int  # Token数（估算）
    position: int  # 位置顺序
    source: str  # 来源（'card' 或 'custom'）


@dataclass
class Message:
    """消息对象"""
    role: str  # 'system', 'user', 'assistant'
    content: str  # 内容
    name: Optional[str] = None  # 可选的名称字段


class PromptBuilder:
    """提示词组装器"""

    # 标准插入顺序
    INSERTION_ORDER = {
        "main_prompt": 1,
        "world_info_before": 2,
        "persona_description": 3,
        "char_description": 4,
        "char_personality": 5,
        "scenario": 6,
        "enhance_definitions": 7,
        "auxiliary_prompt": 8,
        "world_info_after": 9,
        "chat_examples": 10,
        "chat_history": 11,
        "post_history_instructions": 12
    }

    def __init__(self,
                 card,
                 main_prompt: Optional[str] = None,
                 enhance_definitions: Optional[str] = None,
                 auxiliary_prompt: Optional[str] = None,
                 post_history_instructions: Optional[str] = None,
                 persona_description: str = "",
                 user_name: str = "User",
                 enable_variable_replacement: bool = True,
                 max_variable_depth: int = 5):
        """
        初始化提示词组装器

        Args:
            card: 角色卡对象 (CharacterCardV2 或 CharacterCardV3)
            main_prompt: 自定义主提示词（如果为None，使用角色卡的system_prompt）
            enhance_definitions: 自定义增强定义
            auxiliary_prompt: 自定义辅助提示词
            post_history_instructions: 自定义历史后指令（如果为None，使用角色卡的）
            persona_description: 用户人设描述
            user_name: 用户名
            enable_variable_replacement: 是否启用变量替换
            max_variable_depth: 最大变量嵌套深度（防止无限递归）
        """
        self.card = card
        self.persona_description = persona_description
        self.enable_variable_replacement = enable_variable_replacement
        self.max_variable_depth = max_variable_depth

        # 获取角色卡数据
        if isinstance(card, CharacterCardV3):
            self.data = card.data
        else:
            self.data = card

        # 创建变量替换器
        self.variable_replacer = VariableReplacer(
            user_name=user_name,
            char_name=card.name
        )

        # 处理 Main Prompt（优先使用自定义，否则使用角色卡的system_prompt）
        if main_prompt is not None:
            self.main_prompt = main_prompt
            self.main_prompt_source = "custom"
        else:
            self.main_prompt = getattr(self.data, 'system_prompt', '')
            self.main_prompt_source = "card"

        # 处理 Post-History Instructions（优先使用自定义，否则使用角色卡的）
        if post_history_instructions is not None:
            self.post_history_instructions = post_history_instructions
            self.post_history_source = "custom"
        else:
            self.post_history_instructions = getattr(self.data, 'post_history_instructions', '')
            self.post_history_source = "card"

        # 自定义字段（这些不从角色卡获取）
        self.enhance_definitions = enhance_definitions or ""
        self.auxiliary_prompt = auxiliary_prompt or ""

    def register_variable(self, var_name: str, callback):
        """
        注册自定义变量

        Args:
            var_name: 变量名
            callback: 回调函数
        """
        self.variable_replacer.register_variable(var_name, callback)

    def build_messages(self,
                       chat_history: List[Dict[str, str]] = None,
                       user_message: str = "",
                       include_world_info: bool = True,
                       include_examples: bool = True,
                       max_history_messages: int = 20) -> List[Message]:
        """
        构建消息列表（按角色分离）

        Args:
            chat_history: 聊天历史 [{"role": "user/assistant", "content": "..."}]
            user_message: 当前用户消息（用于触发世界书关键词）
            include_world_info: 是否包含世界书
            include_examples: 是否包含对话示例
            max_history_messages: 最大历史消息数

        Returns:
            消息列表 [Message(role="system", content="..."), ...]
        """
        chat_history = chat_history or []

        # 构建系统提示词
        system_content = self._build_system_prompt(
            user_message,
            include_world_info,
            include_examples
        )

        messages = []

        # 1. 系统消息
        if system_content.strip():
            messages.append(Message(
                role="system",
                content=system_content
            ))

        # 2. 对话示例（转换为消息格式）
        if include_examples and self.data.mes_example:
            example_messages = self._parse_chat_examples(self.data.mes_example)
            messages.extend(example_messages)

        # 3. 聊天历史
        if chat_history:
            history_messages = self._format_chat_history_as_messages(
                chat_history,
                max_history_messages
            )
            messages.extend(history_messages)

        # 4. Post-History Instructions（作为最后的系统消息）
        if self.post_history_instructions:
            post_content = self.post_history_instructions
            if self.enable_variable_replacement:
                post_content = self._replace_variables_recursive(post_content)

            if post_content.strip():
                messages.append(Message(
                    role="system",
                    content=post_content
                ))

        # 5. 当前用户消息（如果有）
        if user_message:
            user_content = user_message
            if self.enable_variable_replacement:
                user_content = self._replace_variables_recursive(user_content)

            messages.append(Message(
                role="user",
                content=user_content
            ))

        return messages

    def build_messages_dict(self, **kwargs) -> List[Dict[str, str]]:
        """
        构建消息字典列表（标准格式）

        Returns:
            [{"role": "system", "content": "..."}, ...]
        """
        messages = self.build_messages(**kwargs)

        result = []
        for msg in messages:
            msg_dict = {
                "role": msg.role,
                "content": msg.content
            }
            if msg.name:
                msg_dict["name"] = msg.name
            result.append(msg_dict)

        return result

    def _build_system_prompt(self,
                             user_message: str,
                             include_world_info: bool,
                             include_examples: bool) -> str:
        """构建系统提示词部分"""
        sections = []

        # 1. Main Prompt
        if self.main_prompt:
            content = self.main_prompt
            if self.enable_variable_replacement:
                content = self._replace_variables_recursive(content)
            sections.append(content)

        # 2. World Info (before)
        if include_world_info:
            world_before = self._get_world_info_content("before_char", user_message)
            if world_before:
                sections.append(world_before)

        # 3. Persona Description
        if self.persona_description:
            content = self.persona_description
            if self.enable_variable_replacement:
                content = self._replace_variables_recursive(content)
            sections.append(content)

        # 4. Char Description
        if self.data.description:
            content = self.data.description
            if self.enable_variable_replacement:
                content = self._replace_variables_recursive(content)
            sections.append(content)

        # 5. Char Personality
        if self.data.personality:
            content = self.data.personality
            if self.enable_variable_replacement:
                content = self._replace_variables_recursive(content)
            sections.append(content)

        # 6. Scenario
        if self.data.scenario:
            content = self.data.scenario
            if self.enable_variable_replacement:
                content = self._replace_variables_recursive(content)
            sections.append(content)

        # 7. Enhance Definitions
        if self.enhance_definitions:
            content = self.enhance_definitions
            if self.enable_variable_replacement:
                content = self._replace_variables_recursive(content)
            sections.append(content)

        # 8. Auxiliary Prompt
        if self.auxiliary_prompt:
            content = self.auxiliary_prompt
            if self.enable_variable_replacement:
                content = self._replace_variables_recursive(content)
            sections.append(content)

        # 9. World Info (after)
        if include_world_info:
            world_after = self._get_world_info_content("after_char", user_message)
            if world_after:
                sections.append(world_after)

        # 拼接所有部分
        return "\n\n".join(s.strip() for s in sections if s.strip())

    def _replace_variables_recursive(self, text: str, depth: int = 0) -> str:
        """
        递归替换变量（支持宏套宏）

        Args:
            text: 原始文本
            depth: 当前递归深度

        Returns:
            替换后的文本
        """
        if depth >= self.max_variable_depth:
            print(f"⚠️ 达到最大变量嵌套深度 {self.max_variable_depth}，停止递归")
            return text

        # 第一次替换
        replaced = self.variable_replacer.replace(text)

        if replaced == text:
            return replaced

            # 只有当文本发生变化，且看起来还有变量时，才继续递归
        if re.search(r'\{\{[^}]+}}', replaced):
            return self._replace_variables_recursive(replaced, depth + 1)

        return replaced

    def _get_world_info_content(self, position: str, user_message: str) -> str:
        """
        获取指定位置的世界书内容
        实现常驻触发（蓝灯）和关键词触发（绿灯）

        Args:
            position: 'before_char' 或 'after_char'
            user_message: 用户消息（用于关键词匹配）
        """
        # 获取世界书
        lorebook = None
        if isinstance(self.card, CharacterCardV3):
            lorebook = self.data.character_book
        elif isinstance(self.card, CharacterCardV2):
            lorebook = self.card.character_book

        if not lorebook or not lorebook.entries:
            return ""

        # 筛选指定位置的条目
        position_entries = [e for e in lorebook.entries
                            if e.position == position and e.enabled]

        if not position_entries:
            return ""

        # 分类条目
        triggered_entries = []

        for entry in position_entries:
            # 1. 蓝灯条目（常驻触发）
            if entry.constant:
                triggered_entries.append(entry)
                continue

            # 2. 向量条目（暂时跳过）
            if entry.extensions.vectorized:
                continue

            # 3. 绿灯条目（关键词触发）
            if self._check_keyword_match(entry, user_message):
                triggered_entries.append(entry)

        if not triggered_entries:
            return ""

        # 按 insertion_order 排序
        triggered_entries.sort(key=lambda e: e.insertion_order)

        # 组装内容（并替换变量）
        parts = []
        for entry in triggered_entries:
            if entry.content.strip():
                content = entry.content.strip()
                if self.enable_variable_replacement:
                    content = self._replace_variables_recursive(content)
                parts.append(content)

        return "\n\n".join(parts)

    def _check_keyword_match(self, entry: WorldBookEntry, user_message: str) -> bool:
        """检查关键词是否匹配"""
        if not user_message:
            return False

        all_keywords = entry.keys + entry.secondary_keys

        if not all_keywords:
            return False

        search_text = user_message

        case_sensitive = entry.extensions.case_sensitive
        if case_sensitive is None:
            case_sensitive = False

        if not case_sensitive:
            search_text = search_text.lower()
            all_keywords = [k.lower() for k in all_keywords]

        use_regex = entry.use_regex
        match_whole_words = entry.extensions.match_whole_words
        if match_whole_words is None:
            match_whole_words = False

        for keyword in all_keywords:
            if not keyword.strip():
                continue

            if use_regex:
                try:
                    flags = 0 if case_sensitive else re.IGNORECASE
                    if re.search(keyword, user_message, flags):
                        return True
                except re.error:
                    if keyword in search_text:
                        return True
            else:
                if match_whole_words:
                    pattern = r'\b' + re.escape(keyword) + r'\b'
                    flags = 0 if case_sensitive else re.IGNORECASE
                    if re.search(pattern, user_message, flags):
                        return True
                else:
                    if keyword in search_text:
                        return True

        return False

    def _parse_chat_examples(self, mes_example: str) -> List[Message]:
        """
        解析对话示例为消息列表

        格式: <START>\n对话1\n<START>\n对话2
        """
        messages = []

        # 按 <START> 分割
        examples = mes_example.split('<START>')

        for example in examples:
            example = example.strip()
            if not example:
                continue

            # 替换变量
            if self.enable_variable_replacement:
                example = self._replace_variables_recursive(example)

            # 解析对话（简单实现：按行分割，识别 User: 和 Char:）
            lines = example.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # 尝试识别角色
                if line.startswith('{{user}}:') or line.startswith('User:'):
                    content = line.split(':', 1)[1].strip()
                    messages.append(Message(role="user", content=content))
                elif line.startswith('{{char}}:') or line.startswith(f'{self.card.name}:'):
                    content = line.split(':', 1)[1].strip()
                    messages.append(Message(role="assistant", content=content))
                else:
                    # 无法识别角色，作为系统消息
                    messages.append(Message(role="system", content=line))

        return messages

    def _format_chat_history_as_messages(self,
                                         chat_history: List[Dict[str, str]],
                                         max_messages: int) -> List[Message]:
        """格式化聊天历史为消息列表"""
        recent_history = chat_history[-max_messages:] if max_messages > 0 else chat_history

        messages = []
        for msg in recent_history:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            # 替换变量
            if self.enable_variable_replacement:
                content = self._replace_variables_recursive(content)

            messages.append(Message(
                role=role,
                content=content
            ))

        return messages

    def _estimate_tokens(self, text: str) -> int:
        """估算 Token 数"""
        if not text:
            return 0
        return len(text) // 3

    def get_total_tokens(self, messages: List[Message]) -> int:
        """计算总 Token 数"""
        return sum(self._estimate_tokens(msg.content) for msg in messages)

    def print_messages(self, messages: List[Message]):
        """打印消息列表（用于调试）"""
        print("\n" + "=" * 80)
        print("📨 消息列表")
        print("=" * 80)

        total_tokens = 0

        for i, msg in enumerate(messages, 1):
            tokens = self._estimate_tokens(msg.content)
            total_tokens += tokens

            role_icon = {
                "system": "⚙️",
                "user": "👤",
                "assistant": "🤖"
            }.get(msg.role, "❓")

            print(f"\n{role_icon} 消息 #{i} [{msg.role}] (~{tokens} tokens)")
            print("-" * 80)

            # 显示内容（限制长度）
            content = msg.content
            if len(content) > 200:
                content = content[:200] + "..."
            print(content)

        print("\n" + "=" * 80)
        print(f"📊 总计: {len(messages)} 条消息, ~{total_tokens} tokens")
        print("=" * 80 + "\n")

