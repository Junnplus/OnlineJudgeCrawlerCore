from scrapy.spider import Spider
from scrapy.http import Request, FormRequest
from scrapy.selector import Selector
from OJCC.items import ProblemItem

class SdutProblemSpider(Spider):
    name = 'sdut_problem'
    allowed_domains = ['acm.sdut.edu.cn']

    def __init__(self, problem_id='1000', *args, **kwargs):
        super(SdutSpider, self).__init__(*args, **kwargs)
        self.start_urls = [
            'http://acm.sdut.edu.cn/sdutoj/problem.php?action=showproblem&problemid=%s'
                % problem_id
        ]

    def parse(self, response):
        sel = Selector(response)

        item = ProblemItem()
        item['origin_oj'] = 'sdut'
        item['problem_url'] = response.url
        item['title'] = sel.xpath('//center/h2/text()').extract()[0]
        item['description'] = sel.css('.pro_desc').extract()[0]
        item['input'] = sel.css('.pro_desc').extract()[1]
        item['output'] = sel.css('.pro_desc').extract()[2]
        item['time_limit'] = sel.xpath('//a/h5/text()').re('T[\S*\s]*s')[0]
        item['memory_limit'] = sel.xpath('//a/h5/text()').re('M[\S*\s]*K')[0]
        item['sample_input'] = sel.xpath('//pre').extract()[0]
        item['sample_output'] = sel.xpath('//pre').extract()[1]
        yield item

class SdutSubmitSpider(Spider):
    name = 'sdut_submit'
    allowed_domains = ['acm.sdut.edu.cn']
    login_url = 'http://acm.sdut.edu.cn/sdutoj/login.php?action=login'
    submit_url = 'http://acm.sdut.edu.cn/sdutoj/submit.php?action=submit'
    source = \
        'I2luY2x1ZGUgPHN0ZGlvLmg+CgppbnQgbWFpbigpCnsKICAgIGludCBhLGI7CiAgICBzY2FuZigiJWQgJWQiLCZhLCAmYik7CiAgICBwcmludGYoIiVkXG4iLGErYik7CiAgICByZXR1cm4gMDsKfQ=='

    start_urls = [
        "http://acm.sdut.edu.cn/status.php"
    ]

    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip,deflate",
        "Accept-Language": "en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4",
        "Connection": "keep-alive",
        "Content-Type":" application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",
    }

    def __init__(self, problem_id='1000', language='g++', source=None, *args, **kwargs):
        self.problem_id = problem_id
        self.language = language
        if source is not None:
            self.source = source

    def start_requests(self):
        return [FormRequest(self.login_url,
                headers = self.headers,
                formdata = {
                        'username': 'sdutacm1',
                        'password': 'sdutacm',
                        'submit': '++%E7%99%BB+%E5%BD%95++'
                },
                callback = self.after_login,
                dont_filter = True
        )]

    def after_login(self, response):
        return [FormRequest(self.submit_url,
                headers = self.headers,
                formdata = {
                    'Sub[problem_id]': self.problem_id,
                    'Sub[pro_lang]': self.language,
                    'Sub[sub_code]': self.source,
                },
                callback = self.after_submit,
                dont_filter = True
        )]

    def after_submit(self, response):
        for url in self.start_urls :
            yield self.make_requests_from_url(url)
