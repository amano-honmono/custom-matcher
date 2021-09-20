from discord import Client

from src.player import Player


class Game:
    team_a: list[Player]
    team_b: list[Player]

    def __init__(self, team_a, team_b):
        self.team_a = team_a
        self.team_b = team_b

    async def new_game_message(self, client: Client):
        messages = list()
        messages.append('NEW GAME')
        messages.append(await self.to_message(client))
        messages.append("リアクションを押してください")
        messages.append('▶: ゲーム開始')
        messages.append('⏹: 中止')
        messages.append('🔁: チーム分け変更')
        return '\n'.join(messages)

    async def start_game_message(self, client: Client):
        messages = list()
        messages.append('NOW PLAYING')
        messages.append(await self.to_message(client))
        messages.append("ゲーム終了後、勝ったチームにリアクションしてください。")
        return '\n'.join(messages)

    async def to_message(self, client: Client):
        messages = list()
        messages.append('🟦 TEAM 1')
        for player in self.team_a:
            name = (await client.fetch_user(player.discord_id)).name
            messages.append("%s %d" % (name, int(player.rating)))
        messages.append('\n🟥 TEAM 2')
        for player in self.team_b:
            name = (await client.fetch_user(player.discord_id)).name
            messages.append("%s %d" % (name, int(player.rating)))
        return '\n'.join(messages)
