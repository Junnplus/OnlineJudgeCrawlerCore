import random
from OJCC.settings import USER_AGENT_LIST
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware

class RandomUserAgentMiddleware(UserAgentMiddleware):

    user_agent_list = USER_AGENT_LIST

    def __init__(self, user_agent=''):
        self.user_agent = user_agent

    def _user_agent(self, spider):
        if hasattr(spider, 'user_agent'):
            return spider.user_agent

        return random.choice(self.user_agent_list)

    def process_request(self, request, spider):
        ua = self._user_agent(spider)
        if ua:
            request.headers.setdefault('User-Agent', ua)
