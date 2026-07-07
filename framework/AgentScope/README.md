# 三国狼人杀 - AgentScope 2.x 版本

这是一个基于 AgentScope 2.x 的中文版狼人杀游戏，融合了三国演义角色。

## 项目更新内容

### 1. 适配 AgentScope 2.x API 变更

- **DashScopeChatModel 构造函数** 已更新为使用 `credential` 和 `model` 参数，而非原来的 `model_name` 和 `api_key`
- **Agent 初始化** 使用了新的配置类结构
- **结构化输出** 不再使用 `response_format` 参数，改为通过提示词要求输出 JSON，然后在代码中解析

### 2. 修复的问题

- 修复了相对导入错误（`from ..models` → `from models`）
- 更新了 config/model.py 以使用新的 DashScopeCredential 类
- 更新了 agents/player_agent.py 移除对旧版 response_format 的依赖
- 修复了 GameModerator 类不再继承自 Agent（Agent 现在需要必需参数，而主持人不需要 LLM）
- 添加了 `extract_json_from_text()` 函数来解析 LLM 输出的 JSON 内容

## 运行游戏

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 设置 API 密钥

Windows PowerShell:
```powershell
$env:DASHSCOPE_API_KEY="your-api-key-here"
```

Windows CMD:
```cmd
set DASHSCOPE_API_KEY=your-api-key-here
```

Linux/Mac:
```bash
export DASHSCOPE_API_KEY=your-api-key-here
```

### 3. 运行游戏

```bash
python main.py
```

## 项目结构

```
AgentScope/
├── main.py                      # 游戏主程序
├── requirements.txt             # 依赖文件
├── README.md                   # 项目说明
├── agents/                     # Agent 相关模块
│   ├── __init__.py
│   ├── player_agent.py         # 玩家 Agent 类
│   ├── moderator_agent.py      # 主持人 Agent 类
│   └── factory.py              # Agent 工厂
├── config/                     # 配置模块
│   ├── __init__.py
│   ├── model.py               # 模型工厂
│   └── settings.py            # 配置类
├── models/                     # 数据模型
│   ├── __init__.py
│   ├── structured_output.py   # 结构化输出类
│   ├── game_message.py        # 游戏消息类
│   └── game_state.py          # 游戏状态类
├── prompts/                    # 提示词
│   └── prompt.py
├── roles/                      # 角色定义
│   └── gameRoles.py
├── utils/                      # 工具函数
│   └── utils.py
├── workflows/                  # 工作流（可选）
│   └── discussion.py
└── game/                       # 游戏模块
    ├── game.py
    ├── phases.py
    └── state.py
```

## 辅助工具

- `test_api.py`: 测试 API 连接是否正常
- `test_imports.py`: 测试模块导入是否正常
- `check_agentscope.py`: 检查 AgentScope API
- `check_agent.py`: 检查 Agent 类 API
- `start_game.ps1`: PowerShell 启动脚本（设置 API Key 并运行游戏）

## 游戏角色

- 狼人：夜晚击杀玩家，白天隐藏身份
- 预言家：夜晚查验玩家身份
- 女巫：拥有解药和毒药各一瓶
- 猎人：被投票淘汰时可以开枪带走一名玩家
- 村民：无特殊技能，通过推理找出狼人

## 三国角色

游戏中的玩家将扮演以下三国角色之一：
刘备、关羽、张飞、诸葛亮、赵云、曹操、司马懿、周瑜、孙权
