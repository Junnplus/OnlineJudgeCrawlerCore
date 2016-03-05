# OnlineJudge Crawler Core

## Features

- Random UserAgent Support
- Simulate Login Support
- Form Submit Support

## Install

- git clone https://github.com/Junnplus/OnlineJudge_Crawler_Core.git && cd OnlineJudge_Crawler_Core
- pip install -r requirements.txt

## Usage

### Origin_OJ Init Spider

> 抓取 Origin_OJ 现有的所有题目

#### Command
```shell
scrapy crawl `origin_oj`_init_spider
```

Example:
```shell
scrapy crawl poj_init_spider
```

### Problem Crawl Spider

> 抓取 Origin_OJ 指定题目

#### Command
```shell
scrapy crawl `origin_oj`_problrm_spider -a problem_id=''
```
+ argument
    - problem_id

Example:
```shell
scrapy crawl poj_problrm_spider -a problem_id='1000'
```

#### Script
```python
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging

setting = get_project_settings()

def problem_crawl(origin_oj, problem_id):
    configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})
    process = CrawlerProcess(settings)
    process.crawl(origin_oj + '_problem_spider', problem_id=problem_id)
    process.start()
```

### Code Submit Spider

> 提交的代码需要通过 [base64 编码](http://tool.chinaz.com/Tools/Base64.aspx)

#### Command
```shell
scrapy crawl `origin_oj`_submit_spider -a problem_id='' -a language='' -a source='' -a username='' -a password=''
```
+ argument
    - problem_id 
    - language `default: g++`
    - source `base64 编码`
    - username 
    - password

各大OJ语言支持

origin_oj | language
--------- | ---------
POJ       | `gcc`, `g++`, `java`, `pascal`, `c`, `c++`, `fortran`
HDU_OJ    | `gcc`, `g++`, `java`, `pascal`, `c`, `c++`, `c#`
SDUT_OJ   | `gcc`, `g++`, `java`, `pascal`, `go`, `lua`, `dao`, `perl`, `ruby`, `haskell`, `python2`, `python3`
FZU_OJ    | `gcc`, `g++`, `java`, `pascal`, `c`, `c++`

Example:
```shell
scrapy crawl sdut_submit_spider -a problem_id='1000' -a language='gcc' -a source='I2luY2x1ZGUgPHN0ZGlvLmg+CgppbnQgbWFpbigpCnsKICAgIGludCBhLGI7CiAgICBzY2FuZigiJWQgJWQiLCZhLCAmYik7CiAgICBwcmludGYoIiVkXG4iLGErYik7CiAgICByZXR1cm4gMDsKfQ==' -a username='sdutacm1' -a password='sdutacm'
```

#### Script
```python
# ...
def code_submit(origin_oj, problem_id, language, source, username, password):
    configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})
    process = CrawlerProcess(settings)
    process.crawl(origin_oj + '_submit_spider', problem_id=problem_id, language=language, source=source, username=username, password=password)
    process.start()
```

### Account Info Spider

> 抓取帐号信息

#### Command
```shell
scrapy crawl `origin_oj`_user_spider -a username='' -a password=''
```
+ argument
    - username 
    - password

Example:
```shell
scrapy crawl sdut_user_spider -a username='sdutacm1' -a password='sdutacm'
```

#### Script
```python
# ...
def account_info(origin_oj, username, password):
    configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})
    process = CrawlerProcess(settings)
    process.crawl(origin_oj + '_user_spider', username=username, password=password)
    process.start()
```

## Support

- [POJ](http://poj.org)
- [HDU_OJ](http://acm.hdu.edu.cn)
- [SDUT_OJ](http://acm.sdut.edu.cn)
- [FZU_OJ](http://acm.fzu.edu.cn)
