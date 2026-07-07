from typing import Literal, Optional, List

from pydantic import BaseModel, Field


class DiscussionOutput(BaseModel):
    """讨论阶段"""

    content: str = Field(
        description="你的发言内容"
    )

    reach_agreement: bool = Field(
        description="是否认为已形成共识"
    )

    confidence: int = Field(
        ge=1,
        le=10,
        description="推理可信度"
    )


def get_vote_model(players: list[str]):

    class VoteOutput(BaseModel):

        vote: Literal[tuple(players)] = Field(
            description="投票对象"
        )

        reason: str = Field(
            description="投票理由"
        )

        suspicion: int = Field(
            ge=1,
            le=10,
            description="怀疑程度"
        )

    return VoteOutput


def get_seer_model(players: list[str]):

    class SeerOutput(BaseModel):

        target: Literal[tuple(players)] = Field(
            description="查验对象"
        )

        reason: str = Field(
            description="查验原因"
        )

    return SeerOutput


def get_hunter_model(players: list[str]):

    class HunterOutput(BaseModel):

        shoot: bool = Field(
            description="是否开枪"
        )

        target: Optional[
            Literal[tuple(players)]
        ] = None

        reason: Optional[str] = None

    return HunterOutput


def get_witch_model(players: list[str]):

    class WitchOutput(BaseModel):

        use_antidote: bool = False

        use_poison: bool = False

        target: Optional[
            Literal[tuple(players)]
        ] = None

        reason: Optional[str] = None

    return WitchOutput


# 中文版模型 - 适配 AgentScope 的 Msg 和 metadata
class DiscussionModelCN(BaseModel):
    """中文版讨论阶段模型"""
    
    content: str = Field(
        description="你的发言内容"
    )
    
    reach_agreement: bool = Field(
        description="是否认为已形成共识"
    )
    
    confidence: int = Field(
        ge=1,
        le=10,
        description="推理可信度"
    )


def get_vote_model_cn(players: list):
    """
    获取中文版投票模型
    
    Args:
        players: 玩家对象列表或玩家名称列表
    
    Returns:
        Pydantic 模型类
    """
    player_names = []
    for p in players:
        if hasattr(p, 'name'):
            player_names.append(p.name)
        else:
            player_names.append(str(p))
    
    class VoteOutputCN(BaseModel):
        vote: Literal[tuple(player_names)] = Field(
            description="投票对象，必须是当前存活的玩家之一"
        )
        
        reason: str = Field(
            description="投票理由，简要说明为什么投票给该玩家"
        )
        
        suspicion: int = Field(
            ge=1,
            le=10,
            description="对该玩家的怀疑程度，1-10分"
        )
    
    return VoteOutputCN


class WitchActionModelCN(BaseModel):
    """中文版女巫行动模型"""
    
    use_antidote: bool = Field(
        default=False,
        description="是否使用解药"
    )
    
    use_poison: bool = Field(
        default=False,
        description="是否使用毒药"
    )
    
    target_name: Optional[str] = Field(
        default=None,
        description="如果使用毒药，指定目标玩家姓名"
    )
    
    reason: Optional[str] = Field(
        default=None,
        description="行动理由"
    )


def get_seer_model_cn(players: list):
    """
    获取中文版预言家查验模型
    
    Args:
        players: 玩家对象列表或玩家名称列表
    
    Returns:
        Pydantic 模型类
    """
    player_names = []
    for p in players:
        if hasattr(p, 'name'):
            player_names.append(p.name)
        else:
            player_names.append(str(p))
    
    class SeerOutputCN(BaseModel):
        target: Literal[tuple(player_names)] = Field(
            description="要查验的玩家姓名"
        )
        
        reason: str = Field(
            description="选择查验该玩家的原因"
        )
    
    return SeerOutputCN


def get_hunter_model_cn(players: list):
    """
    获取中文版猎人开枪模型
    
    Args:
        players: 玩家对象列表或玩家名称列表
    
    Returns:
        Pydantic 模型类
    """
    player_names = []
    for p in players:
        if hasattr(p, 'name'):
            player_names.append(p.name)
        else:
            player_names.append(str(p))
    
    class HunterOutputCN(BaseModel):
        shoot: bool = Field(
            description="是否开枪"
        )
        
        target: Optional[Literal[tuple(player_names)]] = Field(
            default=None,
            description="如果开枪，指定目标玩家姓名"
        )
        
        reason: Optional[str] = Field(
            default=None,
            description="开枪或不开枪的理由"
        )
    
    return HunterOutputCN


def get_wolf_kill_model_cn(players: list):
    """
    获取狼人击杀模型
    
    Args:
        players: 玩家对象列表或玩家名称列表
    
    Returns:
        Pydantic 模型类
    """
    player_names = []
    for p in players:
        if hasattr(p, 'name'):
            player_names.append(p.name)
        else:
            player_names.append(str(p))
    
    class WerewolfKillOutputCN(BaseModel):
        target: Literal[tuple(player_names)] = Field(
            description="要击杀的玩家姓名"
        )
        
        reason: str = Field(
            description="选择击杀该玩家的原因"
        )
    
    return WerewolfKillOutputCN


# 注意：WerewolfKillModelCN 需要传入 players 参数
# 使用方式：WerewolfKillModelCN(players) 来获取模型类