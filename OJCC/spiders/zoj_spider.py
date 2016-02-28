from scrapy.spiders import Spider
from scrapy.selector import Selector
from OJCC.items import ProblemItem


class ZojSpider(Spider):
    name = 'zoj'
    allowed_domains = ['acm.zju.edu.cn']

    def __init__(self, problem_id=None, *args, **kwargs):
        super(ZojSpider, self).__init__(*args, **kwargs)
        self.start_urls = [
            'http://acm.zju.edu.cn/onlinejudge/showProblem.do?problemCode=%s' %
            problem_id
        ]

    def parse(self, response):
        sel = Selector(response)

        item = ProblemItem()
        item['title'] = sel.css(
            '.bigProblemTitle').xpath('./text()').extract()[0]
        item['description'] = sel.css('.ptx').extract()[0]
        item['input'] = sel.css('.ptx').extract()[1]
        item['output'] = sel.css('.ptx').extract()[2]
        item['time_limit'] = sel.xpath('//center[2]').re('T[\S*\s]*s')[0]
        item['memory_limit'] = sel.xpath('//center[2]').re('M[\S*\s]*B')[0]
        item['sample_input'] = sel.xpath('//pre').extract()[0]
        item['sample_output'] = sel.xpath('//pre').extract()[1]
        yield item
