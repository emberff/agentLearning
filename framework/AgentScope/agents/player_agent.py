# -*- coding: utf-8 -*-
"""
玩家 Agent

所有游戏角色（狼人、村民、预言家、女巫、猎人）
均使用该类，仅角色 Prompt 和技能不同。
"""

from __future__ import annotations

from typing import Optional

from agentscope.agent import (
    Agent,
    ContextConfig,
    ModelConfig,
    ReActConfig,
)
from agentscope.model._base import ChatModelBase

from models.game_state import PlayerState
from utils.utils import create_msg

class PlayerAgent:
    """
    狼人杀玩家

    说明
    ----
    PlayerAgent 不继承 Agent，而是组合（Composition）一个 Agent。

    优点：
        1. 游戏状态与 LLM 解耦
        2. 更符合 AgentScope 2.x 推荐架构
        3. 后续可自由扩展玩家属性
    """

    def __init__(
        self,
        *,
        name: str,
        role: str,
        character: str,
        system_prompt: str,
        model: ChatModelBase,
        model_config: Optional[ModelConfig] = None,
        context_config: Optional[ContextConfig] = None,
        react_config: Optional[ReActConfig] = None,
    ):

        # --------------------------------------------------
        # 基础信息
        # --------------------------------------------------

        self.name = name

        self.role = role

        self.character = character

        # --------------------------------------------------
        # 玩家状态
        # --------------------------------------------------

        self.state = PlayerState(
            name=name,
            role=role,
            character=character,
        )

        # --------------------------------------------------
        # AgentScope Agent
        # --------------------------------------------------

        self.agent = Agent(
            name=name,
            system_prompt=system_prompt,
            model=model,
            model_config=model_config,
            context_config=context_config,
            react_config=react_config,
        )

        # --------------------------------------------------
        # 游戏技能状态
        # --------------------------------------------------

        # 女巫
        self.has_antidote = True
        self.has_poison = True

        # 猎人
        self.can_shoot = True

        # 预言家
        self.checked_today = False

        # 守卫（方便以后扩展）
        self.protected = False

        # --------------------------------------------------
        # 游戏统计
        # --------------------------------------------------

        self.vote_count = 0

        self.survive_days = 0

        self.last_vote_target: Optional[str] = None

        self.last_check_target: Optional[str] = None

        self.last_speak: Optional[str] = None

    # ======================================================
    # 辅助方法
    # ======================================================

    def _get_text_from_content(self, content) -> str:
        """从消息内容中提取纯文本"""
        if isinstance(content, list):
            text_parts = []
            for item in content:
                if hasattr(item, "text"):
                    text_parts.append(item.text)
                elif isinstance(item, str):
                    text_parts.append(item)
            return "\n".join(text_parts) if text_parts else ""
        elif hasattr(content, "text"):
            return content.text
        elif isinstance(content, str):
            return content
        return str(content) if content else ""

    # ======================================================
    # 基础状态
    # ======================================================

    @property
    def alive(self) -> bool:
        """是否存活"""
        return self.state.alive

    @property
    def dead(self) -> bool:
        return not self.state.alive

    @property
    def can_vote(self) -> bool:
        return self.state.can_vote and self.alive

    @property
    def can_speak(self) -> bool:
        return self.state.can_speak and self.alive

    @property
    def is_werewolf(self) -> bool:
        return self.role == "狼人"

    @property
    def is_villager(self) -> bool:
        return self.role == "村民"

    @property
    def is_seer(self) -> bool:
        return self.role == "预言家"

    @property
    def is_witch(self) -> bool:
        return self.role == "女巫"

    @property
    def is_hunter(self) -> bool:
        return self.role == "猎人"

    # ======================================================
    # 状态管理
    # ======================================================

    def kill(self):
        """死亡"""

        self.state.alive = False

    def revive(self):
        """复活"""

        self.state.alive = True

    def disable_vote(self):
        """禁止投票"""

        self.state.can_vote = False

    def enable_vote(self):
        """恢复投票"""

        self.state.can_vote = True

    def disable_speak(self):
        """禁止发言"""

        self.state.can_speak = False

    def enable_speak(self):
        """恢复发言"""

        self.state.can_speak = True

    def next_day(self):
        """
        新的一天开始时调用
        """

        if self.alive:
            self.survive_days += 1

        # 每天恢复
        self.checked_today = False
        self.protected = False

        self.vote_count = 0

        self.last_vote_target = None

    def reset(self):
        """
        重置整个玩家状态（重新开始一局）
        """

        self.state.alive = True
        self.state.can_vote = True
        self.state.can_speak = True

        self.has_antidote = True
        self.has_poison = True

        self.can_shoot = True

        self.checked_today = False

        self.protected = False

        self.vote_count = 0

        self.survive_days = 0

        self.last_vote_target = None

        self.last_check_target = None

        self.last_speak = None

    # ======================================================
    # AgentScope 接口封装
    # ======================================================

    async def observe(self, message):
        """
        将消息加入 Agent 上下文。

        Parameters
        ----------
        message
            Msg 或 Msg 列表。
        """

        return await self.agent.observe(message)

    async def reply(
        self,
        message=None,
    ):
        """
        调用 Agent 回复。

        Parameters
        ----------
        message
            输入消息。

        Returns
        -------
        Agent 回复结果
        """

        return await self.agent.reply(message)

    async def reply_stream(
        self,
        message=None,
    ):
        """
        流式回复。
        """

        async for chunk in self.agent.reply_stream(message):
            yield chunk

    async def compress_context(self):
        """
        压缩上下文。
        """

        return await self.agent.compress_context()

    # ======================================================
    # 游戏行为接口
    # ======================================================

    async def speak(
        self,
        prompt: str,
    ):
        """
        普通发言。

        Parameters
        ----------
        prompt
            主持人发送的提示。

        Returns
        -------
        Agent 回复。
        """

        if not self.can_speak:
            return None

        msg = create_msg("system", prompt, "user")
        result = await self.reply(msg)

        if hasattr(result, "content"):
            self.last_speak = self._get_text_from_content(result.content)
        else:
            self.last_speak = str(result)

        return result

    async def discussion(
        self,
        prompt: str,
    ):
        """
        讨论阶段。
        """

        if not self.can_speak:
            return None

        msg = create_msg("system", prompt, "user")
        result = await self.reply(msg)

        if hasattr(result, "content"):
            self.last_speak = self._get_text_from_content(result.content)

        return result

    async def think(
        self,
        prompt: str,
    ):
        """
        内部推理。

        与 speak 的区别是：
        不广播，仅供 Workflow 使用。
        """
        msg = create_msg("system", prompt, "user")
        return await self.reply(msg)

    # ======================================================
    # 辅助接口
    # ======================================================

    def add_vote(self):
        """
        增加一次被投票数。
        """
        self.vote_count += 1

    def clear_vote(self):
        """
        清空本轮得票数。
        """
        self.vote_count = 0

    def record_vote(self, target: str):
        """
        记录本轮投票目标。
        """
        self.last_vote_target = target

    def record_check(self, target: str):
        """
        记录预言家查验对象。
        """
        self.last_check_target = target

    def record_speak(self, content: str):
        """
        记录最近一次发言。
        """
        self.last_speak = content

    def use_antidote(self) -> bool:
        """
        使用解药。

        Returns
        -------
        bool
            是否成功使用。
        """
        if not self.has_antidote:
            return False

        self.has_antidote = False
        return True

    def use_poison(self) -> bool:
        """
        使用毒药。

        Returns
        -------
        bool
            是否成功使用。
        """
        if not self.has_poison:
            return False

        self.has_poison = False
        return True

    def use_hunter_skill(self) -> bool:
        """
        猎人开枪。

        Returns
        -------
        bool
            是否还能开枪。
        """
        if not self.can_shoot:
            return False

        self.can_shoot = False
        return True

    def mark_checked(self):
        """
        标记本夜已经查验。
        """
        self.checked_today = True

    def protect(self):
        """
        被守卫保护。
        """
        self.protected = True

    def unprotect(self):
        """
        取消保护状态。
        """
        self.protected = False

    def to_dict(self) -> dict:
        """
        转换为字典，方便日志记录或保存状态。
        """
        return {
            "name": self.name,
            "role": self.role,
            "character": self.character,
            "alive": self.alive,
            "can_vote": self.can_vote,
            "can_speak": self.can_speak,
            "vote_count": self.vote_count,
            "survive_days": self.survive_days,
            "last_vote_target": self.last_vote_target,
            "last_check_target": self.last_check_target,
            "last_speak": self.last_speak,
            "has_antidote": self.has_antidote,
            "has_poison": self.has_poison,
            "can_shoot": self.can_shoot,
        }

    def __str__(self) -> str:
        status = "存活" if self.alive else "死亡"
        return f"{self.name}({self.role}) [{status}]"

    def __repr__(self) -> str:
        return self.__str__()

    async def receive(
            self,
            msg: Msg | list[Msg],
    ):
        """
        接收消息（Workflow 调用）。
        """
        await self.observe(msg)