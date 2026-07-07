# -*- coding: utf-8 -*-

"""
模型工厂
"""

import os
from agentscope.agent import (
    ContextConfig,
    ModelConfig,
    ReActConfig,
)

from agentscope.model import DashScopeChatModel
from agentscope.credential import DashScopeCredential

from .settings import (
    AgentSettings,
    ModelSettings,
)


class ModelFactory:
    """模型工厂"""

    @staticmethod
    def create_model():
        # 创建凭证
        credential = DashScopeCredential(
            api_key=os.environ.get("DASHSCOPE_API_KEY", "")
        )
        
        # 创建参数
        parameters = DashScopeChatModel.Parameters(
            temperature=ModelSettings.TEMPERATURE,
            top_p=ModelSettings.TOP_P,
            max_tokens=ModelSettings.MAX_TOKENS,
        )
        
        return DashScopeChatModel(
            credential=credential,
            model=ModelSettings.MODEL_NAME,
            parameters=parameters,
        )

    @staticmethod
    def create_model_config():

        return ModelConfig()

    @staticmethod
    def create_context_config():

        return ContextConfig(
            enable_context_compress=AgentSettings.AUTO_COMPRESS_CONTEXT,
            max_context_messages=AgentSettings.MAX_CONTEXT_MESSAGES,
        )

    @staticmethod
    def create_react_config():

        return ReActConfig(
            enable_react=AgentSettings.ENABLE_REACT,
        )