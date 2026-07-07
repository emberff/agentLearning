# -*- coding: utf-8 -*-
"""
全局配置
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelSettings:
    """模型配置"""

    MODEL_NAME: str = "qwen-max"

    TEMPERATURE: float = 0.7

    TOP_P: float = 0.9

    MAX_TOKENS: int = 4096


@dataclass(frozen=True)
class AgentSettings:
    """Agent配置"""

    # 是否自动压缩上下文
    AUTO_COMPRESS_CONTEXT: bool = True

    # 最大上下文轮数
    MAX_CONTEXT_MESSAGES: int = 30

    # 是否开启ReAct
    ENABLE_REACT: bool = False


@dataclass(frozen=True)
class GameSettings:
    """游戏配置"""

    DISCUSSION_ROUNDS: int = 2

    MAX_GAME_DAYS: int = 20

    VOTE_TIMEOUT: int = 120

    ENABLE_LOG: bool = True


@dataclass(frozen=True)
class RoleSettings:
    """角色技能配置"""

    WITCH_HAS_ANTIDOTE: bool = True

    WITCH_HAS_POISON: bool = True

    HUNTER_CAN_SHOOT: bool = True

    SEER_CHECK_PER_NIGHT: int = 1