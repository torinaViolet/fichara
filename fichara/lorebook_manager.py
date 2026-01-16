# lorebook_manager.py
"""
世界书管理器
提供世界书条目的增删改查、合并、排序等功能
"""

from typing import List, Dict, Optional, Tuple, Callable
from models import CharacterBook, WorldBookEntry, WorldBookEntryExtensions
from copy import deepcopy


class LorebookManager:
    """世界书管理器"""

    def __init__(self, character_book: CharacterBook):
        """
        初始化世界书管理器

        Args:
            character_book: 角色世界书对象
        """
        self.book = character_book

    # ============ 基础操作 ============

    def add_entry(self, entry: WorldBookEntry) -> int:
        """
        添加新条目

        Args:
            entry: 世界书条目

        Returns:
            新条目的ID
        """
        # 自动分配ID
        if entry.id is None or self.get_entry(entry.id) is not None:
            entry.id = self._get_next_id()

        self.book.entries.append(entry)
        print(f"✅ 已添加条目: {entry.comment} (ID: {entry.id})")

        return entry.id

    def remove_entry(self, entry_id: int) -> bool:
        """
        删除条目

        Args:
            entry_id: 条目ID

        Returns:
            是否删除成功
        """
        original_count = len(self.book.entries)
        self.book.entries = [e for e in self.book.entries if e.id != entry_id]

        if len(self.book.entries) < original_count:
            print(f"✅ 已删除条目 ID: {entry_id}")
            return True
        else:
            print(f"❌ 未找到条目 ID: {entry_id}")
            return False

    def get_entry(self, entry_id: int) -> Optional[WorldBookEntry]:
        """
        获取指定ID的条目

        Args:
            entry_id: 条目ID

        Returns:
            条目对象，如果不存在则返回None
        """
        for entry in self.book.entries:
            if entry.id == entry_id:
                return entry
        return None

    def update_entry(self, entry_id: int, **kwargs) -> bool:
        """
        更新条目字段

        Args:
            entry_id: 条目ID
            **kwargs: 要更新的字段

        Returns:
            是否更新成功
        """
        entry = self.get_entry(entry_id)
        if not entry:
            print(f"❌ 未找到条目 ID: {entry_id}")
            return False

        # 更新字段
        for key, value in kwargs.items():
            if hasattr(entry, key):
                setattr(entry, key, value)
            elif hasattr(entry.extensions, key):
                setattr(entry.extensions, key, value)
            else:
                print(f"⚠️ 未知字段: {key}")

        print(f"✅ 已更新条目 ID: {entry_id}")
        return True

    def duplicate_entry(self, entry_id: int) -> Optional[int]:
        """
        复制条目

        Args:
            entry_id: 要复制的条目ID

        Returns:
            新条目的ID，失败返回None
        """
        original = self.get_entry(entry_id)
        if not original:
            print(f"❌ 未找到条目 ID: {entry_id}")
            return None

        # 深拷贝
        new_entry = deepcopy(original)
        new_entry.id = self._get_next_id()
        new_entry.comment = f"{original.comment} (副本)"

        self.book.entries.append(new_entry)
        print(f"✅ 已复制条目: {new_entry.comment} (新ID: {new_entry.id})")

        return new_entry.id

    # ============ 查询功能 ============

    def find_by_keyword(self, keyword: str, case_sensitive: bool = False) -> List[WorldBookEntry]:
        """
        根据关键词查找条目

        Args:
            keyword: 关键词
            case_sensitive: 是否区分大小写

        Returns:
            包含该关键词的条目列表
        """
        results = []

        if not case_sensitive:
            keyword = keyword.lower()

        for entry in self.book.entries:
            # 在主关键词中查找
            keys_to_search = entry.keys if case_sensitive else [k.lower() for k in entry.keys]
            if any(keyword in k for k in keys_to_search):
                results.append(entry)
                continue

            # 在次要关键词中查找
            secondary_keys = entry.secondary_keys if case_sensitive else [k.lower() for k in entry.secondary_keys]
            if any(keyword in k for k in secondary_keys):
                results.append(entry)
                continue

            # 在注释中查找
            comment = entry.comment if case_sensitive else entry.comment.lower()
            if keyword in comment:
                results.append(entry)
                continue

            # 在内容中查找
            content = entry.content if case_sensitive else entry.content.lower()
            if keyword in content:
                results.append(entry)

        return results

    def find_by_type(self, entry_type: str) -> List[WorldBookEntry]:
        """
        根据类型查找条目

        Args:
            entry_type: 'green'(关键词), 'blue'(常驻), 'vector'(向量)

        Returns:
            指定类型的条目列表
        """
        if entry_type == 'green':
            return [e for e in self.book.entries
                    if not e.constant and not e.extensions.vectorized]
        elif entry_type == 'blue':
            return [e for e in self.book.entries if e.constant]
        elif entry_type == 'vector':
            return [e for e in self.book.entries if e.extensions.vectorized]
        else:
            print(f"❌ 未知类型: {entry_type}")
            return []

    def find_by_position(self, position: int) -> List[WorldBookEntry]:
        """
        根据插入位置查找条目

        Args:
            position: 位置编号 (0-7)

        Returns:
            指定位置的条目列表
        """
        return [e for e in self.book.entries if e.extensions.position == position]

    def find_by_role(self, role: int) -> List[WorldBookEntry]:
        """
        根据角色类型查找条目

        Args:
            role: 0=System, 1=User, 2=Assistant

        Returns:
            指定角色的条目列表
        """
        return [e for e in self.book.entries if e.extensions.role == role]

    def find_by_depth(self, min_depth: int = None, max_depth: int = None) -> List[WorldBookEntry]:
        """
        根据深度范围查找条目

        Args:
            min_depth: 最小深度
            max_depth: 最大深度

        Returns:
            符合深度范围的条目列表
        """
        results = []
        for entry in self.book.entries:
            depth = entry.extensions.depth
            if min_depth is not None and depth < min_depth:
                continue
            if max_depth is not None and depth > max_depth:
                continue
            results.append(entry)
        return results

    def find_empty_entries(self) -> List[WorldBookEntry]:
        """
        查找空内容的条目

        Returns:
            内容为空的条目列表
        """
        return [e for e in self.book.entries
                if not e.content or e.content.strip() == ""]

    def find_no_keywords_entries(self) -> List[WorldBookEntry]:
        """
        查找没有关键词的绿灯条目（可能有问题）

        Returns:
            没有关键词的绿灯条目列表
        """
        return [e for e in self.book.entries
                if not e.constant
                and not e.extensions.vectorized
                and not e.keys
                and not e.secondary_keys]

    def find_duplicates(self) -> List[Tuple[int, int]]:
        """
        查找重复的条目ID

        Returns:
            重复ID的列表
        """
        ids = [e.id for e in self.book.entries]
        duplicates = []
        seen = set()

        for id in ids:
            if id in seen:
                duplicates.append(id)
            seen.add(id)

        return [(id, id) for id in set(duplicates)]

    def find_by_filter(self, filter_func: Callable[[WorldBookEntry], bool]) -> List[WorldBookEntry]:
        """
        使用自定义过滤函数查找条目

        Args:
            filter_func: 过滤函数，接受 WorldBookEntry，返回 bool

        Returns:
            符合条件的条目列表

        Example:
            # 查找深度大于5且已启用的条目
            results = manager.find_by_filter(
                lambda e: e.extensions.depth > 5 and e.enabled
            )
        """
        return [e for e in self.book.entries if filter_func(e)]

    # ============ 批量操作 ============

    def batch_update(self, entry_ids: List[int], **kwargs) -> int:
        """
        批量更新条目

        Args:
            entry_ids: 条目ID列表
            **kwargs: 要更新的字段

        Returns:
            成功更新的数量
        """
        count = 0
        for entry_id in entry_ids:
            if self.update_entry(entry_id, **kwargs):
                count += 1

        print(f"✅ 批量更新完成: {count}/{len(entry_ids)}")
        return count

    def batch_delete(self, entry_ids: List[int]) -> int:
        """
        批量删除条目

        Args:
            entry_ids: 条目ID列表

        Returns:
            成功删除的数量
        """
        count = 0
        for entry_id in entry_ids:
            if self.remove_entry(entry_id):
                count += 1

        print(f"✅ 批量删除完成: {count}/{len(entry_ids)}")
        return count

    def enable_all(self):
        """启用所有条目"""
        for entry in self.book.entries:
            entry.enabled = True
        print(f"✅ 已启用所有 {len(self.book.entries)} 个条目")

    def disable_all(self):
        """禁用所有条目"""
        for entry in self.book.entries:
            entry.enabled = False
        print(f"✅ 已禁用所有 {len(self.book.entries)} 个条目")

    def enable_by_type(self, entry_type: str):
        """
        按类型启用条目

        Args:
            entry_type: 'green', 'blue', 'vector'
        """
        entries = self.find_by_type(entry_type)
        for entry in entries:
            entry.enabled = True
        print(f"✅ 已启用 {len(entries)} 个 {entry_type} 条目")

    def disable_by_type(self, entry_type: str):
        """
        按类型禁用条目

        Args:
            entry_type: 'green', 'blue', 'vector'
        """
        entries = self.find_by_type(entry_type)
        for entry in entries:
            entry.enabled = False
        print(f"✅ 已禁用 {len(entries)} 个 {entry_type} 条目")

    # ============ 排序功能 ============

    def sort_entries(self, by: str = "display_index", reverse: bool = False):
        """
        排序条目

        Args:
            by: 排序依据 ('id', 'display_index', 'insertion_order', 'depth', 'comment')
            reverse: 是否倒序
        """
        if by == "id":
            self.book.entries.sort(key=lambda e: e.id, reverse=reverse)
        elif by == "display_index":
            self.book.entries.sort(key=lambda e: e.extensions.display_index, reverse=reverse)
        elif by == "insertion_order":
            self.book.entries.sort(key=lambda e: e.insertion_order, reverse=reverse)
        elif by == "depth":
            self.book.entries.sort(key=lambda e: e.extensions.depth, reverse=reverse)
        elif by == "comment":
            self.book.entries.sort(key=lambda e: e.comment, reverse=reverse)
        else:
            print(f"❌ 未知排序字段: {by}")
            return

        print(f"✅ 已按 {by} 排序 ({'倒序' if reverse else '正序'})")

    def reindex_display_order(self):
        """
        重新分配 display_index（按当前顺序从0开始）
        """
        for i, entry in enumerate(self.book.entries):
            entry.extensions.display_index = i
        print(f"✅ 已重新分配显示顺序: 0-{len(self.book.entries) - 1}")

    # ============ 合并功能 ============

    def merge_with(self, other_book: CharacterBook,
                   conflict_strategy: str = "keep_both") -> int:
        """
        合并另一个世界书

        Args:
            other_book: 要合并的世界书
            conflict_strategy: 冲突策略
                - 'keep_both': 保留两者（重新分配ID）
                - 'keep_original': 保留原有的
                - 'keep_new': 使用新的覆盖

        Returns:
            新增的条目数量
        """
        added_count = 0

        for entry in other_book.entries:
            existing = self.get_entry(entry.id)

            if existing is None:
                # 没有冲突，直接添加
                new_entry = deepcopy(entry)
                self.book.entries.append(new_entry)
                added_count += 1
            else:
                # 有冲突，根据策略处理
                if conflict_strategy == "keep_both":
                    new_entry = deepcopy(entry)
                    new_entry.id = self._get_next_id()
                    new_entry.comment = f"{entry.comment} (合并)"
                    self.book.entries.append(new_entry)
                    added_count += 1
                elif conflict_strategy == "keep_new":
                    # 替换现有条目
                    idx = self.book.entries.index(existing)
                    self.book.entries[idx] = deepcopy(entry)
                    added_count += 1
                # keep_original 则不做任何操作

        print(f"✅ 合并完成: 新增 {added_count} 个条目")
        return added_count

    # ============ 统计功能 ============

    def get_statistics(self) -> Dict:
        """
        获取世界书统计信息

        Returns:
            统计信息字典
        """
        entries = self.book.entries

        green = [e for e in entries if not e.constant and not e.extensions.vectorized]
        blue = [e for e in entries if e.constant]
        vector = [e for e in entries if e.extensions.vectorized]

        enabled = [e for e in entries if e.enabled]
        disabled = [e for e in entries if not e.enabled]

        empty = self.find_empty_entries()
        no_keywords = self.find_no_keywords_entries()

        # 按位置统计
        position_stats = {}
        position_names = {
            0: "角色定义之前",
            1: "角色定义之后",
            2: "作者注释之前",
            3: "作者注释之后",
            4: "@D 在深度",
            5: "示例消息前",
            6: "示例消息后",
            7: "Outlet"
        }
        for entry in entries:
            pos = entry.extensions.position
            pos_name = position_names.get(pos, f"位置{pos}")
            position_stats[pos_name] = position_stats.get(pos_name, 0) + 1

        # 按角色统计
        role_stats = {0: 0, 1: 0, 2: 0}
        for entry in entries:
            role = entry.extensions.role
            role_stats[role] = role_stats.get(role, 0) + 1

        # 深度分布
        depth_distribution = {}
        for entry in entries:
            depth = entry.extensions.depth
            depth_distribution[depth] = depth_distribution.get(depth, 0) + 1

        # 计算总token估算（粗略）
        total_content_length = sum(len(e.content) for e in entries)
        estimated_tokens = total_content_length // 4  # 粗略估算

        return {
            "total": len(entries),
            "by_type": {
                "green": len(green),
                "blue": len(blue),
                "vector": len(vector)
            },
            "by_status": {
                "enabled": len(enabled),
                "disabled": len(disabled)
            },
            "by_position": position_stats,
            "by_role": {
                "system": role_stats[0],
                "user": role_stats[1],
                "assistant": role_stats[2]
            },
            "depth_distribution": depth_distribution,
            "issues": {
                "empty_entries": len(empty),
                "no_keywords": len(no_keywords),
                "has_duplicates": len(self.find_duplicates()) > 0
            },
            "content": {
                "total_characters": total_content_length,
                "estimated_tokens": estimated_tokens
            }
        }

    def print_statistics(self):
        """打印统计信息"""
        stats = self.get_statistics()

        print("\n" + "=" * 60)
        print("📚 世界书统计信息")
        print("=" * 60)

        print(f"\n📊 总条目数: {stats['total']}")

        print("\n🎨 按类型:")
        print(f"  🟢 关键词触发: {stats['by_type']['green']}")
        print(f"  🔵 常驻触发: {stats['by_type']['blue']}")
        print(f"  🔗 向量触发: {stats['by_type']['vector']}")

        print("\n⚡ 按状态:")
        print(f"  ✅ 已启用: {stats['by_status']['enabled']}")
        print(f"  ❌ 已禁用: {stats['by_status']['disabled']}")

        print("\n👥 按角色:")
        print(f"  ⚙️ 系统: {stats['by_role']['system']}")
        print(f"  👤 用户: {stats['by_role']['user']}")
        print(f"  🤖 AI: {stats['by_role']['assistant']}")

        print("\n📍 按位置:")
        for pos, count in sorted(stats['by_position'].items()):
            print(f"  {pos}: {count}")

        print("\n📏 深度分布:")
        for depth, count in sorted(stats['depth_distribution'].items()):
            print(f"  深度 {depth}: {count} 个条目")

        print("\n📝 内容统计:")
        print(f"  总字符数: {stats['content']['total_characters']}")
        print(f"  估算Token: ~{stats['content']['estimated_tokens']}")

        if stats['issues']['empty_entries'] > 0:
            print(f"\n⚠️ 空内容条目: {stats['issues']['empty_entries']}")

        if stats['issues']['no_keywords'] > 0:
            print(f"⚠️ 无关键词的绿灯条目: {stats['issues']['no_keywords']}")

        if stats['issues']['has_duplicates']:
            print(f"⚠️ 发现重复ID")

        print("=" * 60 + "\n")

    def export_summary(self) -> str:
        """
        导出简要摘要（适合快速查看）

        Returns:
            摘要文本
        """
        stats = self.get_statistics()
        lines = []

        lines.append(f"世界书: {self.book.name or '未命名'}")
        lines.append(
            f"总条目: {stats['total']} (🟢{stats['by_type']['green']} 🔵{stats['by_type']['blue']} 🔗{stats['by_type']['vector']})")
        lines.append(f"状态: ✅{stats['by_status']['enabled']} ❌{stats['by_status']['disabled']}")

        if stats['issues']['empty_entries'] > 0 or stats['issues']['no_keywords'] > 0:
            lines.append(f"⚠️ 问题: 空内容{stats['issues']['empty_entries']} 无关键词{stats['issues']['no_keywords']}")

        return " | ".join(lines)

    # ============ 辅助方法 ============

    def _get_next_id(self) -> int:
        """获取下一个可用的ID"""
        if not self.book.entries:
            return 0

        max_id = max(e.id for e in self.book.entries)
        return max_id + 1

    def create_entry(self,
                     comment: str,
                     content: str = "",
                     keys: List[str] = None,
                     entry_type: str = "green",
                     position: str = "before_char",
                     depth: int = 4,
                     role: int = 0) -> WorldBookEntry:
        """
        快速创建条目

        Args:
            comment: 注释
            content: 内容
            keys: 关键词列表
            entry_type: 类型 ('green', 'blue', 'vector')
            position: 插入位置
            depth: 深度
            role: 角色类型 (0=System, 1=User, 2=Assistant)

        Returns:
            新创建的条目
        """
        # 转换position字符串到数字
        position_map = {
            "before_char": 0,
            "after_char": 1,
        }
        position_num = position_map.get(position, 0)

        entry = WorldBookEntry(
            id=self._get_next_id(),
            comment=comment,
            content=content,
            keys=keys or [],
            constant=(entry_type == "blue"),
            position=position,
            extensions=WorldBookEntryExtensions(
                depth=depth,
                vectorized=(entry_type == "vector"),
                role=role,
                position=position_num
            )
        )

        return entry

    def clear_all(self):
        """清空所有条目（危险操作！）"""
        count = len(self.book.entries)
        self.book.entries = []
        print(f"⚠️ 已清空所有 {count} 个条目")


