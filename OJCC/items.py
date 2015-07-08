# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class ProblemItem(scrapy.Item):

    origin_oj = scrapy.Field()
    problem_id = scrapy.Field()
    problem_url = scrapy.Field()
    title = scrapy.Field()
    time_limit = scrapy.Field()
    memory_limit = scrapy.Field()
    description = scrapy.Field()
    input = scrapy.Field()
    output = scrapy.Field()
    sample_input = scrapy.Field()
    sample_output = scrapy.Field()
    hint = scrapy.Field()
    source = scrapy.Field()

class SolutionItem(scrapy.Item):

    origin_oj = scrapy.Field()
    problem_id = scrapy.Field()
    run_id = scrapy.Field()
    source = scrapy.Field()
    result = scrapy.Field()
    memory = scrapy.Field()
    time = scrapy.Field()
    language = scrapy.Field()
    code_length = scrapy.Field()
    submit_time = scrapy.Field()
