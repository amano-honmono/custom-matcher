import discord
import yaml

from src import match

client = discord.Client()
with open('/opt/project/config.yml') as file:
    config = yaml.safe_load(file)


@client.event
async def on_ready():
    if config["debug"]:
        print("debugモードが有効です！！！本番環境を向いていません！！！")
    print('custom-matcher ready!')
    print('server:', client.get_guild(config['guild']['guild-id']))


@client.event
async def on_message(message: discord.Message):
    if not message.content.startswith("/custom") or message.channel.id != config["guild"]["text-channel-id"]:
        return

    command = message.content.split()[1:]
    if command[0] == "create":
        if match.status != match.MatchStatus.NOTHING:
            await message.channel.send('他のゲームが進行中です')
            return
        game_message = await message.channel.send(await match.create_game(client))
        for reaction in ['▶', '⏹', '🔁']:
            await game_message.add_reaction(reaction)

    if command[0] == "reset":
        match.status = match.MatchStatus.NOTHING
        await message.channel.send("OK")


@client.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
    print("reaction:", reaction)
    print("type:", type(reaction))
    owner_id = config['guild']['owner-id']
    # ゲーム作成時の処理
    if reaction.message.author.bot and reaction.message.content.startswith('NEW GAME'):
        if user.id == owner_id and reaction.emoji == '▶':
            game_message = await reaction.message.channel.send(await match.start_game(client))
            await reaction.message.delete()
            for reaction in ['🟦', '🟥']:
                await game_message.add_reaction(reaction)
        elif user.id == owner_id and reaction.emoji == '⏹':
            match.status = match.MatchStatus.NOTHING
            await reaction.message.delete()
            await reaction.message.channel.send("中止しました。")
        elif user.id == owner_id and reaction.emoji == '🔁':
            await reaction.message.delete()
            game_message = await reaction.message.channel.send(await match.refresh_match(client))
            for reaction in ['▶', '⏹', '🔁']:
                await game_message.add_reaction(reaction)
        else:
            return
    # ゲーム終了時の処理
    elif reaction.message.author.bot and reaction.message.content.startswith('NOW PLAYING'):
        if user.id == owner_id and reaction.emoji == '🟦':
            game_message = await match.finish_game(client, 0)
        elif user.id == owner_id and reaction.emoji == '🟥':
            game_message = await match.finish_game(client, 1)
        else:
            return
        await reaction.message.delete()
        await reaction.message.channel.send(game_message)
    else:
        return


if __name__ == '__main__':
    client.run(config['custom-matcher']['token'])
