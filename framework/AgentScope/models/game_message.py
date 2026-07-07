# -*- coding: utf-8 -*-
"""
游戏消息模块

提供游戏中使用的消息类和工具函数
"""

from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum


class MessageType(Enum):
    """消息类型枚举"""
    ANNOUNCEMENT = "announcement"
    DISCUSSION = "discussion"
    VOTE = "vote"
    ACTION = "action"
    SYSTEM = "system"


@dataclass
class GameMessage:
    """
    游戏消息类
    
    用于在游戏流程中传递消息
    """
    
    content: str
    message_type: MessageType = MessageType.ANNOUNCEMENT
    sender: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "content": self.content,
            "message_type": self.message_type.value,
            "sender": self.sender,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GameMessage":
        """从字典创建对象"""
        return cls(
            content=data.get("content", ""),
            message_type=MessageType(data.get("message_type", "announcement")),
            sender=data.get("sender"),
            metadata=data.get("metadata", {}),
            timestamp=data.get("timestamp")
        )


def create_announcement(content: str, metadata: Optional[Dict] = None) -> GameMessage:
    """
    创建公告消息
    
    Args:
        content: 公告内容
        metadata: 附加元数据
    
    Returns:
        GameMessage 对象
    """
    return GameMessage(
        content=content,
        message_type=MessageType.ANNOUNCEMENT,
        sender="主持人",
        metadata=metadata or {}
    )


def create_action_message(
    content: str, 
    sender: str, 
    metadata: Optional[Dict] = None
) -> GameMessage:
    """
    创建行动消息
    
    Args:
        content: 消息内容
        sender: 发送者
        metadata: 附加元数据
    
    Returns:
        GameMessage 对象
    """
    return GameMessage(
        content=content,
        message_type=MessageType.ACTION,
        sender=sender,
        metadata=metadata or {}
    )


def create_vote_message(
    voter: str, 
    target: str, 
    reason: str = "",
    suspicion: int = 5
) -> GameMessage:
    """
    创建投票消息
    
    Args:
        voter: 投票者
        target: 被投票者
        reason: 投票理由
        suspicion: 怀疑程度
    
    Returns:
        GameMessage 对象
    """
    return GameMessage(
        content=f"{voter} 投票给 {target}",
        message_type=MessageType.VOTE,
        sender=voter,
        metadata={
            "voter": voter,
            "target": target,
            "reason": reason,
            "suspicion": suspicion
        }
    )


def create_discussion_message(
    speaker: str,
    content: str,
    metadata: Optional[Dict] = None
) -> GameMessage:
    """
    创建讨论消息
    
    Args:
        speaker: 发言者
        content: 发言内容
        metadata: 附加元数据
    
    Returns:
        GameMessage 对象
    """
    return GameMessage(
        content=content,
        message_type=MessageType.DISCUSSION,
        sender=speaker,
        metadata=metadata or {}
    )
