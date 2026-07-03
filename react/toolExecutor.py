from typing import Dict, Any


class ToolExecutor:
    """
    工具执行器
    """

    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}

    def registerTool(self, name: str, description: str, func: callable):
        if name in self.tools:
            print(f"警告：工具{name}已存在，将被覆盖。")

        self.tools[name] = {
            "description": description,
            "func": func
        }

        print(f"工具 {name} 注册成功")

    def execute(self, tool_name: str, tool_input: str):
        """
        执行工具，统一返回(success, observation)
        """

        tool = self.tools.get(tool_name)

        if tool is None:
            return False, (
                f"工具 '{tool_name}' 不存在。\n"
                f"可用工具：{', '.join(self.tools.keys())}"
            )

        try:

            result = tool["func"](tool_input)

            if result is None or str(result).strip() == "":
                return False, (
                    f"工具 '{tool_name}' 没有返回有效结果。"
                )

            return True, result

        except Exception as e:

            return False, (
                f"工具 '{tool_name}' 执行失败：{str(e)}"
            )

    def getAvailableTools(self):

        return "\n".join([
            f"- {name}: {info['description']}"
            for name, info in self.tools.items()
        ])