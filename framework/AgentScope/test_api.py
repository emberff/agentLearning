# -*- coding: utf-8 -*-
"""
测试 API 连接
"""

import os
import sys

print("=" * 60)
print("API 连接测试")
print("=" * 60)

# 1. 检查 API Key
api_key = os.environ.get("DASHSCOPE_API_KEY")
if not api_key:
    print("\n错误: DASHSCOPE_API_KEY 环境变量未设置")
    print("\n请使用以下命令设置:")
    print("  PowerShell: $env:DASHSCOPE_API_KEY='your_key'")
    print("  CMD: set DASHSCOPE_API_KEY=your_key")
    sys.exit(1)

print(f"\nAPI Key 已设置 (前10位: {api_key[:10]}...)")

# 2. 测试 AgentScope 导入
try:
    print("\n正在导入 AgentScope...")
    from agentscope.model import DashScopeChatModel
    from agentscope.credential import DashScopeCredential
    from agentscope.message import Msg, TextBlock
    print("AgentScope 导入成功")
except Exception as e:
    print(f"AgentScope 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 3. 测试模型初始化
try:
    print("\n正在初始化模型...")
    credential = DashScopeCredential(api_key=api_key)
    parameters = DashScopeChatModel.Parameters(
        temperature=0.7,
        top_p=0.9,
        max_tokens=100,
    )
    model = DashScopeChatModel(
        credential=credential,
        model="qwen-max",
        parameters=parameters,
    )
    print("模型初始化成功")
except Exception as e:
    print(f"模型初始化失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 4. 简单的测试调用
try:
    print("\n正在进行简单的 API 调用测试...")
    # 创建一个简单的消息
    text_block = TextBlock(text="你好，请用一句话介绍自己")
    messages = [
        Msg(name="user", content=[text_block], role="user")
    ]
    
    # 调用模型
    response = model(messages)
    print(f"API 调用成功!")
    
    # 提取并显示响应文本
    if hasattr(response, "content"):
        text_parts = []
        if isinstance(response.content, list):
            for item in response.content:
                if hasattr(item, "text"):
                    text_parts.append(item.text)
                elif isinstance(item, str):
                    text_parts.append(item)
        response_text = "\n".join(text_parts) if text_parts else str(response.content)
    else:
        response_text = str(response)
    
    print(f"响应: {response_text}")
except Exception as e:
    print(f"API 调用失败: {e}")
    print("\n提示: 请检查您的 API Key 是否有效，以及是否有足够的额度")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("所有测试通过！API 连接正常。")
print("=" * 60)
