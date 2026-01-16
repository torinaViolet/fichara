# exporter.py
"""
角色卡导出工具
支持导出为 JSON、Markdown、PNG 等格式
"""

import json
from typing import Union, Optional
from pathlib import Path
from PIL import Image
from models import CharacterCardV2, CharacterCardV3
from png_handler import save_card_data


class CharacterCardExporter:
    """角色卡导出器"""

    @staticmethod
    def to_json(card: Union[CharacterCardV2, CharacterCardV3],
                output_path: str,
                indent: int = 2,
                ensure_ascii: bool = False):
        """
        导出为JSON文件

        Args:
            card: 角色卡对象
            output_path: 输出文件路径
            indent: JSON缩进空格数
            ensure_ascii: 是否转义非ASCII字符
        """
        # 转换为字典
        data = card.model_dump(by_alias=True, exclude_none=True)

        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)

        print(f"✅ 已导出JSON: {output_path}")

    @staticmethod
    def to_png(card: Union[CharacterCardV2, CharacterCardV3],
               image_path: str,
               output_path: str):
        """
        将角色卡数据写入PNG图片

        Args:
            card: 角色卡对象
            image_path: 源图片路径（作为载体）
            output_path: 输出PNG路径
        """
        # 转换为字典
        card_data = card.model_dump(by_alias=True, exclude_none=True)

        # 写入PNG
        save_card_data(image_path, output_path, card_data)

        print(f"✅ 已导出PNG: {output_path}")

    @staticmethod
    def from_json_to_png(json_path: str,
                         image_path: str,
                         output_path: str):
        """
        从JSON文件创建PNG角色卡

        Args:
            json_path: JSON文件路径
            image_path: 图片路径（作为载体）
            output_path: 输出PNG路径
        """
        # 读取JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            card_data = json.load(f)

        # 写入PNG
        save_card_data(image_path, output_path, card_data)

        print(f"✅ 已从JSON创建PNG: {output_path}")

    @staticmethod
    def change_image(original_png: str,
                     new_image: str,
                     output_path: str):
        """
        更换角色卡的图片（保留数据）

        Args:
            original_png: 原始角色卡PNG
            new_image: 新图片路径
            output_path: 输出路径
        """
        from png_handler import load_card_data

        # 读取原始角色卡数据
        card_data = load_card_data(original_png)

        if not card_data:
            raise ValueError("无法从原始PNG读取角色卡数据")

        # 使用新图片保存数据
        save_card_data(new_image, output_path, card_data)

        print(f"✅ 已更换图片: {output_path}")

    @staticmethod
    def create_png_from_scratch(card: Union[CharacterCardV2, CharacterCardV3],
                                image_path: str,
                                output_path: str):
        """
        从零创建PNG角色卡（使用指定图片）

        Args:
            card: 角色卡对象
            image_path: 图片路径
            output_path: 输出PNG路径
        """
        CharacterCardExporter.to_png(card, image_path, output_path)

    @staticmethod
    def create_default_image(output_path: str,
                             width: int = 512,
                             height: int = 512,
                             color: tuple = (200, 200, 200)):
        """
        创建默认占位图片

        Args:
            output_path: 输出路径
            width: 图片宽度
            height: 图片高度
            color: RGB颜色
        """
        from PIL import Image, ImageDraw, ImageFont

        # 创建图片
        img = Image.new('RGB', (width, height), color)
        draw = ImageDraw.Draw(img)

        # 添加文字
        text = "Character Card"

        # 尝试使用系统字体，失败则使用默认
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()

        # 计算文字位置（居中）
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        position = ((width - text_width) // 2, (height - text_height) // 2)

        # 绘制文字
        draw.text(position, text, fill=(100, 100, 100), font=font)

        # 保存
        img.save(output_path, 'PNG')

        print(f"✅ 已创建默认图片: {output_path}")

        return output_path

    @staticmethod
    def to_markdown(card: Union[CharacterCardV2, CharacterCardV3]) -> str:
        """
        导出为Markdown格式

        Args:
            card: 角色卡对象

        Returns:
            Markdown格式的字符串
        """
        lines = []

        # 标题
        lines.append(f"# {card.name}")
        lines.append("")

        # 基本信息
        lines.append("## 📋 基本信息")
        lines.append("")
        lines.append(f"- **版本**: {card.spec} {card.spec_version}")

        if isinstance(card, CharacterCardV3):
            if card.data.creator:
                lines.append(f"- **作者**: {card.data.creator}")
            if card.data.character_version:
                lines.append(f"- **角色版本**: {card.data.character_version}")
        elif isinstance(card, CharacterCardV2):
            if card.creator:
                lines.append(f"- **作者**: {card.creator}")
            if card.character_version:
                lines.append(f"- **角色版本**: {card.character_version}")

        if card.tags:
            lines.append(f"- **标签**: {', '.join(card.tags)}")

        lines.append("")

        # 角色描述
        lines.append("## 📝 角色描述")
        lines.append("")
        lines.append(card.description if card.description else "*无描述*")
        lines.append("")

        # 角色设定
        if card.personality:
            lines.append("## 🎭 角色设定")
            lines.append("")
            lines.append(card.personality)
            lines.append("")

        # 情景
        if card.scenario:
            lines.append("## 🌍 情景设定")
            lines.append("")
            lines.append(card.scenario)
            lines.append("")

        # 第一条消息
        if card.first_mes:
            lines.append("## 💬 开场白")
            lines.append("")
            lines.append(f"> {card.first_mes}")
            lines.append("")

        # 额外开场白
        if isinstance(card, CharacterCardV3):
            alt_greetings = card.data.alternate_greetings
        else:
            alt_greetings = card.alternate_greetings

        if alt_greetings:
            lines.append("### 额外开场白")
            lines.append("")
            for i, greeting in enumerate(alt_greetings, 1):
                lines.append(f"{i}. {greeting}")
                lines.append("")

        # 对话示例
        if card.mes_example:
            lines.append("## 💭 对话示例")
            lines.append("")
            lines.append("```")
            lines.append(card.mes_example)
            lines.append("```")
            lines.append("")

        # 提示词
        if isinstance(card, CharacterCardV3):
            if card.data.system_prompt:
                lines.append("## ⚙️ 系统提示词")
                lines.append("")
                lines.append(f"```\n{card.data.system_prompt}\n```")
                lines.append("")

            if card.data.post_history_instructions:
                lines.append("## 📌 底部提示词")
                lines.append("")
                lines.append(f"```\n{card.data.post_history_instructions}\n```")
                lines.append("")

            if card.data.creator_notes:
                lines.append("## 📖 作者注释")
                lines.append("")
                lines.append(card.data.creator_notes)
                lines.append("")
        elif isinstance(card, CharacterCardV2):
            if card.system_prompt:
                lines.append("## ⚙️ 系统提示词")
                lines.append("")
                lines.append(f"```\n{card.system_prompt}\n```")
                lines.append("")

            if card.post_history_instructions:
                lines.append("## 📌 底部提示词")
                lines.append("")
                lines.append(f"```\n{card.post_history_instructions}\n```")
                lines.append("")

            if card.creator_notes:
                lines.append("## 📖 作者注释")
                lines.append("")
                lines.append(card.creator_notes)
                lines.append("")

        # 世界书统计
        lorebook = None
        if isinstance(card, CharacterCardV3):
            lorebook = card.data.character_book
        elif isinstance(card, CharacterCardV2):
            lorebook = card.character_book

        if lorebook and lorebook.entries:
            lines.append("## 📚 世界书")
            lines.append("")

            # 统计
            green = [e for e in lorebook.entries if not e.constant and not e.extensions.vectorized]
            blue = [e for e in lorebook.entries if e.constant]
            vector = [e for e in lorebook.entries if e.extensions.vectorized]

            lines.append(f"- **总条目数**: {len(lorebook.entries)}")
            lines.append(f"- 🟢 **关键词触发**: {len(green)}")
            lines.append(f"- 🔵 **常驻触发**: {len(blue)}")
            lines.append(f"- 🔗 **向量触发**: {len(vector)}")
            lines.append("")

            # 条目列表
            lines.append("### 条目列表")
            lines.append("")

            for entry in lorebook.entries:
                # 确定类型
                if entry.constant:
                    entry_type = "🔵 常驻"
                elif entry.extensions.vectorized:
                    entry_type = "🔗 向量"
                else:
                    entry_type = "🟢 关键词"

                # 角色类型
                role_emoji = {0: "⚙️", 1: "👤", 2: "🤖"}.get(entry.extensions.role, "")

                lines.append(f"#### {entry_type} {role_emoji} {entry.comment or f'条目 #{entry.id}'}")
                lines.append("")

                if entry.keys:
                    lines.append(f"- **关键词**: {', '.join(entry.keys)}")
                if entry.secondary_keys:
                    lines.append(f"- **次要关键词**: {', '.join(entry.secondary_keys)}")

                lines.append(f"- **插入位置**: {entry.position}")
                lines.append(f"- **深度**: {entry.extensions.depth}")
                lines.append(f"- **优先级**: {entry.insertion_order}")

                if entry.content:
                    lines.append("")
                    lines.append("**内容**:")
                    lines.append("")
                    lines.append(f"```\n{entry.content}\n```")

                lines.append("")

        return "\n".join(lines)

    @staticmethod
    def save_markdown(card: Union[CharacterCardV2, CharacterCardV3], output_path: str):
        """
        保存为Markdown文件

        Args:
            card: 角色卡对象
            output_path: 输出文件路径
        """
        markdown = CharacterCardExporter.to_markdown(card)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)

        print(f"✅ 已导出Markdown: {output_path}")

    @staticmethod
    def export_lorebook(card: Union[CharacterCardV2, CharacterCardV3],
                        output_path: str):
        """
        导出角色卡的世界书为独立JSON

        Args:
            card: 角色卡对象
            output_path: 输出路径
        """
        from lorebook_handler import LorebookHandler

        # 获取世界书
        lorebook = None
        if isinstance(card, CharacterCardV3):
            lorebook = card.data.character_book
        elif isinstance(card, CharacterCardV2):
            lorebook = card.character_book

        if not lorebook:
            print("❌ 该角色卡没有世界书")
            return

        # 保存为独立格式
        LorebookHandler.save_standalone_lorebook(lorebook, output_path)
