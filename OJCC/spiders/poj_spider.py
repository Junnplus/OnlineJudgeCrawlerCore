#-*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor as link
from scrapy.http import Request, FormRequest
from scrapy.selector import Selector
from OJCC.items import ProblemItem, SolutionItem, AccountItem
from datetime import datetime
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

class PojInitSpider(CrawlSpider):
    name = 'poj_init'
    allowed_domains = ['poj.org']

    start_urls = [
            'http://poj.org/problemlist'
    ]

    rules = [
        Rule(
            link(
                allow=('problemlist\?volume=[0-9]+'),
                unique=True
            )
        ),
        Rule(
            link(
                allow=('problem\?id=[0-9]+')
            ), callback='problem_item'
        )
    ]

    def problem_item(self, response):
        html = response.body.\
            replace('<=', ' &le; ').\
            replace(' < ', ' &lt; ').\
            replace(' > ', ' &gt; ').\
            replace('>=', ' &ge; ')

        sel = Selector(text=html)

        item = ProblemItem()
        print response
        item['origin_oj'] = 'poj'
        item['problem_id'] = response.url[-4:]
        item['problem_url'] = response.url
        item['title'] = sel.css('.ptt').xpath('./text()').extract()[0]
        item['description'] = sel.css('.ptx').extract()[0]
        item['input'] = sel.css('.ptx').extract()[1]
        item['output'] = sel.css('.ptx').extract()[2]
        try:
            item['time_limit'] = sel.css('.plm').re('Case\sT[\S*\s]*MS')[0][21:]
        except:
            item['time_limit'] = sel.css('.plm').re('T[\S*\s]*MS')[0][16:]
        item['memory_limit'] = sel.css('.plm').re('Me[\S*\s]*K')[0]
        item['sample_input'] = sel.css('.sio').extract()[0]
        item['sample_output'] = sel.css('.sio').extract()[1]
        item['update_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return item

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
        html = response.body.\
            replace('<=', ' &le; ').\
            replace(' < ', ' &lt; ').\
            replace(' > ', ' &gt; ').\
            replace('>=', ' &ge; ')

        sel = Selector(text=html)

        item = ProblemItem()
        item['origin_oj'] = 'poj'
        item['problem_id'] = self.problem_id
        item['problem_url'] = response.url
        item['title'] = sel.css('.ptt').xpath('./text()').extract()[0]
        item['description'] = sel.css('.ptx').extract()[0]
        item['input'] = sel.css('.ptx').extract()[1]
        item['output'] = sel.css('.ptx').extract()[2]
        try:
            item['time_limit'] = sel.css('.plm').re('Case\sT[\S*\s]*MS')[0][21:]
        except:
            item['time_limit'] = sel.css('.plm').re('T[\S*\s]*MS')[0][16:]
        item['memory_limit'] = sel.css('.plm').re('Me[\S*\s]*K')[0][18:]
        item['sample_input'] = sel.css('.sio').extract()[0]
        item['sample_output'] = sel.css('.sio').extract()[1]
        item['update_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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

    is_judged = False

    def __init__(self,
            solution_id=1,
            problem_id='1000',
            language='g++',
            source=None,
            username='sdutacm1',
            password='sdutacm', *args, **kwargs):
        super(PojSubmitSpider, self).__init__(*args, **kwargs)

        self.solution_id = solution_id
        self.username = username
        self.password = password
        self.problem_id = problem_id
        self.language = language
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
                        'language': LANGUAGE.get(self.language, '0'),
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
        item['solution_id'] = self.solution_id
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

                try:
                    item['memory'] = \
                        tr.xpath('.//td')[4].xpath('./text()').extract()[0]
                    item['time'] = \
                        tr.xpath('.//td')[5].xpath('./text()').extract()[0]
                except:
                    pass

                item['code_length'] = tr.xpath('.//td/text()').extract()[-2]
                item['result'] = tr.xpath('.//td').xpath('.//font/text()').extract()[0]
                self.is_judged = True
                return item

class PojAccountSpider(CrawlSpider):
    name = 'poj_user'
    allowed_domains = ['poj.org']
    login_url = 'http://poj.org/login'
    login_verify_url = 'http://poj.org/loginlog'

    is_login = False

    def __init__(self,
            username='sdutacm1',
            password='sdutacm', *args, **kwargs):
        super(PojAccountSpider, self).__init__(*args, **kwargs)

        self.username = username
        self.password = password

        self.start_urls = [
                "http://poj.org/userstatus?user_id=%s" % username
        ]

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
        return [Request(self.login_verify_url,
            callback = self.login_verify
        )]

    def login_verify(self, response):
        if response.url == self.login_verify_url:
            self.is_login = True
        for url in self.start_urls:
            yield self.make_requests_from_url(url)

    def parse(self, response):
        sel = Selector(response)

        item = AccountItem()
        item['origin_oj'] = 'poj'
        item['username'] = self.username
        if self.is_login:
            try:
                item['rank'] = sel.xpath('//center/table/tr')[1].\
                    xpath('.//td/font/text()').extract()[0]
                item['accept'] = sel.xpath('//center/table/tr')[2].\
                    xpath('.//td/a/text()').extract()[0]
                item['submit'] = sel.xpath('//center/table/tr')[3].\
                    xpath('.//td/a/text()').extract()[0]
                item['status'] = 'Authentication Success'
            except:
                item['status'] = 'Unknown Error'
        else:
            item['status'] = 'Authentication Failed'

        return item
