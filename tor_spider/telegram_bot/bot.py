from telethon import TelegramClient, events, Button
from aiohttp_socks import ProxyConnector
from pathlib import Path
import sqlite3
import asyncio
import aiohttp
import random
import json
from datetime import datetime
from datetime import timedelta


headers = {}
headers['User-agent'] = "Mozilla/5.0 (Windows NT 6.1; rv:60.0) Gecko/20100101 Firefox/60.0"


def do_query(path, q, args=None):
    if args is None:
        args = []
    with sqlite3.connect(path) as db:
        cur = db.execute(q, args)
        ans = cur.fetchall()
    return ans



async def fetch(session, url):
    async with session.get(url, headers=headers, timeout=60*5) as response:
        return response.status


async def get_code(url):
    connector = ProxyConnector.from_url(config['proxy_url'], rdns=True)
    async with aiohttp.ClientSession(connector=connector) as session:
        return await fetch(session, url)


async def check_url(task_name, url):
    try:
        code = await get_code(url)
        if code == 200:
            return url
    except Exception as e:
        await asyncio.sleep(10)


async def get_first_success(urls):
    tasks = []
    for i, url in enumerate(urls):   
        task = asyncio.create_task(check_url(f'task{i}', url))
        tasks.append(task)
    done, pending = await asyncio.wait(
        tasks,
        return_when=asyncio.FIRST_COMPLETED,
        timeout=10
        )
    return done.pop().result()


current_path = Path(__file__)
with open(current_path.parent.joinpath('config.json')) as f:
    config = json.loads(f.read())
db_path = current_path.parent.parent.joinpath(config['db_name'])


bot = TelegramClient('bot',
        config['api_id'],
        config['api_hash']).start(bot_token=config['bot_token'])


@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    """Send a message when the command /start is issued."""
    await event.respond('Welcome!', buttons=[
        Button.text('Get random onion!',
            resize=True,
            selective=True),
        ])
    raise events.StopPropagation


@bot.on(events.NewMessage)
async def send_onion(event):
    """Send random link from database."""
    try:
        urls = [row[0] for row in do_query(db_path,
            'SELECT {} FROM {} WHERE {} >= "{}" ORDER BY RANDOM() LIMIT 20'.format(
                config['field'], config['table'],
                config['date_field'], datetime.now() - timedelta(days=config['days_before_visited'])
                ))]
        url = await get_first_success(urls)
        await event.respond(url)
    except Exception as e:
        await event.respond('Sowwy =(')
        with open(Path(__file__).parent.joinpath('bot_err.log'), 'a') as f:
            t = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
            f.write('{}\t{}\n'.format(t, str(e).replace('\n', ' ')))


def main():
    """Start the bot."""
    bot.run_until_disconnected()
