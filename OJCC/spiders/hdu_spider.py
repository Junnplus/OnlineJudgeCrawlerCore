from scrapy.spiders import Spider
from scrapy.http import Request, FormRequest
from scrapy.selector import Selector
from OJCC.items import ProblemItem

class HduProblemSpider(Spider):
    name = 'hdu_problem'
    allowed_domains = ['acm.hdu.edu.cn']

    def __init__(self, problem_id='1000', *args, **kwargs):
        super(HduSpider, self).__init__(*args, **kwargs)
        self.start_urls = [
            'http://acm.hdu.edu.cn/showproblem.php?pid=%s' % problem_id
        ]

    def parse(self, response):
        sel = Selector(response)

        item = ProblemItem()
        item['origin_oj'] = 'hdu'
        item['problem_url'] = response.url
        item['title'] = sel.xpath('//h1/text()').extract()[0]
        item['description'] = sel.css('.panel_content').extract()[0]
        item['input'] = sel.css('.panel_content').extract()[1]
        item['output'] = sel.css('.panel_content').extract()[2]
        item['time_limit'] = sel.xpath('//b/span/text()').re('T[\S*\s]*S')[0]
        item['memory_limit'] = sel.xpath('//b/span/text()').re('Me[\S*\s]*K')[0]
        item['sample_input'] = sel.xpath('//pre').extract()[0]
        item['sample_output'] = sel.xpath('//pre').extract()[1]
        yield item

class HduSubmitSpider(Spider):
    name = 'hdu_submit'
    allowed_domains = ['acm.hdu.edu.cn']
    login_url = 'http://acm.hdu.edu.cn/userloginex.php?action=login'
    submit_url = 'http://acm.hdu.edu.cn/submit.php?action=submit'
    source = \
        'I2luY2x1ZGUgPHN0ZGlvLmg+CgppbnQgbWFpbigpCnsKICAgIGludCBhLGI7CiAgICBzY2FuZigiJWQgJWQiLCZhLCAmYik7CiAgICBwcmludGYoIiVkXG4iLGErYik7CiAgICByZXR1cm4gMDsKfQ=='

    start_urls = [
        'http://acm.hdu.edu.cn/status.php'
    ]

    def __init__(self, problem_id='1000', language='0', source=None, *args, **kwargs):
        self.problem_id = problem_id
        self.language = language
        if source is not None:
            self.source = source

    def start_requests(self):
        return [FormRequest(self.login_url,
                formdata = {
                        'username': 'sdutacm1',
                        'userpass': 'sdutacm',
                        'login': 'Sign+In',
                },
                callback = self.after_login,
                dont_filter = True
        )]

    def after_login(self, response):
        return [FormRequest(self.submit_url,
                formdata = {
                        'problemid': self.problem_id,
                        'language': self.language,
                        'usercode': self.source,
                        'check': '0'
                },
                callback = self.after_submit,
                dont_filter = True
        )]

    def after_submit(self, response):
        for url in self.start_urls :
            yield self.make_requests_from_url(url)
