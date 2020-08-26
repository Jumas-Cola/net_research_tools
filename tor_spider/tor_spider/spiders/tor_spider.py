import scrapy
from scrapy.linkextractors import LinkExtractor
import sqlite3
import random
import time
from urllib import parse
from collections import Counter
import re
import ssdeep
import os


def do_query(path, q, args=None, commit=False):
    """
    do_query - Run a SQLite query, waiting for DB in necessary

    Args:
        path (str): path to DB file
        q (str): SQL query
        args (list): values for `?` placeholders in q
        commit (bool): whether or not to commit after running query
    Returns:
        list of lists: fetchall() for the query
    """
    if args is None:
        args = []
    for attempt in range(50):
        try:
            con = sqlite3.connect(path)
            cur = con.cursor()
            cur.execute(q, args)
            ans = cur.fetchall()
            if commit:
                con.commit()
            cur.close()
            con.close()
            del cur
            del con
            return ans
        except:
            time.sleep(random.randint(10, 30))


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

    # Spider settings
    name = 'tor_spider'
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tor_links')
    table = 'Links'
    link_field = 'Link'
    page_hash = 'Hash'
    proxy = 'http://127.0.0.1:8118' # privoxy > tor port
    max_depth = 3
    rotate_user_agent = True
    allow=[r'.*\.onion.*']
    deny=[r'.*facebook.*', r'.*\.org.*', r'.*\.com.*',
            r'.*porn.*', r'.*sex.*', r'.*child.*', r'.*market.*',
            r'.*shop.*', r'.*apple.*', r'.*iphone.*', r'.*card.*',
            r'.*bitcoin.*', r'.*coin.*', r'.*money.*', r'.*weapon.*',
            r'.*guns.*', r'.*cannabis.*', r'.*scam.*', r'.*kids.*',
            r'.*hitman.*', r'.*kill.*', r'.*murder.*', r'.*cocaine.*',
            r'.*teen.*', r'.*rape.*', r'.*pedo.*', r'.* cp .*',
            r'.*jailbait.*', r'.*loli.*', r'.*boys.*']
    deny_extensions=['jpg', 'png', 'mp3', 'wav', 'gif',
            'pdf', 'rss', 'ogg', 'mp4', 'avi', 'svg', 'csv',
            '7z', '7zip', 'apk', 'bz2', 'cdr', 'dmg', 'ico',
            'iso', 'tar', 'tar.gz', 'webm', 'xz']
    max_netloc_count = 300 # link count for one host
    randomize = True


    def start_requests(self):
        start_urls = [row[1] for row in do_query(self.db_path,
            'SELECT * FROM {}'.format(self.table))]
        if self.randomize:
            random.shuffle(start_urls)
        self.visited_urls = VisitedLinksCollection(start_urls)

        for url in start_urls:
            yield scrapy.Request(
                    url=url,
                    callback=self.parse,
                    meta={'proxy': self.proxy}
                    )


    def update_db(self, response, title, description):
        parsed_url = parse.urlparse(response.url)
        url = parse.urlunsplit((parsed_url.scheme, parsed_url.netloc, '', '', ''))

        insert = True

        if len(do_query(self.db_path,
            'SELECT * FROM {} WHERE {} LIKE "%{}"'.format(self.table, self.link_field, url))):
            print('[WARNING] Domain already in DB:', response.url)
            insert = False

        if insert:
            page_hash = ssdeep.hash(response.text)

            if len(do_query(self.db_path,
                'SELECT * FROM {} WHERE {} LIKE "{}%"'.format(self.table, self.page_hash, page_hash))):
                print('[WARNING] Clone page:', response.url)
                insert = False

        if insert:
            row = (title, url, description, page_hash)

            do_query(self.db_path, 'INSERT INTO {} VALUES ({})'.format(self.table, ','.join('?'
                for _ in range(len(row)))), args=row, commit=True)
            print('[INFO] Inserted in DB:', url)


    def parse(self, response):

        if not parse.urlparse(response.url).netloc.endswith('.onion'):
            return

        print('[INFO]', response.url)

        curr_depth = response.meta.get('depth', 1)

        try:
            title = response.css('title::text').get()
            if any(re.search(pattern, title, re.IGNORECASE) for pattern in self.deny):
                return
        except:
            title = ''

        try:
            description = response.css('meta[name=description]').attrib['content']
            if any(re.search(pattern, description, re.IGNORECASE) for pattern in self.deny):
                return
        except:
            description = ''

        self.update_db(response, title, description)

        if not curr_depth < self.max_depth:
            return

        le = LinkExtractor(
                allow=self.allow,
                deny=self.deny,
                deny_extensions=self.deny_extensions,
                unique=True
                )
        links = le.extract_links(response)

        for link in links:
            if parse.urlparse(link.url).netloc.endswith('.onion') \
                    and link.url not in self.visited_urls \
                    and self.visited_urls[link.url] < self.max_netloc_count:
                self.visited_urls.add(link.url)
                yield scrapy.Request(
                        url=link.url,
                        meta={
                            'depth': curr_depth + 1,
                            'proxy': self.proxy
                            },
                        callback=self.parse,
                        )
