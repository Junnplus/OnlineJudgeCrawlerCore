from scrapy.spider import Spider
from scrapy.selector import Selector
from OJCC.items import ProblemItem

class HduSpider(Spider):
    name = 'hdu'
    allowed_domains = ['acm.hdu.edu.cn']

    def __init__(self, problem_id=None, *args, **kwargs):
        super(HduSpider, self).__init__(*args, **kwargs)
        self.start_urls = [
            'http://acm.hdu.edu.cn/showproblem.php?pid=%s' % problem_id
        ]

    def parse(self, response):
        sel = Selector(response)

        item = ProblemItem()
        item['title'] = sel.xpath('//h1/text()').extract()[0]
        item['description'] = sel.css('.panel_content').extract()[0]
        item['input'] = sel.css('.panel_content').extract()[1]
        item['output'] = sel.css('.panel_content').extract()[2]
        item['time_limit'] = sel.xpath('//b/span/text()').re('T[\S*\s]*S')[0]
        item['memory_limit'] = sel.xpath('//b/span/text()').re('Me[\S*\s]*K')[0]
        item['sample_input'] = sel.xpath('//pre').extract()[0]
        item['sample_output'] = sel.xpath('//pre').extract()[1]
        yield item
