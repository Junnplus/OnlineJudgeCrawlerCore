#-*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor as link
from scrapy.http import Request, FormRequest
from scrapy.selector import Selector
from OJCC.items import ProblemItem, SolutionItem
from base64 import b64decode
from datetime import datetime
import time

LANGUAGE = {
    'gcc': 'gcc',
    'g++': 'g++',
    'java': 'java',
    'pascal': 'pascal',
    'go': 'go',
    'lua': 'lua',
    'dao': 'dao',
    'perl': 'perl',
    'ruby': 'ruby',
    'haskell': 'haskell',
    'python2': 'python2',
    'python3': 'python3'
}

class SdutInitSpider(CrawlSpider):
    name = 'sdut_init'
    allowed_domains = ['acm.sdut.edu.cn']

    start_urls = [
        'http://acm.sdut.edu.cn/sdutoj/problem.php'
    ]

    rules = [
        Rule(
            link(
                allow=('problem.php\?page=[0-9]+'),
                unique=True
            )
        ),
        Rule(
            link(
                allow=('problem.php\?action\S*[0-9]+')
            ), callback='problem_item'
        )
    ]

    def problem_item(self, response):
        sel = Selector(response)

        item = ProblemItem()
        item['origin_oj'] = 'sdut'
        item['problem_id'] = response.url[-4:]
        item['problem_url'] = response.url
        item['title'] = sel.xpath('//center/h2/text()').extract()[0]
        item['description'] = sel.css('.pro_desc').extract()[0]
        item['input'] = sel.css('.pro_desc').extract()[1]
        item['output'] = sel.css('.pro_desc').extract()[2]
        item['time_limit'] = sel.xpath('//a/h5/text()').re('T[\S*\s]*s')[0][12:]
        item['memory_limit'] = \
            sel.xpath('//a/h5/text()').re('M[\S*\s]*K')[0][14:]
        item['sample_input'] = sel.xpath('//pre').extract()[0]
        item['sample_output'] = sel.xpath('//pre').extract()[1]
        item['update_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return item

class SdutProblemSpider(Spider):
    name = 'sdut_problem'
    allowed_domains = ['acm.sdut.edu.cn']

    def __init__(self, problem_id='1000', *args, **kwargs):
        self.problem_id = problem_id
        super(SdutProblemSpider, self).__init__(*args, **kwargs)
        self.start_urls = [
            'http://acm.sdut.edu.cn/sdutoj/problem.php?action=showproblem&problemid=%s'
                % problem_id
        ]

    def parse(self, response):
        sel = Selector(response)

        item = ProblemItem()
        item['origin_oj'] = 'sdut'
        item['problem_id'] = self.problem_id
        item['problem_url'] = response.url
        item['title'] = sel.xpath('//center/h2/text()').extract()[0]
        item['description'] = sel.css('.pro_desc').extract()[0]
        item['input'] = sel.css('.pro_desc').extract()[1]
        item['output'] = sel.css('.pro_desc').extract()[2]
        item['time_limit'] = sel.xpath('//a/h5/text()').re('T[\S*\s]*s')[0][12:]
        item['memory_limit'] = \
            sel.xpath('//a/h5/text()').re('M[\S*\s]*K')[0][14:]
        item['sample_input'] = sel.xpath('//pre').extract()[0]
        item['sample_output'] = sel.xpath('//pre').extract()[1]
        item['update_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return item

class SdutSubmitSpider(CrawlSpider):
    name = 'sdut_submit'
    allowed_domains = ['acm.sdut.edu.cn']
    login_url = 'http://acm.sdut.edu.cn/sdutoj/login.php?action=login'
    submit_url = 'http://acm.sdut.edu.cn/sdutoj/submit.php?action=submit'
    source = \
        'I2luY2x1ZGUgPHN0ZGlvLmg+CgppbnQgbWFpbigpCnsKICAgIGludCBhLGI7CiAgICBzY2FuZigiJWQgJWQiLCZhLCAmYik7CiAgICBwcmludGYoIiVkXG4iLGErYik7CiAgICByZXR1cm4gMDsKfQ=='

    start_urls = [
        "http://acm.sdut.edu.cn/sdutoj/status.php"
    ]

    rules = [
        Rule(
            link(
                allow=('status.php\?page=[0-9]+\S*'), \
                deny=('status.php\?page=1&\S*'),
                unique=True
            ),
            follow=True, callback='parse_start_url')
    ]

    is_judged = False

    def __init__(self,
            problem_id = '1000',
            language = 'g++',
            source = None,
            username = 'sdutacm1',
            password = 'sdutacm', *args, **kwargs):
        super(SdutSubmitSpider, self).__init__(*args, **kwargs)
        self.problem_id = problem_id
        self.language = LANGUAGE.get(language, 'g++')
        self.username = username
        self.password = password
        if source is not None:
            self.source = source

    def start_requests(self):
        return [FormRequest(self.login_url,
                formdata = {
                        'username': self.username,
                        'password': self.password,
                        'submit': '++%E7%99%BB+%E5%BD%95++'
                },
                callback = self.after_login,
                dont_filter = True
        )]

    def after_login(self, response):
        self.login_time = time.mktime(time.strptime(\
                response.headers['Date'], \
                '%a, %d %b %Y %H:%M:%S %Z')) + (8 * 60 * 60)
        time.sleep(1)
        return [FormRequest(self.submit_url,
                formdata = {
                    'Sub[problem_id]': self.problem_id,
                    'Sub[pro_lang]': self.language,
                    'Sub[code]': b64decode(self.source)
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
        for tr in sel.xpath('//table[@class="tablelist"]/tr')[1:]:
            user = tr.xpath('.//td/a/xmp/text()').extract()[0]
            _submit_time = tr.xpath('.//td/text()').extract()[-1]
            submit_time = time.mktime(\
                    time.strptime(_submit_time, '%Y-%m-%d %H:%M:%S'))
            if submit_time > self.login_time and \
                    user == self.username:
                item['origin_oj'] = 'sdut'
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
                    item['memory'] = []
                    item['time'] = []

                item['code_length'] = tr.xpath('.//td/text()').extract()[-2]
                item['result'] = tr.xpath('.//td').xpath('.//font/text()').extract()[0]
                self.is_judged = True
                return item
