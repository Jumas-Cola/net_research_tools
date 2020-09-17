# Scrapy settings for tor_spider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

#LOG_ENABLED = 0

DB_CONNECTION_PARAMS = dict(
    host='localhost',
    port=6379,
    password='hardpass123',
)

TITLE_FIELD = 'Title'
LINK_FIELD = 'Link'
HASH_FIELD = 'Hash'
DESCRIPTION_FIELD = 'Description'
LAST_VISITED_FIELD = 'LastVisited'

PROXY = 'http://127.0.0.1:8118'

MAX_DEPTH = None
MAX_LINKS_FOR_HOST = None
ROTATE_USER_AGENT = True
RANDOMIZE_URLS = True
ALLOW = [r'.*\.onion.*']
DENY = [r'.*facebook.*', r'.*\.org.*', r'.*\.com.*',
        r'.*porn.*', r'.*sex.*', r'.*child.*', r'.*market.*',
        r'.*shop.*', r'.*apple.*', r'.*iphone.*', r'.*card.*',
        r'.*bitcoin.*', r'.*coin.*', r'.*money.*', r'.*weapon.*',
        r'.*guns.*', r'.*cannabis.*', r'.*scam.*', r'.*kids.*',
        r'.*hitman.*', r'.*kill.*', r'.*murder.*', r'.*cocaine.*',
        r'.*teen.*', r'.*rape.*', r'.*pedo.*', r'.* cp .*',
        r'.*jailbait.*', r'.*loli.*', r'.*boys.*'
        ]
DENY_EXTENSIONS = ['jpg', 'png', 'mp3', 'wav', 'gif',
        'pdf', 'rss', 'ogg', 'mp4', 'avi', 'svg', 'csv',
        '7z', '7zip', 'apk', 'bz2', 'cdr', 'dmg', 'ico',
        'iso', 'tar', 'tar.gz', 'webm', 'xz'
        ]

SPIDER_MODULES = ['tor_spider.spiders']
NEWSPIDER_MODULE = 'tor_spider.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'tor_spider (+http://www.yourdomain.com)'

# Obey robots.txt rules
#ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'tor_spider.middlewares.TorSpiderSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'tor_spider.middlewares.TorSpiderDownloaderMiddleware': 543,
#}

DOWNLOADER_MIDDLEWARES = {
        'tor_spider.middlewares.RotateUserAgentMiddleware': 110,
        }

USER_AGENT_CHOICES = [
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:23.0) Gecko/20100101 Firefox/23.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.62 Safari/537.36',
        'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; WOW64; Trident/6.0)',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.146 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.146 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64; rv:24.0) Gecko/20140205 Firefox/24.0 Iceweasel/24.3.0',
        'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:28.0) Gecko/20100101 Firefox/28.0',
        'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:28.0) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2',
        ]

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    'tor_spider.pipelines.TorSpiderPipeline': 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

#TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'
