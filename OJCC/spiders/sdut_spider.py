from scrapy.spiders import Spider, CrawlSpider
from scrapy.http import Request, FormRequest
from scrapy.selector import Selector
from OJCC.items import ProblemItem

class SdutProblemSpider(Spider):
    name = 'sdut_problem'
    allowed_domains = ['acm.sdut.edu.cn']

    def __init__(self, problem_id='1000', *args, **kwargs):
        super(SdutProblemSpider, self).__init__(*args, **kwargs)
        self.problem_id = problem_id
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
        return item

class SdutSubmitSpider(CrawlSpider):
    name = 'sdut_submit'
    allowed_domains = ['acm.sdut.edu.cn']
    login_url = 'http://acm.sdut.edu.cn/sdutoj/login.php?action=login'
    submit_url = 'http://acm.sdut.edu.cn/sdutoj/submit.php?action=submit'
    source = \
        'I2luY2x1ZGUgPHN0ZGlvLmg+CgppbnQgbWFpbigpCnsKICAgIGludCBhLGI7CiAgICBzY2FuZigiJWQgJWQiLCZhLCAmYik7CiAgICBwcmludGYoIiVkXG4iLGErYik7CiAgICByZXR1cm4gMDsKfQ=='

    start_urls = [
        "http://acm.sdut.edu.cn/status.php"
    ]

    rules = [
        Rule(link(allow=('/status\?top=[0-9]+'), deny=('status\?bottom=[0-9]+')), follow=True, callback='parse_start_url')
    ]

    username = 'sdutacm1'
    password = 'sdutacm'

    def __init__(self, 
            problem_id='1000', 
            language='g++', 
            source=None, *args, **kwargs):
        super(SdutSubmitSpider, self).__init__(*args, **kwargs)
        self.problem_id = problem_id
        self.language = language
        if source is not None:
            self.source = source

    def start_requests(self):
        return [FormRequest(self.login_url,
                formdata = {
                        'username': username,
                        'password': password,
                        'submit': '++%E7%99%BB+%E5%BD%95++'
                },
                callback = self.after_login,
                dont_filter = True
        )]

    def after_login(self, response):
        return [FormRequest(self.submit_url,
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
