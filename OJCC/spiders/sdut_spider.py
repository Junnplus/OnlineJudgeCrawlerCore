from scrapy.spider import Spider
from OJCC.items import ProblemItem

class SdutSpider(Spider):
    name = 'sdut'
    allowed_domains = ['acm.sdut.edu.cn']
    start_urls = [
        'http://acm.sdut.edu.cn/sdutoj/problem.php?action=showproblem&problemid=1018'
        ]

    def parse(self, response):
        item = ProblemItem()
        item['title'] = response.xpath('//center/h2').extract()[0]
        item['description'] = response.css('.pro_desc').extract()[0]
        item['input'] = response.css('.pro_desc').extract()[1]
        item['output'] = response.css('.pro_desc').extract()[2]
        item['time_limit'] = response.xpath('//a/h5/text()').re('T[\S*\s]*s')[0]
        item['memory_limit'] = response.xpath('//a/h5/text()').re('M[\S*\s]*K')[0]
        item['sample_input'] = response.xpath('//pre').extract()[0]
        item['sample_output'] = response.xpath('//pre').extract()[1]
        yield item
