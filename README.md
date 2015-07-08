# OnlineJudge Crawler Core


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

### Problem Crawl
#### Command
```shell
scrapy crawl `origin_oj`_problrm -a problem_id=''
```
+ argument
    - problem_id

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

各大OJ支持语言

language | origin_oj
-------- | ---------
gcc      | `POJ`, `HDU_OJ`, `SDUT_OJ`, `FZU_OJ`
g++      | `POJ`, `HDU_OJ`, `SDUT_OJ`, `FZU_OJ`
java     | `POJ`, `HDU_OJ`, `SDUT_OJ`, `FZU_OJ`
pascal   | `POJ`, `HDU_OJ`, `SDUT_OJ`, `FZU_OJ`
c        | `POJ`, `HDU_OJ`, `FZU_OJ`
c++      | `POJ`, `HDU_OJ`, `FZU_OJ`
fortran  | `POJ`
c#       | `HDU_OJ`


#### Command
```shell
scrapy crawl `origin_oj`_submit -a problem_id='' -a language='' -a source=''
```
+ argument
    - problem_id
    - language
    - source `base64 编码`

#### Script
```python
# ...
def code_submit(origin_oj, problem_id, language, source):
    configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})
    process = CrawlerProcess(settings)
    process.crawl(origin_oj + '_submit', problem_id=problem_id, language=language, source=source)
    process.start()
```


## Support

- [POJ](http://poj.org)
- [HDU_OJ](http://acm.hdu.edu.cn)
- [SDUT_OJ](http://acm.sdut.edu.cn)
- [FZU_OJ](http://acm.fzu.edu.cn)
