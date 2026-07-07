import re

from LLMCilent import HelloAgentsLLM
from paradigm.react.toolExecutor import ToolExecutor


# ReAct 提示词模板
REACT_PROMPT_TEMPLATE = """
请注意，你是一个有能力调用外部工具的智能助手。

可用工具如下:
{tools}

请严格按照以下格式进行回应:

Thought: 你的思考过程，用于分析问题、拆解任务和规划下一步行动。
Action: 你决定采取的行动，必须是以下格式之一:
- `{{tool_name}}[{{tool_input}}]`:调用一个可用工具。
- `Finish[最终答案]`:当你认为已经获得最终答案时。
- 当你收集到足够的信息，能够回答用户的最终问题时，你必须在Action:字段后使用 Finish[最终答案] 来输出最终答案。

现在，请开始解决以下问题:
Question: {question}
History: {history}
"""


class ReActAgent:
    def __init__(self, llm_client: HelloAgentsLLM, tool_executor: ToolExecutor, max_steps: int = 5):
        self.llm_client = llm_client
        self.tool_executor = tool_executor
        self.max_steps = max_steps
        self.history = []
        self.failed_count = 0
        self.same_tool_failed = 0
        self.last_failed_tool = None

    def run(self, question: str):

        self.history = []

        self.failed_count = 0
        self.same_tool_failed = 0
        self.last_failed_tool = None

        current_step = 0

        while current_step < self.max_steps:

            current_step += 1

            print(f"--- 第{current_step}步 ---")

            tools_desc = self.tool_executor.getAvailableTools()

            history_str = "\n".join(self.history)

            prompt = REACT_PROMPT_TEMPLATE.format(
                tools=tools_desc,
                question=question,
                history=history_str
            )

            messages = [
                {
                    "roles": "user",
                    "content": prompt
                }
            ]

            response = self.llm_client.think(messages)

            if not response:
                break

            thought, action = self._parse_output(response)

            if thought:
                print("Thought:", thought)

            if not action:
                print("无法解析Action")
                break

            if action.startswith("Finish"):
                answer = re.match(
                    r"Finish\[(.*)\]",
                    action,
                    re.DOTALL
                ).group(1)

                print(answer)

                return answer

            tool_name, tool_input = self._parse_action(action)

            if tool_name is None:
                observation = (
                    "Action格式错误。\n"
                    "正确格式：ToolName[input]"
                )

                self.history.append(f"Action:{action}")
                self.history.append(f"Observation:{observation}")

                continue

            print(f"Action：{tool_name}[{tool_input}]")

            success, observation = self.tool_executor.execute(
                tool_name,
                tool_input
            )

            # ========= Tool Error Recovery =========

            if success:

                self.failed_count = 0
                self.same_tool_failed = 0
                self.last_failed_tool = None

            else:

                self.failed_count += 1

                if self.last_failed_tool == tool_name:
                    self.same_tool_failed += 1
                else:
                    self.same_tool_failed = 1

                self.last_failed_tool = tool_name

                if self.same_tool_failed >= 2:
                    observation += (
                        "\n\n你已经连续两次调用同一个失败工具。"
                        "\n请不要继续重复调用它。"
                        "\n请重新分析问题，并尝试其它工具。"
                    )

                if self.failed_count >= 3:
                    observation += (
                        "\n\n工具已经连续失败三次。"
                        "\n请重新思考："
                        "\n1. 是否工具选择错误？"
                        "\n2. 是否参数格式错误？"
                        "\n3. 是否应该换一个工具？"
                    )

                if self.failed_count >= 5:
                    print("工具连续失败次数过多，停止执行。")

                    return "工具调用连续失败，任务终止。"

            # ======================================

            print("Observation:")
            print(observation)

            self.history.append(f"Action: {action}")
            self.history.append(f"Observation: {observation}")

        print("达到最大推理步数")

        return None

    def _parse_output(self, text: str):
        """解析LLM的输出，提取Thought和Action。
        """
        # Thought: 匹配到 Action: 或文本末尾
        thought_match = re.search(r"Thought:\s*(.*?)(?=\nAction:|$)", text, re.DOTALL)
        # Action: 匹配到文本末尾
        action_match = re.search(r"Action:\s*(.*?)$", text, re.DOTALL)
        thought = thought_match.group(1).strip() if thought_match else None
        action = action_match.group(1).strip() if action_match else None
        return thought, action

    def _parse_action(self, action_text: str):
        """解析Action字符串，提取工具名称和输入。
        """
        match = re.match(r"(\w+)\[(.*)\]", action_text, re.DOTALL)
        if match:
            return match.group(1), match.group(2)
        return None, None


if __name__ == "__main__":
    from paradigm.react.tool.calculator import calculator

    llm = HelloAgentsLLM()

    tool_executor = ToolExecutor()

    tool_executor.registerTool(
        "Calculator",
        "可以回答任何问题。",
        calculator
    )

    agent = ReActAgent(llm, tool_executor)

    answer = agent.run("苏州天气？")

    print(answer)