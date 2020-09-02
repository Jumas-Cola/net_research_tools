from scrapy.utils.project import get_project_settings
from scrapy.linkextractors import LinkExtractor
from collections import Counter
from datetime import datetime
from urllib import parse
import aiosqlite
import asyncio
import logging
import random
import ssdeep
import scrapy
import time
import re


# Import variables from settings
locals().update(get_project_settings().copy_to_dict())

for module, log_level in LOG_LEVELS.items():
    logging.getLogger(module).setLevel(getattr(logging, log_level))


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


class VisitedLinksCollection:
    """
    VisitedLinksCollection - custom collection class
    for checking grabbed links.
    """
    def __init__(self, iterable_links):
        self._netloc_counter = Counter(parse.urlparse(url).netloc for url in iterable_links)
        self._link_set = set(iterable_links)


    def add(self, url):
        self._link_set.add(url)
        self._netloc_counter += {parse.urlparse(url).netloc: 1}


    def __contains__(self, url):
        return url in self._link_set


    def __getitem__(self, url):
        return self._netloc_counter[url]


class TorSpider(scrapy.Spider):

    """
    Main spider class, which crawl all links from
    start pages and walk on them to maximum depth.
    """

    name = 'tor_spider'

    rotate_user_agent = ROTATE_USER_AGENT


    def start_requests(self):
        start_urls = [row[1] for row in do_query(DB_PATH, 
            'SELECT * FROM {}'.format(TABLE))]
        if RANDOMIZE_URLS:
            random.shuffle(start_urls)
        self.visited_urls = VisitedLinksCollection(start_urls)

        for url in start_urls:
            yield scrapy.Request(
                    url=url,
                    callback=self.parse,
                    meta={'proxy': PROXY}
                    )


    def update_db(self, response, title, description):
        parsed_url = parse.urlparse(response.url)
        url = parse.urlunsplit((parsed_url.scheme, parsed_url.netloc, '', '', ''))

        insert = True

        if len(do_query(DB_PATH,
            'SELECT * FROM {} WHERE {} LIKE "%{}"'.format(TABLE, LINK_FIELD, url))):
            do_query(DB_PATH, 'UPDATE {} SET {}="{}" WHERE {}="{}"'.format(
                TABLE, LAST_VISITED_FIELD, datetime.now(), LINK_FIELD, url), commit=True)
            if LOG_ENABLED:
                print('[WARNING] Domain already in DB:', response.url)
            insert = False

        if insert:
            hash_val = ssdeep.hash(response.text)

            if len(do_query(DB_PATH,
                'SELECT * FROM {} WHERE {} LIKE "{}%"'.format(TABLE, HASH_FIELD, hash_val))):
                if LOG_ENABLED:
                    print('[WARNING] Clone page:', response.url)
                insert = False

        if insert:
            row = (title, url, description, hash_val, datetime.now())

            do_query(DB_PATH, 'INSERT INTO {} VALUES ({})'.format(TABLE, ','.join('?'
                for _ in range(len(row)))), args=row, commit=True)
            print('[INFO] Inserted in DB:', url)


    def parse(self, response):

        if not parse.urlparse(response.url).netloc.endswith('.onion'):
            return

        curr_depth = response.meta.get('depth', 1)

        try:
            title = response.css('title::text').get()
            if any(re.search(pattern, title, re.IGNORECASE) for pattern in DENY):
                return
        except:
            title = ''

        try:
            description = response.css('meta[name=description]').attrib['content']
            if any(re.search(pattern, description, re.IGNORECASE) for pattern in DENY):
                return
        except:
            description = ''

        self.update_db(response, title, description)

        if curr_depth > MAX_DEPTH:
            return

        le = LinkExtractor(
                allow=ALLOW,
                deny=DENY,
                deny_extensions=DENY_EXTENSIONS,
                unique=True
                )
        links = le.extract_links(response)

        for link in links:
            if parse.urlparse(link.url).netloc.endswith('.onion') \
                    and link.url not in self.visited_urls \
                    and self.visited_urls[link.url] < MAX_LINKS_FOR_HOST:
                self.visited_urls.add(link.url)
                yield scrapy.Request(
                        url=link.url,
                        meta={
                            'depth': curr_depth + 1,
                            'proxy': PROXY
                            },
                        callback=self.parse,
                        )
