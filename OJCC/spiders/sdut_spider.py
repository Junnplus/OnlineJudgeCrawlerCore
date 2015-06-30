from scrapy.spider import Spider
from scrapy.selector import Selector
from OJCC.items import ProblemItem

class SdutSpider(Spider):
    name = 'sdut'
    allowed_domains = ['acm.sdut.edu.cn']

    def __init__(self, problem_id=None, *args, **kwargs):
        super(SdutSpider, self).__init__(*args, **kwargs)
        self.start_urls = [
            'http://acm.sdut.edu.cn/sdutoj/problem.php?action=showproblem&problemid=%s'
                % problem_id
        ]

    def parse(self, response):
        sel = Selector(response)

        item = ProblemItem()
        item['title'] = sel.xpath('//center/h2/text()').extract()[0]
        item['description'] = sel.css('.pro_desc').extract()[0]
        item['input'] = sel.css('.pro_desc').extract()[1]
        item['output'] = sel.css('.pro_desc').extract()[2]
        item['time_limit'] = sel.xpath('//a/h5/text()').re('T[\S*\s]*s')[0]
        item['memory_limit'] = sel.xpath('//a/h5/text()').re('M[\S*\s]*K')[0]
        item['sample_input'] = sel.xpath('//pre').extract()[0]
        item['sample_output'] = sel.xpath('//pre').extract()[1]
        yield item
