from scrapy.spiders import Spider
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor as link
from scrapy.http import Request, FormRequest
from scrapy.selector import Selector
from OJCC.items import ProblemItem, SolutionItem
import time

LANGUAGE = {
        'g++': '0',
        'gcc': '1',
        'java': '2',
        'pascal': '3',
        'c++': '4',
        'c': '5',
        'fortran': '6'
    }

class PojProblemSpider(Spider):
    name = 'poj_problem'
    allowed_domains = ['poj.org']

    def __init__(self, problem_id='1000', *args, **kwargs):
        self.problem_id = problem_id
        super(PojProblemSpider, self).__init__(*args, **kwargs)
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

    is_judged = False

    def __init__(self,
            problem_id='1000',
            language='g++',
            source=None,
            *args, **kwargs):
        super(PojSubmitSpider, self).__init__(*args, **kwargs)

        self.problem_id = problem_id
        self.language = LANGUAGE.get(language, '0')
        if source is not None:
            self.source = source

    def start_requests(self):
        return [FormRequest(self.login_url,
                formdata = {
                        'user_id1': self.username,
                        'password1': self.password,
                        'B1': 'login',
                },
                callback = self.after_login,
        )]

    def after_login(self, response):
        self.login_time = time.mktime(time.strptime(\
                response.headers['Date'], \
                '%a, %d %b %Y %H:%M:%S %Z')) + (8 * 60 * 60)
        time.sleep(1)
        return [FormRequest(self.submit_url,
                formdata = {
                        'problem_id': self.problem_id,
                        'language': self.language,
                        'source': self.source,
                        'submit': 'Submit',
                        'encoded': '1'
                },
                callback = self.after_submit,
                dont_filter = True
        )]

    def after_submit(self, response):
        time.sleep(3)
        for url in self.start_urls:
            yield self.make_requests_from_url(url)

    def parse_start_url(self, response):
        if self.is_judged:
            self._rules = []

        sel = Selector(response)

        item = SolutionItem()
        for tr in sel.xpath('//table')[-1].xpath('.//tr')[1:]:
            user = tr.xpath('.//td/a/text()').extract()[0]
            _submit_time = tr.xpath('.//td/text()').extract()[-1]
            submit_time = time.mktime(\
                    time.strptime(_submit_time, '%Y-%m-%d %H:%M:%S'))
            if submit_time > self.login_time and \
                    user == self.username:
                item['origin_oj'] = 'poj'
                item['problem_id'] = self.problem_id
                item['language'] = self.language
                item['submit_time'] = _submit_time
                item['run_id'] = tr.xpath('.//td/text()').extract()[0]

                item['memory'] = tr.xpath('.//td')[4].xpath('./text()').extract()
                item['time'] = tr.xpath('.//td')[5].xpath('./text()').extract()
                item['code_length'] = tr.xpath('.//td/text()').extract()[-2]
                item['result'] = tr.xpath('.//td').xpath('.//font/text()').extract()[0]
                self.is_judged = True
                return item
