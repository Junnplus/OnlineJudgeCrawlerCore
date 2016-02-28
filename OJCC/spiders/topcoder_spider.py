# -*- coding: utf-8 -*-

from scrapy.spiders import Spider
from scrapy.selector import Selector
from ojcc.items import AccountItem


class TopcoderAccountSpider(Spider):
    name = 'topcoder_user'
    allowed_domains = ['community.topcoder.com']

    def __init__(self, username, *args, **kwargs):
        super(TopcoderAccountSpider, self).__init__(*args, **kwargs)

        self.username = username
        self.start_urls = [
            'http://community.topcoder.com/tc?module=SimpleSearch&ha=%s' %
            username
        ]

    def parse(self, response):

        sel = Selector(response)

        item = AccountItem()
        item['origin_oj'] = 'topcoder'
        item['username'] = self.username

        item['rating'] = sel.xpath('//*[@id="left"]/h1/span[1]/text()').\
            extract()[0]
        return item
