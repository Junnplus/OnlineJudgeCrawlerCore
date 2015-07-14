from scrapy.spiders import Spider
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor as link
from scrapy.http import Request, FormRequest
from scrapy.selector import Selector
from OJCC.items import ProblemItem, SolutionItem, AccountItem
from base64 import b64decode
from datetime import datetime
import time
import re

LANGUAGE = {
        'g++': '0',
        'gcc': '1',
        'c++': '2',
        'c': '3',
        'pascal': '4',
        'java': '5',
        'c#': '6'
    }

class HduInitSpider(CrawlSpider):
    name = 'hdu_init'
    allowed_domains = ['acm.hdu.edu.cn']

    start_urls = [
            'http://acm.hdu.edu.cn/listproblem.php'
    ]

    rules = [
        Rule(
            link(
                allow=('listproblem.php\?vol=[0-9]+'),
                unique=True
            )),
        Rule(
            link(
                allow=('showproblem.php\?pid=[0-9]+')
            ), callback='problem_item')
    ]

    def problem_item(self, response):
        sel = Selector(response)

        item = ProblemItem()
        item['origin_oj'] = 'hdu'
        item['problem_id'] = response.url[-4:]
        item['problem_url'] = response.url
        item['title'] = sel.xpath('//h1/text()').extract()[0]
        item['description'] = sel.css('.panel_content').extract()[0]
        item['input'] = sel.css('.panel_content').extract()[1]
        item['output'] = sel.css('.panel_content').extract()[2]
        item['time_limit'] = \
            sel.xpath('//b/span/text()').re('T[\S*\s]*S')[0][12:]
        item['memory_limit'] = \
            sel.xpath('//b/span/text()').re('Me[\S*\s]*K')[0][14:]
        item['sample_input'] = sel.xpath('//pre').extract()[0]
        item['sample_output'] = sel.xpath('//pre').extract()[1]
        item['update_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return item

class HduProblemSpider(Spider):
    name = 'hdu_problem'
    allowed_domains = ['acm.hdu.edu.cn']

    def __init__(self, problem_id='1000', *args, **kwargs):
        self.problem_id = problem_id
        super(HduProblemSpider, self).__init__(*args, **kwargs)
        self.start_urls = [
            'http://acm.hdu.edu.cn/showproblem.php?pid=%s' % problem_id
        ]

    def parse(self, response):
        sel = Selector(response)

        item = ProblemItem()
        item['origin_oj'] = 'hdu'
        item['problem_id'] = self.problem_id
        item['problem_url'] = response.url
        item['title'] = sel.xpath('//h1/text()').extract()[0]
        item['description'] = sel.css('.panel_content').extract()[0]
        item['input'] = sel.css('.panel_content').extract()[1]
        item['output'] = sel.css('.panel_content').extract()[2]
        item['time_limit'] = \
            sel.xpath('//b/span/text()').re('T[\S*\s]*S')[0][12:]
        item['memory_limit'] = \
            sel.xpath('//b/span/text()').re('Me[\S*\s]*K')[0][14:]
        item['sample_input'] = sel.xpath('//pre').extract()[0]
        item['sample_output'] = sel.xpath('//pre').extract()[1]
        item['update_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return item

class HduSubmitSpider(CrawlSpider):
    name = 'hdu_submit'
    allowed_domains = ['acm.hdu.edu.cn']
    login_url = 'http://acm.hdu.edu.cn/userloginex.php?action=login'
    submit_url = 'http://acm.hdu.edu.cn/submit.php?action=submit'
    source = \
        'I2luY2x1ZGUgPHN0ZGlvLmg+CgppbnQgbWFpbigpCnsKICAgIGludCBhLGI7CiAgICBzY2FuZigiJWQgJWQiLCZhLCAmYik7CiAgICBwcmludGYoIiVkXG4iLGErYik7CiAgICByZXR1cm4gMDsKfQ=='

    start_urls = [
        'http://acm.hdu.edu.cn/status.php'
    ]

    rules = [
        Rule(link(allow=('/status.php\?first\S*status')), follow=True, callback='parse_start_url')
    ]

    is_judged = False

    def __init__(self,
            problem_id = '1000',
            language = 'g++',
            source=None,
            username = 'sdutacm1',
            password = 'sdutacm', *args, **kwargs):
        super(HduSubmitSpider, self).__init__(*args, **kwargs)

        self.username = username
        self.password = password
        self.problem_id = problem_id
        self.language = LANGUAGE.get(language, '0')
        if source is not None:
            self.source = source

    def start_requests(self):
        return [FormRequest(self.login_url,
                formdata = {
                        'username': self.username,
                        'userpass': self.password,
                        'login': 'Sign+In',
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
                        'problemid': self.problem_id,
                        'language': self.language,
                        'usercode': b64decode(self.source),
                        'check': '0'
                },
                callback = self.after_submit,
                dont_filter = True
        )]

    def after_submit(self, response):
        time.sleep(3)
        for url in self.start_urls :
            yield self.make_requests_from_url(url)

    def parse_start_url(self, response):
        if is_judged:
            self._rules = []

        sel = Selector(response)

        item = SolutionItem()
        for tr in sel.xpath('//table[@class="table_text"]/tr')[1:]:
            user = tr.xpath('.//td/a/text()').extract()[-1]
            _submit_time = tr.xpath('.//td/text()').extract()[1]
            submit_time = time.mktime(\
                    time.strptime(_submit_time, '%Y-%m-%d %H:%M:%S'))
            if submit_time > self.login_time and \
                    user == self.username:
                item['origin_oj'] = 'hdu'
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

                item['code_length'] = tr.xpath('.//td/a/text()').extract()[-2]
                item['result'] = tr.xpath('.//td').xpath('.//font/text()').extract()[0]
                self.is_judged = True
                return item

class HduAccountSpider(Spider):
    name = 'hdu_user'
    allowed_domains = ['acm.hdu.edu.cn']
    login_url = 'http://acm.hdu.edu.cn/userloginex.php?action=login'
    login_verify_url = 'http://acm.hdu.edu.cn/control_panel.php'

    is_login = False

    def __init__(self,
            username='sdutacm1',
            password='sdutacm', *args, **kwargs):
        super(HduAccountSpider, self).__init__(*args, **kwargs)

        self.username = username
        self.password = password

        self.start_urls = [
            'http://acm.hdu.edu.cn/userstatus.php?user=%s' % username
        ]

    def start_requests(self):
        return [FormRequest(self.login_url,
                formdata = {
                        'username': self.username,
                        'userpass': self.password,
                        'login': 'Sign+In',
                },
                callback = self.after_login,
                dont_filter = True
        )]

    def after_login(self, response):
        if not re.search(r'No such user or wrong password.', response.body):
            self.is_login = True
        for url in self.start_urls:
            yield self.make_requests_from_url(url)

    def parse(self, response):
        sel = Selector(response)

        item = AccountItem()
        item['origin_oj'] = 'hdu'
        item['username'] = self.username
        if self.is_login:
            try:
                item['rank'] = sel.xpath('//table')[3].\
                    xpath('./tr')[1].xpath('./td/text()')[1].extract()
                item['accept'] = sel.xpath('//table')[3].\
                    xpath('./tr')[3].xpath('./td/text()')[1].extract()
                item['submit'] = sel.xpath('//table')[3].\
                    xpath('./tr')[4].xpath('./td/text()')[1].extract()
                item['status'] = 'Authentication Success'
            except:
                item['status'] = 'Unknown Error'
        else:
            item['status'] = 'Authentication Failed'

        return item
