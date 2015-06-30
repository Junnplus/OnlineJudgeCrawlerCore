from scrapy.spider import Spider
from scrapy.selector import Selector
from OJCC.items import ProblemItem

class PojSpider(Spider):
    name = 'poj'
    allowed_domains = ['poj.org']

    def __init__(self, problem_id=None):
        self.start_urls = [
            'http://poj.org/problem?id=%s' % problem_id
        ]

    def parse(self, response):
        sel = Selector(response)

        item = ProblemItem()
        item['title'] = sel.css('.ptt').xpath('./text()').extract()[0]
        item['description'] = sel.css('.ptx').extract()[0]
        item['input'] = sel.css('.ptx').extract()[1]
        item['output'] = sel.css('.ptx').extract()[2]
        item['time_limit'] = sel.css('.plm').re('T[\S*\s]*MS')[0]
        item['memory_limit'] = sel.css('.plm').re('Me[\S*\s]*K')[0]
        item['sample_input'] = sel.css('.sio').extract()[0]
        item['sample_output'] = sel.css('.sio').extract()[1]
        yield item
