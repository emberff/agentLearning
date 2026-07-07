# -*- coding: utf-8 -*-

"""
白天讨论 Workflow
"""

from __future__ import annotations

from typing import List

from agents.player_agent import PlayerAgent
from agents.moderator_agent import ModeratorAgent

from agentscope.message import Msg


class DiscussionWorkflow:
    """
    白天讨论流程

    功能：

        主持人宣布开始

        玩家依次发言

        发言广播给其他玩家

        保存讨论历史
    """

    @classmethod
    async def run(
        cls,
        moderator: ModeratorAgent,
        players: List[PlayerAgent],
        prompt: str,
        rounds: int = 1,
    ) -> List[Msg]:

        history: List[Msg] = []

        alive_players = [
            p for p in players
            if p.alive
        ]

        moderator.announce(
            "开始讨论。"
        )

        for round_id in range(rounds):

            moderator.announce_round(
                round_id + 1
            )

            for speaker in alive_players:

                # -----------------------------
                # 当前玩家发言
                # -----------------------------

                result = await speaker.speak(
                    prompt
                )

                if result is None:
                    continue

                content = getattr(
                    result,
                    "content",
                    str(result),
                )

                message = Msg(
                    name=speaker.name,
                    role="assistant",
                    content=content,
                )

                history.append(message)

                moderator.announce(
                    f"{speaker.name}：{content}"
                )

                # -----------------------------
                # 广播给其它玩家
                # -----------------------------

                for listener in alive_players:

                    if listener.name == speaker.name:
                        continue

                    await listener.observe(message)

        return history