# -*- coding: utf-8 -*-

"""
Agent 工厂
"""

from __future__ import annotations

from typing import Iterable

from agentscope.agent import (
    ContextConfig,
    ModelConfig,
    ReActConfig,
)

from config.model import ModelFactory

from prompts.prompt import ChinesePrompts

from agents.player_agent import PlayerAgent


class AgentFactory:
    """
    Agent创建工厂

    Game层禁止直接创建PlayerAgent，
    所有Agent均由Factory负责初始化。
    """

    @staticmethod
    def create_player(
        *,
        name: str,
        role: str,
        character: str,
    ) -> PlayerAgent:

        system_prompt = ChinesePrompts.get_role_prompt(
            role=role,
            character=character,
        )

        model = ModelFactory.create_model()

        return PlayerAgent(
            name=name,
            role=role,
            character=character,
            system_prompt=system_prompt,
            model=model,
            model_config=ModelConfig(),
            context_config=ContextConfig(),
            react_config=ReActConfig(),
        )

    @classmethod
    def create_players(
        cls,
        roles: Iterable[str],
        characters: Iterable[str],
    ) -> list[PlayerAgent]:

        players = []

        for role, character in zip(
            roles,
            characters,
        ):

            players.append(
                cls.create_player(
                    name=character,
                    role=role,
                    character=character,
                )
            )

        return players