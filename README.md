# OnlineJudge Crawler Core

## Features

- Random UserAgent Support
- Simulate Login Support
- Form Submit Support

## Install

- sudo pip install virtualenvwrapper
- add the following lines to your ~/.bashrc:

```
export WORKON_HOME=~/.virtualenvs
source /usr/bin/virtualenvwrapper.sh
```
- source ~/.bashrc
- git clone https://github.com/Junnplus/OnlineJudge_Crawler_Core.git && cd OnlineJudge_Crawler_Core
- mkvirtualenv OJCC
- pip install -r requirements.txt

## Usage

### Problem Init

> 抓取Origin_OJ现有的所有题目

#### Command
```shell
scrapy crawl `origin_oj`_init
```

Example:
```shell
scrapy crawl poj_init
```

### Problem Crawl
#### Command
```shell
scrapy crawl `origin_oj`_problrm -a problem_id=''
```
+ argument
    - problem_id

Example:
```shell
scrapy crawl poj_problrm -a problem_id='1000'
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
    process.crawl(origin_oj + '_problem', problem_id=problem_id)
    process.start()
```

### Code Submit

> 提交的代码需要通过 [base64 编码](http://tool.chinaz.com/Tools/Base64.aspx)

#### Command
```shell
scrapy crawl `origin_oj`_submit -a problem_id='' -a language='' -a source='' -a username='' -a password=''
```
+ argument
    - problem_id 
    - language `default: g++`
    - source `base64 编码`

各大OJ语言支持

origin_oj | language
--------- | ---------
POJ       | `gcc`, `g++`, `java`, `pascal`, `c`, `c++`, `fortran`
HDU_OJ    | `gcc`, `g++`, `java`, `pascal`, `c`, `c++`, `c#`
SDUT_OJ   | `gcc`, `g++`, `java`, `pascal`, `go`, `lua`, `dao`, `perl`, `ruby`, `haskell`, `python2`, `python3`
FZU_OJ    | `gcc`, `g++`, `java`, `pascal`, `c`, `c++`

Example:
```shell
scrapy crawl sdut_submit -a problem_id='1000' -a language='gcc' -a source='I2luY2x1ZGUgPHN0ZGlvLmg+CgppbnQgbWFpbigpCnsKICAgIGludCBhLGI7CiAgICBzY2FuZigiJWQgJWQiLCZhLCAmYik7CiAgICBwcmludGYoIiVkXG4iLGErYik7CiAgICByZXR1cm4gMDsKfQ==' -a username='sdutacm1' -a password='sdutacm'
```

#### Script
```python
# ...
def code_submit(origin_oj, problem_id, language, source, username, password):
    configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})
    process = CrawlerProcess(settings)
    process.crawl(origin_oj + '_submit', problem_id=problem_id, language=language, source=source, username=username, password=password)
    process.start()
```


## Support

- [POJ](http://poj.org)
- [HDU_OJ](http://acm.hdu.edu.cn)
- [SDUT_OJ](http://acm.sdut.edu.cn)
- [FZU_OJ](http://acm.fzu.edu.cn)
