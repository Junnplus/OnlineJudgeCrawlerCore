# -*- coding: utf-8 -*-

import time
from datetime import datetime
from urllib import urlencode

from scrapy.spiders import Spider
from scrapy.spiders import CrawlSpider
from scrapy.spiders import Rule
from scrapy.http import Request
from scrapy.http import FormRequest
from scrapy.linkextractors import LinkExtractor as link
from scrapy.selector import Selector
from scrapy.exceptions import CloseSpider

from OJCC.items import ProblemItem
from OJCC.items import SolutionItem
from OJCC.items import AccountItem

TABLE_TR_XPATH = '//table[@class="a"]/tr[position()>1]'
PROBLEM_ID_XPATH = './/td[3]/a/text()'
SUBMIT_TIME_XPATH = './/td[last()]/text()'
NICKNAME_XPATH = './/td/a/text()'
RESTRICT_XPATHS = ('/html/body/p[2]')
RULE_REGEX = 'status\S+top=\d+'

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
    name = 'poj_init_spider'
    allowed_domains = ['poj.org']

    start_urls = [
        'http://poj.org/problemlist'
    ]

    download_delay = 5

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
            item['time_limit'] = sel.css(
                '.plm').re('Case\sT[\S*\s]*MS')[0][21:]
        except:
            item['time_limit'] = sel.css('.plm').re('T[\S*\s]*MS')[0][16:]
        item['memory_limit'] = sel.css('.plm').re('Me[\S*\s]*K')[0]
        item['sample_input'] = sel.css('.sio').extract()[0]
        item['sample_output'] = sel.css('.sio').extract()[1]
        item['update_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return item


class PojProblemSpider(Spider):
    name = 'poj_problem_spider'
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
            item['time_limit'] = sel.css(
                '.plm').re('Case\sT[\S*\s]*MS')[0][21:]
        except:
            item['time_limit'] = sel.css('.plm').re('T[\S*\s]*MS')[0][16:]
        item['memory_limit'] = sel.css('.plm').re('Me[\S*\s]*K')[0][18:]
        item['sample_input'] = sel.css('.sio').extract()[0]
        item['sample_output'] = sel.css('.sio').extract()[1]
        item['update_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return item


class PojSubmitSpider(CrawlSpider):
    name = 'poj_submit_spider'
    allowed_domains = ['poj.org']
    login_url = 'http://poj.org/login'
    submit_url = 'http://poj.org/submit'
    login_verify_url = 'http://poj.org/loginlog'
    source = 'I2luY2x1ZGUgPHN0ZGlvLmg+CgppbnQgbWFpbigpCnsKI\
              CAgIGludCBhLGI7CiAgICBzY2FuZigiJWQgJWQiLCZhLC\
              AmYik7CiAgICBwcmludGYoIiVkXG4iLGErYik7CiAgICByZXR1cm4gMDsKfQ=='

    start_urls = [
        "http://poj.org/status"
    ]

    download_delay = 0.5

    rules = [
        Rule(link(
            allow=('/status\?top=[0-9]+'),
            deny=('status\?bottom=[0-9]+')),
            follow=True, callback='parse_start_url')
    ]

    is_login = False

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
        return [FormRequest(
            self.login_url,
            formdata={
                'user_id1': self.username,
                'password1': self.password,
                'B1': 'login',
            },
            callback=self.after_login,
        )]

    def after_login(self, response):
        return [Request(
            self.login_verify_url,
            callback=self.login_verify
        )]

    def login_verify(self, response):
        if response.url == self.login_verify_url:
            self.is_login = True

            self.login_time = time.mktime(time.strptime(
                response.headers['Date'],
                '%a, %d %b %Y %H:%M:%S %Z')) + (8 * 60 * 60)
            time.sleep(1)
            return [FormRequest(
                self.submit_url,
                formdata={
                    'problem_id': self.problem_id,
                    'language': LANGUAGE.get(self.language, '0'),
                    'source': self.source,
                    'submit': 'Submit',
                    'encoded': '1'
                },
                callback=self.after_submit,
                dont_filter=True
            )]
        else:
            return Request(self.start_urls[0], callback=self.parse_start_url)

    def after_submit(self, response):
        time.sleep(3)
        for url in self.start_urls:
            yield self.make_requests_from_url(url)

    def parse_start_url(self, response):

        sel = Selector(response)

        item = SolutionItem()
        item['solution_id'] = self.solution_id
        item['origin_oj'] = 'poj'
        item['problem_id'] = self.problem_id
        item['language'] = self.language

        if self.is_login:
            for tr in sel.xpath('//table')[-1].xpath('.//tr')[1:]:
                user = tr.xpath('.//td/a/text()').extract()[0]
                _submit_time = tr.xpath('.//td/text()').extract()[-1]
                submit_time = time.mktime(
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

                    item['code_length'] = tr.xpath(
                        './/td/text()').extract()[-2]
                    item['result'] = tr.xpath(
                        './/td').xpath('.//font/text()').extract()[0]
                    self._rules = []
                    return item
        else:
            item['result'] = 'Submit Error'
            self._rules = []
            return item


class PojAccountSpider(Spider):
    name = 'poj_user_spider'
    allowed_domains = ['poj.org']
    login_url = 'http://poj.org/login'
    login_verify_url = 'http://poj.org/loginlog'

    download_delay = 1
    is_login = False
    solved = {}

    def __init__(self, username, password, *args, **kwargs):
        super(PojAccountSpider, self).__init__(*args, **kwargs)

        self.username = username
        self.password = password

        self.start_urls = [
            "http://poj.org/userstatus?user_id=%s" % username
        ]

    def start_requests(self):
        return [FormRequest(
            self.login_url,
            formdata={
                'user_id1': self.username,
                'password1': self.password,
                'B1': 'login',
            },
            callback=self.after_login,
        )]

    def after_login(self, response):
        return [Request(
            self.login_verify_url,
            callback=self.login_verify
        )]

    def login_verify(self, response):
        if response.url == self.login_verify_url:
            self.is_login = True
        for url in self.start_urls:
            yield self.make_requests_from_url(url)

    def parse(self, response):
        sel = Selector(response)

        self.item = AccountItem()
        self.item['origin_oj'] = 'poj'
        self.item['username'] = self.username
        if self.is_login:
            try:
                self.item['rank'] = sel.xpath('//center/table/tr')[1].\
                    xpath('.//td/font/text()').extract()[0]
                self.item['accept'] = sel.xpath('//center/table/tr')[2].\
                    xpath('.//td/a/text()').extract()[0]
                self.item['submit'] = sel.xpath('//center/table/tr')[3].\
                    xpath('.//td/a/text()').extract()[0]
                self.item['status'] = 'Authentication Success'
            except:
                self.item['status'] = 'Unknown Error'
        else:
            self.item['status'] = 'Authentication Failed'

        yield self.item


class PojSolvedSpider(CrawlSpider):
    name = 'poj_solved_spider'
    allowed_domains = ['poj.org']
    status_url = 'http://poj.org/status'
    download_delay = 10
    rules = [Rule(link(allow=(RULE_REGEX),
                       restrict_xpaths=RESTRICT_XPATHS,
                       unique=True),
                  follow=True,
                  callback='parse_item')]
    solved = {}

    def __init__(self, username, *args, **kwargs):
        super(PojSolvedSpider,
              self).__init__(*args, **kwargs)

        self.origin_oj = 'poj'
        self.username = username
        self.start_urls = [
            '{0}?{1}'.format(
                self.status_url,
                urlencode(dict(user_id=username,
                               result=0)))]

    def parse_start_url(self, response):
        return self.parse_item(response)

    def parse_item(self, response):
        sel = Selector(response)
        items = sel.xpath(TABLE_TR_XPATH)

        for item in items:
            nickname = item.xpath(
                NICKNAME_XPATH).extract()[0]
            problem_id = item.xpath(
                PROBLEM_ID_XPATH).extract()[0].strip()
            submit_time = item.xpath(
                SUBMIT_TIME_XPATH).extract()[0].split(' ')[0]

            if nickname == self.username:
                self.solved[problem_id] = submit_time

        if not items:
            yield AccountItem(**dict(
                origin_oj=self.origin_oj,
                username=self.username,
                solved=self.solved
            ))
            raise CloseSpider('Crawl finished')

        return
