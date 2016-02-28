# -*- coding: utf-8 -*-

from scrapy.spiders import Spider
from scrapy.selector import Selector
from ojcc.items import AccountItem


class BestcoderAccountSpider(Spider):
    name = 'bestcoder_user'
    allowed_domains = ['bestcoder.hdu.edu.cn']

    def __init__(self, username, *args, **kwargs):
        super(BestcoderAccountSpider, self).__init__(*args, **kwargs)

        self.username = username
        self.start_urls = [
            'http://bestcoder.hdu.edu.cn/rating.php?user=%s' % username
        ]

    def parse(self, response):

        sel = Selector(response)

        item = AccountItem()
        item['origin_oj'] = 'bestcoder'
        item['username'] = self.username

        item['rank'] = sel.xpath('//span[@class="bigggger"]/text()').\
            extract()[0]
        item['rating'] = sel.xpath('//span[@class="bigggger"]/text()').\
            extract()[1]
        return item
