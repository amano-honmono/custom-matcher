import random
from enum import Enum
from statistics import mean

import MySQLdb
import itertools

from discord import Client

from main import config
from src.game import Game
from src.player import Player


class MatchStatus(Enum):
    NOTHING = 1
    CREATING = 2
    PLAYING = 3


connection = MySQLdb.connect(
    user=config['mysql']['user'],
    passwd=config['mysql']['passwd'],
    host=config['mysql']['host'],
    db=config['mysql']['db_dev'] if config['debug'] else config['mysql']['db'],
)
cursor = connection.cursor()

match_list = []
match_iter = 0
status = MatchStatus.NOTHING


async def start_game(client: Client):
    global status
    status = MatchStatus.PLAYING
    game = Game(match_list[match_iter][0], match_list[match_iter][1])
    return await game.start_game_message(client)


async def update_rating(client: Client, winner: int):
    k = 32
    win_team = match_list[match_iter][winner]
    lose_team = match_list[match_iter][1 - winner]
    win_team_rating_mean = mean([player.rating for player in win_team])
    lose_team_rating_mean = mean([player.rating for player in lose_team])
    messages = list()
    for player in win_team:
        pre_rating = player.rating
        w_ba = 1 / (pow(10, (pre_rating - lose_team_rating_mean) / 400) + 1)
        post_rating = pre_rating + k * w_ba
        player.rating = post_rating
        messages.append("%s: %d -> %d" % (await client.fetch_user(player.discord_id), int(pre_rating), int(post_rating)))
    for player in lose_team:
        pre_rating = player.rating
        w_ba = 1 / (pow(10, (win_team_rating_mean - pre_rating) / 400) + 1)
        post_rating = pre_rating - k * w_ba
        player.rating = post_rating
        messages.append("%s: %d -> %d" % (await client.fetch_user(player.discord_id), int(pre_rating), int(post_rating)))
    return '\n'.join(messages)


def update_db(winner: int):
    # gameテーブルを更新
    query = 'INSERT INTO game (winner) VALUES (%s)'
    print('execute SQL:', query)
    cursor.execute(query, (winner,))
    game_id = cursor.lastrowid

    # playerテーブル, userテーブルを更新
    for team in [0, 1]:
        query = 'INSERT INTO player VALUES (%s, %s, %s)'
        print('execute SQL:', query)
        cursor.executemany(query, [(game_id, player.discord_id, team) for player in match_list[match_iter][team]])

        query = 'UPDATE user SET rating=%s where discord_id = %s'
        print('execute SQL:', query)
        cursor.executemany(query, [(player.rating, player.discord_id) for player in match_list[match_iter][team]])

    connection.commit()


async def finish_game(client: Client, winner: int):
    messages = list()
    messages.append("試合終了!")
    messages.append("レッド" if winner else "ブルー" + "チームの勝ち！")
    messages.append(await update_rating(client, winner))
    update_db(winner)
    messages.append("レーティングの更新が完了しました。")
    global status
    status = MatchStatus.NOTHING
    return '\n'.join(messages)


async def create_game(client: Client):
    global status
    status = MatchStatus.CREATING
    generate_match(client)
    game = Game(match_list[match_iter][0], match_list[match_iter][1])
    return await game.new_game_message(client)


async def refresh_match(client: Client):
    global match_iter
    match_iter = match_iter + 1
    game = Game(match_list[match_iter][0], match_list[match_iter][1])
    return await game.new_game_message(client)


def generate_match(client: Client):
    # customチャンネルにいるuserのidを取得
    print(config['guild']['voice-channel-id']['custom'])
    members = client.get_channel(config['guild']['voice-channel-id']['custom']).voice_states.keys()
    ############################################ debug ###############################################
    # members = [735519093045854371, 267469367195860992, 211265291097735168, 219488189860151296]
    ##################################################################################################
    print('members id:', members)
    players = get_players(members)

    global match_iter
    match_iter = 0

    # playersを半分ずつに分け、ratingの合計の差分の少ない順にソート
    team_list = list(itertools.combinations(players, len(members) // 2))
    global match_list
    match_list = []
    registered_team = set()
    for team_a in team_list:
        team_a = set(team_a)
        team_b = set(players) - team_a

        # そのままだと同じチームが２回ずつ追加されるので、被っていないか判定
        registered_team.add(tuple(sorted([int(i.discord_id) for i in team_a])))
        if tuple(sorted([int(i.discord_id) for i in team_b])) in registered_team:
            continue

        rating_diff = abs(sum(player.rating for player in team_a) - sum(player.rating for player in team_b))
        if random.choice([True, False]):
            match_list.append((team_a, team_b, rating_diff))
        else:
            match_list.append((team_b, team_a, rating_diff))
    match_list.sort(key=lambda x: x[2])


def get_players(members: list[int]):
    # DBからuserを取得
    format_strings = ','.join(['%s'] * len(members))
    query = 'SELECT * FROM user WHERE discord_id IN (%s)' % format_strings
    print('execute SQL:', query)
    cursor.execute(query, tuple(members))
    sql_response = cursor.fetchall()
    print('===========================================')
    for row in sql_response:
        print(row[0], row[1])
    print('===========================================')
    players = [Player(row[0], row[1]) for row in sql_response]

    # membersには入っているが、レスポンスには無いuserをDBに追加
    new_user = set(members) - set([int(row[0]) for row in sql_response])
    if len(new_user) > 0:
        print('new_user:', new_user)
        players.extend([Player(discord_id, 1500.) for discord_id in new_user])
        query = 'INSERT INTO user (discord_id) VALUES (%s)'
        print('execute SQL:', query)
        cursor.executemany(query, [(i,) for i in new_user])
        connection.commit()
    return players


if __name__ == '__main__':
    pass
