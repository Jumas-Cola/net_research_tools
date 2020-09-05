import scrapy
from ..items import ImageItem
from itertools import product
import os
import random
import pickle
from time import sleep


class LightshotSpider(scrapy.Spider):
    name = 'lightshot_spider'
    rotate_user_agent = True
    location = os.path.dirname(os.path.realpath(__file__))
    urls_product_file = os.path.join(location, 'urls_product.pickle')

    handle_httpstatus_list = [403]

    def start_requests(self):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789'

        if os.path.isfile(self.urls_product_file):
            with open(self.urls_product_file, 'rb') as f:
                self.strings = pickle.load(f)
        else:
            self.strings = product(chars, repeat=6)

        for string in self.strings:
            url = 'https://prnt.sc/' + ''.join(string)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        if int(response.status) != 200:
            with open(self.urls_product_file, 'wb') as f:
                pickle.dump(self.strings, f)
        else:
            img_src = response.css('#screenshot-image').attrib['src']
            yield ImageItem(image_urls=[img_src])
