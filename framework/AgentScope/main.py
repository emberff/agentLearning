# -*- coding: utf-8 -*-
"""
三国狼人杀 - 基于 AgentScope 2.x 的中文版狼人杀游戏
融合三国演义角色和传统狼人杀玩法
"""
import sys
import io
# 确保输出支持 UTF-8 编码，允许显示 emoji
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import asyncio
import os
import random
import json
import re
from typing import List, Dict, Optional

from prompts.prompt import ChinesePrompts
from roles.gameRoles import GameRoles
from utils.utils import (
    check_winning_cn,
    majority_vote_cn,
    get_chinese_name,
    format_player_list,
    GameModerator,
    MAX_GAME_ROUND,
    MAX_DISCUSSION_ROUND,
    create_msg,
)
from config.model import ModelFactory
from config.settings import (
    ModelSettings,
    AgentSettings,
)
from agents.player_agent import PlayerAgent


def get_text_from_content(content) -> Optional[str]:
    """
    从 AgentScope 2.x 的消息内容中提取纯文本
    
    Args:
        content: 可能是 TextBlock 数组或其他格式
    
    Returns:
        提取的文本字符串
    """
    if isinstance(content, list):
        text_parts = []
        for item in content:
            if hasattr(item, "text"):
                text_parts.append(item.text)
            elif isinstance(item, str):
                text_parts.append(item)
        return "\n".join(text_parts) if text_parts else None
    elif hasattr(content, "text"):
        return content.text
    elif isinstance(content, str):
        return content
    return None


def extract_json_from_text(content) -> Optional[Dict]:
    """
    从文本中提取 JSON 格式的内容。
    
    Args:
        content: 可能包含 JSON 的文本或 TextBlock 数组
    
    Returns:
        解析后的字典，如果解析失败返回 None
    """
    # 先提取纯文本
    text = get_text_from_content(content)
    if not text:
        return None

    # 方法1: 尝试直接解析整个文本
    try:
        return json.loads(text)
    except Exception:
        pass

    # 方法2: 尝试找到用 ```json 包裹的内容
    json_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
    matches = re.findall(json_pattern, text)
    for match in matches:
        try:
            return json.loads(match.strip())
        except Exception:
            pass

    # 方法3: 尝试找到用大括号包裹的对象
    json_pattern = r'\{[\s\S]*\}'
    matches = re.findall(json_pattern, text)
    for match in matches:
        try:
            return json.loads(match.strip())
        except Exception:
            pass

    return None


