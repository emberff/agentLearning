# -*- coding: utf-8 -*-

"""
游戏主持人
"""

from __future__ import annotations

from typing import Iterable


class ModeratorAgent:
    """
    游戏主持人

    不依赖LLM，仅负责：

    - 公告
    - 夜晚提示
    - 白天提示
    - 投票结果
    - 游戏结束
    """

    def __init__(self):

        self.name = "主持人"

        self.logs: list[str] = []

    def log(self, message: str):
        """保存日志"""

        self.logs.append(message)

    def announce(self, message: str):

        self.log(message)

        print(f"\n【{self.name}】{message}")

    def night_begin(self, day: int):

        self.announce(
            f"========== 第 {day} 夜 =========="
        )

    def day_begin(self, day: int):

        self.announce(
            f"========== 第 {day} 天 =========="
        )

    def announce_dead_players(
        self,
        players: Iterable[str],
    ):

        players = list(players)

        if len(players) == 0:

            self.announce("昨夜是平安夜。")

            return

        self.announce(
            "昨夜死亡玩家：" +
            "、".join(players)
        )

    def announce_vote_result(
        self,
        player: str,
        votes: int,
    ):

        self.announce(
            f"{player} 被放逐（{votes}票）。"
        )

    def announce_game_over(
        self,
        winner: str,
    ):

        self.announce(
            f"游戏结束，{winner} 获胜！"
        )

    def announce_role(
        self,
        player: str,
        role: str,
    ):

        self.announce(
            f"{player} 的身份是【{role}】"
        )

    def announce_round(self, round_id: int):

        self.announce(
            f"========== 第 {round_id} 轮讨论 =========="
        )

    def separator(self):

        print("-" * 60)

    def get_logs(self):

        return self.logs.copy()