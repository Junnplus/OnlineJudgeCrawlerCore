# -*- coding: utf-8 -*-

from scrapy.spiders import Spider
from scrapy.selector import Selector

from OJCC.items import AccountItem


class CodeforcesAccountSpider(Spider):
    name = 'codeforces_user_spider'
    allowed_domains = ['codeforces.com']

    def __init__(self, username, *args, **kwargs):
        super(CodeforcesAccountSpider, self).__init__(*args, **kwargs)

        self.username = username
        self.start_urls = [
            'http://codeforces.com/profile/%s' %
            username
        ]

    def parse(self, response):

        sel = Selector(response)

        item = AccountItem()
        item['origin_oj'] = 'codeforces'
        item['username'] = self.username

        item['rating'] = sel.xpath('//div[@class="info"]/ul/li[1]/span[1]/text()').\
            extract()[0]
        return item
