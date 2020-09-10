import scrapy
from scrapy.utils.project import get_project_settings
from itertools import product
import pickle
from time import sleep
from pathlib import Path
import aiosqlite
import asyncio
import random
import re


# Import variables from settings
locals().update(get_project_settings().copy_to_dict())

def do_query(path, q, args=None, commit=False):

    async def _do_query(path, q, args=None, commit=False):
        if args is None:
            args = []
        async with aiosqlite.connect(path) as db:
            cur = await db.execute(q, args)
            ans = await cur.fetchall()
            if commit:
                await db.commit()
        return ans

    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_do_query(path, q, args, commit))


def infinite_random(iterable, l):
    while True:
        yield tuple(random.choice(iterable) for _ in range(l))


class CloudMailSpider(scrapy.Spider):

    name = 'cloudmail_spider'

    location = Path(__file__).parent
    urls_product_file = location.joinpath('urls_product.pickle')
    db_path = location.parent.parent.joinpath('links.db')
    table = 'Links'
    grabbing_type = 'random'
    visited_count = 0

    def start_requests(self):
        chars = 'abcdefghijklmnopqrstuvwxyz'
        chars += chars.upper()
        chars += '0123456789'

        if self.grabbing_type == 'product':
            if self.urls_product_file.is_file():
                with open(self.urls_product_file, 'rb') as f:
                    self.strings = pickle.load(f)
            else:
                self.strings = product(chars, repeat=13)
        elif self.grabbing_type == 'random':
            self.strings = infinite_random(chars, 13)

        for string in self.strings:
            url = 'https://cloud.mail.ru/public/' + ''.join(string[:4]) + '/' + ''.join(string[4:])
            yield scrapy.Request(url=url, method='POST', callback=self.parse)

    def parse(self, response):
        self.visited_count += 1
        if self.visited_count % 100 == 0:
            print(response.url, self.visited_count)
        if self.grabbing_type == 'product':
            with open(self.urls_product_file, 'wb') as f:
                pickle.dump(self.strings, f)
        if len(response.body) > 523000:
            print(response.url)

            try:
                title = response.css('title::text').get()
                if any(re.search(pattern, title, re.IGNORECASE) for pattern in DENY):
                    return
            except:
                title = ''

            row = ((title, response.url))
            do_query(self.db_path, 'INSERT INTO {} VALUES ({})'.format(self.table, ','.join('?'
                for _ in range(len(row)))), args=row, commit=True)
