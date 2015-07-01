from scrapy.spider import Spider
from scrapy.http import Request, FormRequest
from scrapy.selector import Selector
from OJCC.items import ProblemItem

class FzuProblemSpider(Spider):
    name = 'fzu_problem'
    allowed_domains = ['acm.fzu.edu.cn']

    def __init__(self, problem_id='1000', *args, **kwargs):
        super(FzuSpider, self).__init__(*args, **kwargs)
        self.start_urls = [
            'http://acm.fzu.edu.cn/problem.php?pid=%s' % problem_id
        ]

    def parse(self, response):
        sel = Selector(response)

        item = ProblemItem()
        item['origin_oj'] = 'fzu'
        item['problem_url'] = response.url
        item['title'] = sel.xpath(
            '//div[contains(@class, "problem_title")]/b/text()').extract()[0]
        item['description'] = sel.css('.pro_desc').extract()[0]
        item['input'] = sel.css('.pro_desc').extract()[1]
        item['output'] = sel.css('.pro_desc').extract()[2]
        item['time_limit'] = sel.css('.problem_desc').re('T[\S*\s]*c')[0]
        item['memory_limit'] = sel.css('.problem_desc').re('M[\S*\s]*B')[0]
        item['sample_input'] = sel.css('.data').extract()[0]
        item['sample_output'] = sel.css('.data').extract()[1]
        yield item

class FzuSubmitSpider(Spider):
    name = 'fzu_submit'
    allowed_domains = ['acm.fzu.edu.cn']
    login_url = 'http://acm.fzu.edu.cn/login.php?act=1&dir='
    submit_url = 'http://acm.fzu.edu.cn/submit.php?act=5'
    source = \
        'I2luY2x1ZGUgPHN0ZGlvLmg+CgppbnQgbWFpbigpCnsKICAgIGludCBhLGI7CiAgICBzY2FuZigiJWQgJWQiLCZhLCAmYik7CiAgICBwcmludGYoIiVkXG4iLGErYik7CiAgICByZXR1cm4gMDsKfQ=='

    start_urls = [
            "http://acm.fzu.edu.cn/log.php"
    ]

    def __init__(self, problem_id='1000', language='0', source=None, *args, **kwargs):
        self.problem_id = problem_id
        self.language = language
        if source is not None:
            self.source = source

    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip,deflate",
        "Accept-Language": "en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4",
        "Connection": "keep-alive",
        "Content-Type":" application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",
    }

    def start_requests(self):
        return [FormRequest(self.login_url,
                headers = self.headers,
                formdata = {
                        'uname': 'sdutacm1',
                        'upassword': 'sdutacm',
                        'submit': 'Submit',
                },
                callback = self.after_login,
                dont_filter = True
        )]

    def after_login(self, response):
        return [FormRequest(self.submit_url,
                headers = self.headers,
                formdata = {
                        'pid': self.problem_id,
                        'lang': self.language,
                        'code': self.source,
                        'submit': 'Submit',
                },
                callback = self.after_submit,
                dont_filter = True
        )]

    def after_submit(self, response):
        for url in self.start_urls :
            yield self.make_requests_from_url(url)
