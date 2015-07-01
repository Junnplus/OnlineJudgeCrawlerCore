from scrapy.spider import Spider
from scrapy.selector import Selector
from OJCC.items import ProblemItem

class FzuSpider(Spider):
    name = 'fzu'
    allowed_domains = ['acm.fzu.edu.cn']

    def __init__(self, problem_id=1000, *args, **kwargs):
        super(FzuSpider, self).__init__(*args, **kwargs)
        self.start_urls = [
            'http://acm.fzu.edu.cn/problem.php?pid=%s' % problem_id
        ]

    def parse(self, response):
        sel = Selector(response)

        item = ProblemItem()
        item['origin_oj'] = 'fzu'
        item['problem_url'] = response.url
        item['title'] = sel.xpath(
            '//div[contains(@class, "problem_title")]/b/text()').extract()[0]
        item['description'] = sel.css('.pro_desc').extract()[0]
        item['input'] = sel.css('.pro_desc').extract()[1]
        item['output'] = sel.css('.pro_desc').extract()[2]
        item['time_limit'] = sel.css('.problem_desc').re('T[\S*\s]*c')[0]
        item['memory_limit'] = sel.css('.problem_desc').re('M[\S*\s]*B')[0]
        item['sample_input'] = sel.css('.data').extract()[0]
        item['sample_output'] = sel.css('.data').extract()[1]
        yield item
