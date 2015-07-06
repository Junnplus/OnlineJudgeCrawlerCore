from scrapy.spiders import Spider
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor as link
from scrapy.http import Request, FormRequest
from scrapy.selector import Selector
from OJCC.items import ProblemItem, SolutionItem
from time import sleep
from datetime import datetime

class PojProblemSpider(Spider):
    name = 'poj_problem'
    allowed_domains = ['poj.org']

    def __init__(self, problem_id='1000', *args, **kwargs):
        self.problem_id = problem_id
        super(PojSpider, self).__init__(*args, **kwargs)
        self.start_urls = [
            'http://poj.org/problem?id=%s' % problem_id
        ]

    def parse(self, response):
        sel = Selector(response)

        item = ProblemItem()
        item['origin_oj'] = 'poj'
        item['problem_id'] = self.problem_id
        item['problem_url'] = response.url
        item['title'] = sel.css('.ptt').xpath('./text()').extract()[0]
        item['description'] = sel.css('.ptx').extract()[0]
        item['input'] = sel.css('.ptx').extract()[1]
        item['output'] = sel.css('.ptx').extract()[2]
        item['time_limit'] = sel.css('.plm').re('T[\S*\s]*MS')[0]
        item['memory_limit'] = sel.css('.plm').re('Me[\S*\s]*K')[0]
        item['sample_input'] = sel.css('.sio').extract()[0]
        item['sample_output'] = sel.css('.sio').extract()[1]
        return item

class PojSubmitSpider(CrawlSpider):
    name = 'poj_submit'
    allowed_domains = ['poj.org']
    login_url = 'http://poj.org/login'
    submit_url = 'http://poj.org/submit'
    source = \
        'I2luY2x1ZGUgPHN0ZGlvLmg+CgppbnQgbWFpbigpCnsKICAgIGludCBhLGI7CiAgICBzY2FuZigiJWQgJWQiLCZhLCAmYik7CiAgICBwcmludGYoIiVkXG4iLGErYik7CiAgICByZXR1cm4gMDsKfQ=='

    start_urls = [
        "http://poj.org/status"
    ]

    rules = [
        Rule(link(allow=('/status\?top=[0-9]+'), deny=('status\?bottom=[0-9]+')), follow=True, callback='parse_start_url')
    ]

    username = 'sdutacm1'
    password = 'sdutacm'

    def __init__(self,
            problem_id='1000',
            language='0',
            source=None,
            *args, **kwargs):
        super(PojSubmitSpider, self).__init__(*args, **kwargs)

        self.problem_id = problem_id
        self.language = language
        if source is not None:
            self.source = source

    def start_requests(self):
        self.login_time = datetime.now()
        return [FormRequest(self.login_url,
                formdata = {
                        'user_id1': self.username,
                        'password1': self.password,
                        'B1': 'login',
                },
                callback = self.after_login,
        )]

    def after_login(self, response):
        return [FormRequest(self.submit_url,
                formdata = {
                        'problem_id': self.problem_id,
                        'language': self.language,
                        'source': self.source,
                        'submit': 'Submit',
                        'encoded': '1'
                },
                callback = self.after_submit,
        )]

    def after_submit(self, response):
        sleep(1)
        for url in self.start_urls:
            yield self.make_requests_from_url(url)

    def parse_start_url(self, response):

        sel = Selector(response)

        item = SolutionItem()
        for tr in sel.xpath('//table')[-1].xpath('.//tr')[1:]:
            user = tr.xpath('.//td/a/text()').extract()[0]
            _submit_time = tr.xpath('.//td/text()').extract()[-1]
            submit_time = datetime.strptime(_submit_time, '%Y-%m-%d %H:%M:%S')
            if submit_time > self.login_time and \
                    user == self.username:
                item['origin_oj'] = 'poj'
                try:
                    item['problem_id'] = tr.xpath('.//td/a/text()').extract()[1]
                    item['language'] = tr.xpath('.//td/a/text()').extract()[-1]
                    item['run_id'] = tr.xpath('.//td/text()').extract()[0]
                    item['memory'] = tr.xpath('.//td')[4].xpath('./text()').extract()
                    item['time'] = tr.xpath('.//td')[5].xpath('./text()').extract()
                    item['submit_time'] = _submit_time
                    item['code_length'] = tr.xpath('.//td/text()').extract()[-2]
                    item['result'] = tr.xpath('.//td').xpath('.//font/text()').extract()[0]
                    yield item
                except IndexError:
                    continue
