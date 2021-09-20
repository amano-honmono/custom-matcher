from discord import Client

from src.db import DB

db = DB()


async def get_ranking(client: Client):
    sql = 'SELECT discord_id, rating FROM user ORDER BY rating DESC'
    cursor = db.query(sql)
    sql_response = cursor.fetchall()
    messages = list()
    for row in sql_response:
        messages.append("%s: %d" % (await client.fetch_user(row[0]), int(row[1])))

    return '\n'.join(messages)
