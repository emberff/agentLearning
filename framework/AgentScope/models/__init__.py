"""
数据模型模块
"""
from agentscope.message import Msg

from .structured_output import (
    DiscussionOutput,
    get_vote_model,
    get_seer_model,
    get_hunter_model,
    get_witch_model,
    # 中文版模型
    DiscussionModelCN,
    get_vote_model_cn,
    WitchActionModelCN,
    get_seer_model_cn,
    get_hunter_model_cn,
    get_wolf_kill_model_cn,
)

from .game_message import (
    GameMessage,
    MessageType,
    create_announcement,
    create_action_message,
    create_vote_message,
    create_discussion_message,
)

from .game_state import PlayerState

__all__ = [
    # 基础模型
    "DiscussionOutput",
    "get_vote_model",
    "get_seer_model",
    "get_hunter_model",
    "get_witch_model",
    # 中文版模型
    "DiscussionModelCN",
    "get_vote_model_cn",
    "WitchActionModelCN",
    "get_seer_model_cn",
    "get_hunter_model_cn",
    "get_wolf_kill_model_cn",
    # 消息相关
    "GameMessage",
    "MessageType",
    "create_announcement",
    "create_action_message",
    "create_vote_message",
    "create_discussion_message",
    # 游戏状态
    "PlayerState",
]