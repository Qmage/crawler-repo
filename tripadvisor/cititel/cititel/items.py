# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field

class CititelItem(scrapy.Item):
    name = Field()
    streetaddr = Field()
    city = Field()
    postcode = Field()
    country = Field()
    scrapday = Field()
    score = Field()
    post_date = Field()
    review_title = Field()
    reviewer_origin = Field()
    review_comments = Field()
    reviewer = Field()
    pass
