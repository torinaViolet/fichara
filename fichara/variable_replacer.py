# variable_replacer.py
"""
变量替换系统
支持内置变量和自定义变量，使用回调函数机制
"""

from typing import Callable, Dict, Any, Optional
import re
from datetime import datetime
import random


class VariableReplacer:
    """变量替换器"""

    # 内置变量的默认回调
    BUILTIN_VARIABLES = {
        "user": lambda ctx: ctx.get("user_name", "User"),
        "char": lambda ctx: ctx.get("char_name", "Character"),
        "time": lambda ctx: datetime.now().strftime("%H:%M"),
        "date": lambda ctx: datetime.now().strftime("%Y-%m-%d"),
        "datetime": lambda ctx: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "random": lambda ctx: str(random.randint(1, 100)),
        "newline": lambda ctx: "\n",
    }

    def __init__(self,
                 user_name: str = "User",
                 char_name: str = "Character"):
        """
        初始化变量替换器

        Args:
            user_name: 用户名
            char_name: 角色名
        """
        self.user_name = user_name
        self.char_name = char_name

        # 变量回调函数字典
        self.variable_callbacks: Dict[str, Callable[[Dict[str, Any]], str]] = {}

        # 注册内置变量
        self._register_builtin_variables()

    def _register_builtin_variables(self):
        """注册内置变量"""
        for var_name, callback in self.BUILTIN_VARIABLES.items():
            self.variable_callbacks[var_name] = callback

    def register_variable(self,
                          var_name: str,
                          callback: Callable[[Dict[str, Any]], str]):
        """
        注册自定义变量

        Args:
            var_name: 变量名（不含{{}}）
            callback: 回调函数，接受上下文字典，返回替换值

        Example:
            replacer.register_variable(
                "weather",
                lambda ctx: "sunny"
            )
        """
        self.variable_callbacks[var_name] = callback
        print(f"✅ 已注册变量: {{{{{{var_name}}}}}}")

    def unregister_variable(self, var_name: str):
        """
        注销变量

        Args:
            var_name: 变量名
        """
        if var_name in self.variable_callbacks:
            del self.variable_callbacks[var_name]
            print(f"✅ 已注销变量: {{{{{{var_name}}}}}}")
        else:
            print(f"⚠️ 变量不存在: {{{{{{var_name}}}}}}")

    def replace(self, text: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        替换文本中的所有变量

        Args:
            text: 原始文本
            context: 上下文字典（可选）

        Returns:
            替换后的文本
        """
        if not text:
            return text

        # 准备上下文
        ctx = self._prepare_context(context)

        # 查找所有变量 {{variable}}
        pattern = r'\{\{([^}]+)\}\}'

        def replace_match(match):
            var_name = match.group(1).strip()
            return self._get_variable_value(var_name, ctx)

        result = re.sub(pattern, replace_match, text)

        return result

    def _prepare_context(self, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """准备上下文"""
        ctx = {
            "user_name": self.user_name,
            "char_name": self.char_name,
        }

        if context:
            ctx.update(context)

        return ctx

    def _get_variable_value(self, var_name: str, context: Dict[str, Any]) -> str:
        """
        获取变量值

        Args:
            var_name: 变量名
            context: 上下文

        Returns:
            变量值
        """
        # 检查是否有回调函数
        if var_name in self.variable_callbacks:
            try:
                return str(self.variable_callbacks[var_name](context))
            except Exception as e:
                print(f"⚠️ 变量 {{{{{{var_name}}}}}} 回调执行失败: {e}")
                return f"{{{{{var_name}}}}}"  # 保留原样
        else:
            # 未知变量，保留原样
            print(f"⚠️ 未知变量: {{{{{{var_name}}}}}}")
            return f"{{{{{var_name}}}}}"

    def list_variables(self):
        """列出所有已注册的变量"""
        print("\n" + "=" * 60)
        print("📋 已注册的变量")
        print("=" * 60)

        # 内置变量
        builtin = [v for v in self.variable_callbacks.keys()
                   if v in self.BUILTIN_VARIABLES]

        # 自定义变量
        custom = [v for v in self.variable_callbacks.keys()
                  if v not in self.BUILTIN_VARIABLES]

        if builtin:
            print("\n🔧 内置变量:")
            for var in sorted(builtin):
                print(f"  {{{{{{var}}}}}}")

        if custom:
            print("\n✏️ 自定义变量:")
            for var in sorted(custom):
                print(f"  {{{{{{var}}}}}}")

        print("=" * 60 + "\n")

    def test_variable(self, var_name: str, context: Optional[Dict[str, Any]] = None):
        """
        测试变量

        Args:
            var_name: 变量名
            context: 上下文
        """
        ctx = self._prepare_context(context)
        value = self._get_variable_value(var_name, ctx)
        print(f"{{{{{{var_name}}}}}} = {value}")

