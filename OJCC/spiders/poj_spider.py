from scrapy.spider import Spider
from scrapy.http import Request, FormRequest
from scrapy.selector import Selector
from OJCC.items import ProblemItem

class PojProblemSpider(Spider):
    name = 'poj_problem'
    allowed_domains = ['poj.org']

    def __init__(self, problem_id='1000', *args, **kwargs):
        super(PojSpider, self).__init__(*args, **kwargs)
        self.start_urls = [
            'http://poj.org/problem?id=%s' % problem_id
        ]

    def parse(self, response):
        sel = Selector(response)

        item = ProblemItem()
        item['origin_oj'] = 'poj'
        item['problem_url'] = response.url
        item['title'] = sel.css('.ptt').xpath('./text()').extract()[0]
        item['description'] = sel.css('.ptx').extract()[0]
        item['input'] = sel.css('.ptx').extract()[1]
        item['output'] = sel.css('.ptx').extract()[2]
        item['time_limit'] = sel.css('.plm').re('T[\S*\s]*MS')[0]
        item['memory_limit'] = sel.css('.plm').re('Me[\S*\s]*K')[0]
        item['sample_input'] = sel.css('.sio').extract()[0]
        item['sample_output'] = sel.css('.sio').extract()[1]
        yield item

class PojSubmitSpider(Spider):
    name = 'poj_submit'
    allowed_domains = ['poj.org']
    login_url = 'http://poj.org/login'
    submit_url = 'http://poj.org/submit'
    source = \
        'I2luY2x1ZGUgPHN0ZGlvLmg+CgppbnQgbWFpbigpCnsKICAgIGludCBhLGI7CiAgICBzY2FuZigiJWQgJWQiLCZhLCAmYik7CiAgICBwcmludGYoIiVkXG4iLGErYik7CiAgICByZXR1cm4gMDsKfQ=='

    start_urls = [
        "http://poj.org/status"
    ]

    def __init__(self, problem_id='1000', language='0', source=None, *args, **kwargs):
        self.problem_id = problem_id
        self.language = language
        if source is not None:
            self.source = source

    def start_requests(self):
        return [FormRequest(self.login_url,
                formdata = {
                        'user_id1': 'sdutacm1',
                        'password1': 'sdutacm',
                        'B1': 'login',
                },
                callback = self.after_login,
                dont_filter = True
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
                dont_filter = True
        )]

    def after_submit(self, response):
        for url in self.start_urls :
            yield self.make_requests_from_url(url)
