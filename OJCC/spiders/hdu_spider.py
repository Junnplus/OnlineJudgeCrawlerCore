from scrapy.spiders import Spider
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor as link
from scrapy.http import Request, FormRequest
from scrapy.selector import Selector
from OJCC.items import ProblemItem, SolutionItem, AccountItem, AcceptedItem
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
    problem_base_url = 'http://acm.hdu.edu.cn/showproblem.php?pid='

    start_urls = [
            'http://acm.hdu.edu.cn/listproblem.php'
    ]

    rules = [
        Rule(
            link(
                allow=('listproblem.php\?vol=[0-9]+'),
                unique=True,
            ),
            callback='problem_list'
        )
    ]

    def problem_list(self, response):
        sel = Selector(response)
        problems = sel.xpath('//script')[4].re('\(.+?\)')
        for problem in problems:
            problem_id = problem.split(',')[1]
            yield Request(self.problem_base_url + problem_id,
                callback=self.problem_item)

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
    login_verify_url = 'http://acm.hdu.edu.cn/control_panel.php'

    source = \
        'I2luY2x1ZGUgPHN0ZGlvLmg+CgppbnQgbWFpbigpCnsKICAgIGludCBhLGI7CiAgICBzY2FuZigiJWQgJWQiLCZhLCAmYik7CiAgICBwcmludGYoIiVkXG4iLGErYik7CiAgICByZXR1cm4gMDsKfQ=='

    start_urls = [
        'http://acm.hdu.edu.cn/status.php'
    ]

    is_login = False

    rules = [
        Rule(link(allow=('/status.php\?first\S*status')), follow=True, callback='parse_start_url')
    ]

    def __init__(self,
            solution_id = 1,
            problem_id = '1000',
            language = 'g++',
            source=None,
            username = 'sdutacm1',
            password = 'sdutacm', *args, **kwargs):
        super(HduSubmitSpider, self).__init__(*args, **kwargs)

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

            self.login_time = time.mktime(time.strptime(\
                    response.headers['Date'], \
                    '%a, %d %b %Y %H:%M:%S %Z')) + (8 * 60 * 60)
            time.sleep(1)
            return [FormRequest(self.submit_url,
                    formdata = {
                            'problemid': self.problem_id,
                            'language': LANGUAGE.get(self.language, '0'),
                            'usercode': b64decode(self.source),
                            'check': '0'
                    },
                    callback = self.after_submit,
                    dont_filter = True
            )]
        else:
            return Request(self.start_urls[0], callback=self.parse_start_url)

    def after_submit(self, response):
        time.sleep(3)
        for url in self.start_urls :
            yield self.make_requests_from_url(url)

    def parse_start_url(self, response):

        sel = Selector(response)

        item = SolutionItem()
        item['solution_id'] = self.solution_id
        item['origin_oj'] = 'hdu'
        item['problem_id'] = self.problem_id
        item['language'] = self.language

        if self.is_login:
            for tr in sel.xpath('//table[@class="table_text"]/tr')[1:]:
                user = tr.xpath('.//td/a/text()').extract()[-1]
                _submit_time = tr.xpath('.//td/text()').extract()[1]
                submit_time = time.mktime(\
                        time.strptime(_submit_time, '%Y-%m-%d %H:%M:%S'))
                if submit_time > self.login_time and \
                        user == self.username:
                    item['submit_time'] = _submit_time
                    item['run_id'] = tr.xpath('.//td/text()').extract()[0]

                    try:
                        item['memory'] = \
                            tr.xpath('.//td')[4].xpath('./text()').extract()[0]
                        item['time'] = \
                            tr.xpath('.//td')[5].xpath('./text()').extract()[0]
                    except:
                        pass

                    item['code_length'] = tr.xpath('.//td/a/text()').extract()[-2]
                    item['result'] = tr.xpath('.//td').xpath('.//font/text()').extract()[0]
                    self._rules = []
                    return item
        else:
            item['result'] = 'Submit Error'
            self._rules = []
            return item

class HduAccountSpider(Spider):
    name = 'hdu_user'
    allowed_domains = ['acm.hdu.edu.cn']
    login_url = 'http://acm.hdu.edu.cn/userloginex.php?action=login'
    login_verify_url = 'http://acm.hdu.edu.cn/control_panel.php'
    accepted_url = \
        'http://acm.hdu.edu.cn/status.php?first=&pid=&user=%s&lang=0&status=5'

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
                item['nickname'] = sel.xpath('//h1/text()').extract()[0]
                self.nickname = item['nickname']
                item['rank'] = sel.xpath('//table')[3].\
                    xpath('./tr')[1].xpath('./td/text()')[1].extract()
                item['accept'] = sel.xpath('//table')[3].\
                    xpath('./tr')[3].xpath('./td/text()')[1].extract()
                item['submit'] = sel.xpath('//table')[3].\
                    xpath('./tr')[4].xpath('./td/text()')[1].extract()
                item['solved'] = sel.xpath('//script')[5].re('[0-9]{4}')
                yield Request(self.accepted_url % self.username,
                    callback = self.accepted
                )
                item['status'] = 'Authentication Success'
            except:
                item['status'] = 'Unknown Error'
        else:
            item['status'] = 'Authentication Failed'

        yield item

    def accepted(self, response):

        sel = Selector(response)

        item = AcceptedItem()

        item['origin_oj'] = 'hdu'
        item['username'] = self.username
        next_url = sel.xpath('.//p/a/@href')[2].extract()
        table_tr = sel.xpath('//table[@class="table_text"]/tr')[1:]
        for tr in table_tr:
            name = tr.xpath('.//td/a/text()').extract()[-1]
            problem_id = tr.xpath('.//td[4]/a/text()').extract()[0]
            submit_time = tr.xpath('.//td/text()').extract()[1]

            if name == self.nickname:
                item['problem_id'] = problem_id
                item['first_submit_time'] = submit_time
                yield item

        if table_tr:
            yield Request('http://' + self.allowed_domains[0] + next_url,
                callback = self.accepted
            )