class ThreeKingdomsWerewolfGame:
    """三国狼人杀游戏主类"""

    def __init__(self):
        self.players: Dict[str, PlayerAgent] = {}
        self.roles: Dict[str, str] = {}
        self.moderator = GameModerator()
        self.alive_players: List[PlayerAgent] = []
        self.werewolves: List[PlayerAgent] = []
        self.villagers: List[PlayerAgent] = []
        self.seer: List[PlayerAgent] = []
        self.witch: List[PlayerAgent] = []
        self.hunter: List[PlayerAgent] = []

        # 女巫道具状态
        self.witch_has_antidote = True
        self.witch_has_poison = True

        # 创建模型
        self.model = ModelFactory.create_model()

    def create_player(self, role: str, character: str) -> PlayerAgent:
        """创建具有三国背景的玩家"""
        name = get_chinese_name(character)
        self.roles[name] = role

        system_prompt = ChinesePrompts.get_role_prompt(role, character)

        agent = PlayerAgent(
            name=name,
            role=role,
            character=character,
            system_prompt=system_prompt,
            model=self.model,
            model_config=ModelFactory.create_model_config(),
            context_config=ModelFactory.create_context_config(),
            react_config=ModelFactory.create_react_config(),
        )

        self.players[name] = agent
        return agent

    async def setup_game(self, player_count: int = 6):
        """设置游戏"""
        print("🎮 开始设置三国狼人杀游戏...")

        # 获取角色配置
        roles = GameRoles.get_standard_setup(player_count)
        characters = random.sample([
            "刘备", "关羽", "张飞", "诸葛亮", "赵云",
            "曹操", "司马懿", "周瑜", "孙权"
        ], player_count)

        # 创建玩家
        for role, character in zip(roles, characters):
            agent = self.create_player(role, character)
            self.alive_players.append(agent)

            # 分配到对应阵营
            if role == "狼人":
                self.werewolves.append(agent)
            elif role == "预言家":
                self.seer.append(agent)
            elif role == "女巫":
                self.witch.append(agent)
            elif role == "猎人":
                self.hunter.append(agent)
            else:
                self.villagers.append(agent)

        # 通知玩家他们的角色
        for player in self.alive_players:
            role_desc = GameRoles.get_role_desc(player.role)
            role_ability = GameRoles.get_role_ability(player.role)
            announcement = await self.moderator.announce(
                f"【{player.name}】你在这场三国狼人杀中扮演{role_desc}，"
                f"你的角色是{player.character}。{role_ability}"
            )
            await player.observe(announcement)

        # 游戏开始公告
        await self.moderator.announce(
            f"三国狼人杀游戏开始！参与者：{format_player_list(self.alive_players)}"
        )

        print(f"✅ 游戏设置完成，共{len(self.alive_players)}名玩家")

    async def werewolf_phase(self, round_num: int) -> Optional[str]:
        """狼人阶段"""
        if not self.werewolves:
            return None

        await self.moderator.announce(f"🐺 狼人请睁眼，选择今晚要击杀的目标...")

        # 获取存活玩家列表（排除狼人自己）
        non_wolf_players = [p for p in self.alive_players if p not in self.werewolves]
        if not non_wolf_players:
            return None

        alive_player_names = [p.name for p in self.alive_players]
        non_wolf_names = [p.name for p in non_wolf_players]

        # 狼人讨论
        announcement = await self.moderator.announce(
            f"狼人们，请讨论今晚的击杀目标。存活玩家：{format_player_list(self.alive_players)}"
        )
        for wolf in self.werewolves:
            await wolf.observe(announcement)

        for _ in range(MAX_DISCUSSION_ROUND):
            for wolf in self.werewolves:
                if not wolf.can_speak:
                    continue

                result = await wolf.discussion(
                    prompt="请发表你的看法，讨论今晚要击杀谁",
                )
                if result:
                    # 让其他狼人也听到
                    for other_wolf in self.werewolves:
                        if other_wolf != wolf:
                            await other_wolf.observe(result)

        # 投票击杀
        kill_votes = {}
        for wolf in self.werewolves:
            try:
                prompt = f"""请选择今晚要击杀的目标，仅从以下列表中选择一个名字：
{', '.join(non_wolf_names)}

请以JSON格式回复：
{{
  "target": "玩家名字"
}}"""
                result = await wolf.reply(
                    message=create_msg("system", prompt, "user"),
                )

                target_name = None
                if result and hasattr(result, "content"):
                    parsed = extract_json_from_text(result.content)
                    if parsed and "target" in parsed:
                        target_name = parsed["target"]
                        # 验证目标是否有效
                        if target_name not in non_wolf_names:
                            target_name = None

                if not target_name:
                    # 如果解析失败，随机选择
                    target_name = random.choice(non_wolf_names)
                    print(f"⚠️ {wolf.name}的击杀选择解析失败，随机选择: {target_name}")

                kill_votes[wolf.name] = target_name
            except Exception as e:
                print(f"⚠️ {wolf.name} 投票时出错: {e}")
                kill_votes[wolf.name] = random.choice(non_wolf_names)

        killed_player, _ = majority_vote_cn(kill_votes)
        return killed_player

    async def seer_phase(self):
        """预言家阶段"""
        if not self.seer:
            return

        seer_agent = self.seer[0]
        if not seer_agent.alive:
            return

        await self.moderator.announce("🔮 预言家请睁眼，选择要查验的玩家...")

        alive_player_names = [p.name for p in self.alive_players if p != seer_agent]

        try:
            prompt = f"""请选择要查验的玩家，仅从以下列表中选择一个名字：
{', '.join(alive_player_names)}

请以JSON格式回复：
{{
  "target": "玩家名字"
}}"""
            result = await seer_agent.reply(
                message=create_msg("system", prompt, "user"),
            )

            target_name = None
            if result and hasattr(result, "content"):
                parsed = extract_json_from_text(result.content)
                if parsed and "target" in parsed:
                    target_name = parsed["target"]
                    if target_name not in alive_player_names:
                        target_name = None

            if not target_name:
                target_name = random.choice(alive_player_names)
                print(f"⚠️ 预言家未选择目标，随机选择: {target_name}")

            target_role = self.roles.get(target_name, "村民")

            # 告知预言家结果
            result_msg = await self.moderator.announce(
                f"查验结果：{target_name}是{'狼人' if target_role == '狼人' else '好人'}"
            )
            await seer_agent.observe(result_msg)

        except Exception as e:
            print(f"⚠️ 预言家查验阶段出错: {e}")

    async def witch_phase(self, killed_player: Optional[str]) -> tuple[Optional[str], Optional[str]]:
        """女巫阶段"""
        if not self.witch:
            return killed_player, None

        witch_agent = self.witch[0]
        if not witch_agent.alive:
            return killed_player, None

        await self.moderator.announce("🧙‍♀️ 女巫请睁眼...")

        # 告知女巫死亡信息
        death_info = f"今晚{killed_player}被狼人击杀" if killed_player else "今晚平安无事"
        death_msg = await self.moderator.announce(death_info)
        await witch_agent.observe(death_msg)

        saved_player = None
        poisoned_player = None

        try:
            alive_player_names = [p.name for p in self.alive_players]

            antidote_info = "你有解药可以使用" if self.witch_has_antidote else "解药已用完"
            poison_info = "你有毒药可以使用" if self.witch_has_poison else "毒药已用完"

            prompt = f"""{antidote_info}，{poison_info}。

请决定你的行动，以JSON格式回复：
{{
  "use_antidote": false,  // 是否使用解药
  "use_poison": false,    // 是否使用毒药
  "target_name": null     // 如果使用毒药，填写目标玩家名字
}}"""
            # 女巫行动
            result = await witch_agent.reply(
                message=create_msg("system", prompt, "user"),
            )

            use_antidote = False
            use_poison = False
            target_name = None

            if result and hasattr(result, "content"):
                parsed = extract_json_from_text(result.content)
                if parsed:
                    use_antidote = parsed.get("use_antidote", False)
                    use_poison = parsed.get("use_poison", False)
                    target_name = parsed.get("target_name")

            if use_antidote and self.witch_has_antidote and killed_player:
                saved_player = killed_player
                self.witch_has_antidote = False
                witch_agent.use_antidote()
                save_msg = await self.moderator.announce(f"你使用解药救了{killed_player}")
                await witch_agent.observe(save_msg)

            if use_poison and self.witch_has_poison and target_name in alive_player_names:
                poisoned_player = target_name
                self.witch_has_poison = False
                witch_agent.use_poison()
                poison_msg = await self.moderator.announce(f"你使用毒药毒杀了{target_name}")
                await witch_agent.observe(poison_msg)

        except Exception as e:
            print(f"⚠️ 女巫行动阶段出错: {e}")

        # 确定最终死亡玩家
        final_killed = killed_player if not saved_player else None

        return final_killed, poisoned_player

    async def hunter_phase(self, shot_by_hunter: Optional[str]) -> Optional[str]:
        """猎人阶段"""
        if not self.hunter:
            return None

        hunter_agent = self.hunter[0]
        if hunter_agent.name == shot_by_hunter and hunter_agent.can_shoot:
            await self.moderator.announce("🏹 猎人发动技能，可以带走一名玩家...")

            try:
                alive_player_names = [p.name for p in self.alive_players if p != hunter_agent]

                prompt = f"""请决定是否开枪带走一名玩家，从以下列表选择目标：
{', '.join(alive_player_names)}

请以JSON格式回复：
{{
  "shoot": true/false,
  "target": "玩家名字"  // 如果开枪的话
}}"""
                result = await hunter_agent.reply(
                    message=create_msg("system", prompt, "user"),
                )

                shoot = False
                target = None

                if result and hasattr(result, "content"):
                    parsed = extract_json_from_text(result.content)
                    if parsed:
                        shoot = parsed.get("shoot", False)
                        target = parsed.get("target")

                if shoot and target and target in alive_player_names:
                    hunter_agent.use_hunter_skill()
                    await self.moderator.announce(f"猎人{hunter_agent.name}开枪带走了{target}")
                    return target

            except Exception as e:
                print(f"⚠️ 猎人技能使用阶段出错: {e}")

        return None

    def update_alive_players(self, dead_players: List[str]):
        """更新存活玩家列表"""
        for dead_name in dead_players:
            if dead_name and dead_name in self.players:
                player = self.players[dead_name]
                player.kill()
                # 从存活列表移除
                self.alive_players = [p for p in self.alive_players if p.name != dead_name]
                # 从各阵营移除
                self.werewolves = [p for p in self.werewolves if p.name != dead_name]
                self.villagers = [p for p in self.villagers if p.name != dead_name]
                self.seer = [p for p in self.seer if p.name != dead_name]
                self.witch = [p for p in self.witch if p.name != dead_name]
                self.hunter = [p for p in self.hunter if p.name != dead_name]

    async def day_phase(self, round_num: int) -> Optional[str]:
        """白天阶段"""
        await self.moderator.day_announcement(round_num)

        # 讨论阶段
        discussion_announcement = await self.moderator.announce(
            f"现在开始自由讨论。存活玩家：{format_player_list(self.alive_players)}"
        )

        # 让所有玩家听到公告
        for player in self.alive_players:
            await player.observe(discussion_announcement)

        # 每人发言一轮
        for player in self.alive_players:
            if not player.can_speak:
                continue

            result = await player.speak(prompt="请发表你的看法")
            if result:
                # 让其他玩家也听到
                for other_player in self.alive_players:
                    if other_player != player:
                        await other_player.observe(result)

        # 投票阶段
        vote_announcement = await self.moderator.announce("请投票选择要淘汰的玩家")
        for player in self.alive_players:
            await player.observe(vote_announcement)

        alive_player_names = [p.name for p in self.alive_players]

        votes = {}
        for player in self.alive_players:
            if not player.can_vote:
                votes[player.name] = None
                continue

            try:
                prompt = f"""请投票选择要淘汰的玩家，从以下列表选择一个：
{', '.join(alive_player_names)}

请以JSON格式回复：
{{
  "vote": "玩家名字"
}}"""
                result = await player.reply(
                    message=create_msg("system", prompt, "user"),
                )

                vote_target = None
                if result and hasattr(result, "content"):
                    parsed = extract_json_from_text(result.content)
                    if parsed and "vote" in parsed:
                        vote_target = parsed["vote"]
                        if vote_target not in alive_player_names:
                            vote_target = None

                if vote_target:
                    votes[player.name] = vote_target
                    player.record_vote(vote_target)
                else:
                    votes[player.name] = None
            except Exception as e:
                print(f"⚠️ {player.name} 投票时出错: {e}")
                votes[player.name] = None

        voted_out, vote_count = majority_vote_cn(votes)
        await self.moderator.vote_result_announcement(voted_out, vote_count)

        return voted_out

    async def run_game(self):
        """运行游戏主循环"""
        try:
            await self.setup_game()

            for round_num in range(1, MAX_GAME_ROUND + 1):
                print(f"\n🌙 === 第{round_num}轮游戏开始 ===")

                # 夜晚阶段
                await self.moderator.night_announcement(round_num)

                # 狼人击杀
                killed_player = await self.werewolf_phase(round_num)

                # 预言家查验
                await self.seer_phase()

                # 女巫行动
                final_killed, poisoned_player = await self.witch_phase(killed_player)

                # 更新死亡玩家
                night_deaths = [p for p in [final_killed, poisoned_player] if p]
                self.update_alive_players(night_deaths)

                # 死亡公告
                await self.moderator.death_announcement(night_deaths)

                # 检查胜利条件
                winner = check_winning_cn(self.alive_players, self.roles)
                if winner:
                    await self.moderator.game_over_announcement(winner)
                    return

                # 白天阶段
                voted_out = await self.day_phase(round_num)

                # 猎人技能
                hunter_shot = await self.hunter_phase(voted_out)

                # 更新死亡玩家
                day_deaths = [p for p in [voted_out, hunter_shot] if p]
                self.update_alive_players(day_deaths)

                # 检查胜利条件
                winner = check_winning_cn(self.alive_players, self.roles)
                if winner:
                    await self.moderator.game_over_announcement(winner)
                    return

                print(f"第{round_num}轮结束，存活玩家：{format_player_list(self.alive_players)}")

        except Exception as e:
            print(f"❌ 游戏运行出错: {e}")
            import traceback
            traceback.print_exc()


async def main():
    """主函数"""
    # 检查环境变量
    if "DASHSCOPE_API_KEY" not in os.environ:
        print("请设置环境变量 DASHSCOPE_API_KEY")
        return

    print("🎮 欢迎来到三国狼人杀！")

    # 创建并运行游戏
    game = ThreeKingdomsWerewolfGame()
    await game.run_game()


if __name__ == "__main__":
    asyncio.run(main())
