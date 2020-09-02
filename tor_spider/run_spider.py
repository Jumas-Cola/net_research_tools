from scrapy.crawler import CrawlerProcess
from tor_spider.spiders.tor_spider import TorSpider
from scrapy.utils.reactor import install_reactor
from scrapy.utils.project import get_project_settings

process = CrawlerProcess(get_project_settings())

install_reactor('twisted.internet.asyncioreactor.AsyncioSelectorReactor')
process.crawl(TorSpider)
process.start()
