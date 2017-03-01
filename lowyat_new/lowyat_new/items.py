# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ThreadComment_Item(scrapy.Item):

    topic_id =scrapy.Field()
    topic_url = scrapy.Field()
    topic_title = scrapy.Field()
    topic_description = scrapy.Field()
    topic_replies = scrapy.Field()
    topic_views = scrapy.Field()
    topic_starter = scrapy.Field()
    topic_lastaction = scrapy.Field()
    topic_starttime = scrapy.Field()
    comment_id = scrapy.Field()
    comment = scrapy.Field()
    comment_user = scrapy.Field()
    comment_time = scrapy.Field()