# ============ 使用示例 ============

if __name__ == '__main__':
    from png_handler import load_card_data
    from models import parse_character_card, CharacterCardV3

    print("=" * 60)
    print("世界书管理器测试")
    print("=" * 60)

    # 加载角色卡
    raw_data = load_card_data(r"C:\Users\Violet\Downloads\测试.png")
    card = parse_character_card(raw_data)

    if isinstance(card, CharacterCardV3) and card.data.character_book:
        # 创建管理器
        manager = LorebookManager(card.data.character_book)

        # 显示统计
        manager.print_statistics()

        # 显示摘要
        print("\n📋 快速摘要:")
        print(manager.export_summary())

        # 查找空条目
        print("\n🔍 查找空内容条目...")
        empty = manager.find_empty_entries()
        print(f"找到 {len(empty)} 个空条目")
        for e in empty[:3]:  # 只显示前3个
            print(f"  - ID {e.id}: {e.comment}")

        # 查找没有关键词的绿灯条目
        print("\n🔍 查找无关键词的绿灯条目...")
        no_kw = manager.find_no_keywords_entries()
        print(f"找到 {len(no_kw)} 个")

        # 按深度查找
        print("\n🔍 查找深度4-6的条目...")
        depth_entries = manager.find_by_depth(4, 6)
        print(f"找到 {len(depth_entries)} 个")

        # 自定义过滤
        print("\n🔍 自定义查找: 已启用且深度>3的蓝灯条目...")
        custom = manager.find_by_filter(
            lambda e: e.enabled and e.constant and e.extensions.depth > 3
        )
        print(f"找到 {len(custom)} 个")

        # 复制条目
        if manager.book.entries:
            print("\n📋 复制第一个条目...")
            first_id = manager.book.entries[0].id
            new_id = manager.duplicate_entry(first_id)
            print(f"新条目ID: {new_id}")

        # 最终统计
        print("\n" + "=" * 60)
        manager.print_statistics()
    else:
        print("❌ 该角色卡没有世界书")
