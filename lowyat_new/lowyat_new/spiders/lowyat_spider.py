# Embedded file name: C:\Users\clement.chin\Desktop\lowyat\lowyat\spiders\lowyat_spider.py
import scrapy
import json
from scrapy.spiders import CrawlSpider
from lowyat_new.items import ThreadComment_Item
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import time
from datetime import date, timedelta
import dateutil.parser as parser
import re
import csv
import os.path

class Lowyat_Spider(CrawlSpider):
    name = 'Lowyat'
    allowed_domains = ['forum.lowyat.net']

    def __init__(self, selected_forum=None):
        super().__init__()
        if selected_forum is None:
            raise ValueError('"-a selected_forum=" argument missing')
        forums_to_crawl = selected_forum.split(",")
        if len(forums_to_crawl) == 0:
            raise ValueError('no forums selected')
        else:
            self.start_urls = [urljoin('https://forum.lowyat.net/', x) for x in forums_to_crawl]
        
    def yieldItem(self, thread, postid, clean_comment, clean_datetime, clean_username):
        for i in range(0, len(clean_comment)):
            item = ThreadComment_Item()
            item['topic_id'] = thread['topic_id']
            item['topic_url'] = thread['topic_url']
            item['topic_title'] = thread['topic_title']
            item['topic_description'] = thread['topic_description']
            item['topic_replies'] = thread['topic_replies']
            item['topic_views'] = thread['topic_views']
            item['topic_starter'] = thread['topic_starter']
            item['topic_lastaction'] = thread['topic_lastaction']
            item['topic_starttime'] = thread['topic_starttime']
            item['comment'] = clean_comment[i]
            item['comment_user'] = clean_username[i]
            item['comment_time'] = clean_datetime[i]
            item['comment_id'] = postid[i]
            yield item


    def get_isodatetime(self, raw_date):
        date_time = BeautifulSoup(raw_date).text.split(', ')
        date_var = date_time[0].strip()
        if date_var == 'Today':
            date_var = time.strftime('%Y-%m-%d')
        elif date_var == 'Yesterday':
            date_var = (date.today() - timedelta(1)).strftime('%Y-%m-%d')
        time_var = date_time[1]
        return parser.parse(date_var + ' ' + time_var).isoformat()

    def parse_start_url(self, response):
        return self.parse_thread_list(response)

    def parse_thread_list(self, response):
        sub_forum = response.xpath("//td[@class='row2']/b/a/@href").extract()
        if len(sub_forum) > 0:
            for s in sub_forum:
                request3 = scrapy.Request(urljoin(response.url, s), callback=self.parse_thread_list)
                yield request3

        thread = {}
        
        raw_url = response.xpath("//td[@class='row1']/div/div[1]/a[1]/@href").extract()
        thread['topic_id'] = [r.rsplit('/', 1)[1] for r in raw_url]
        thread['topic_url'] = [urljoin(response.url, r) for r in raw_url]

        raw_title = response.xpath("//td[@class='row1']/div/div[1]/a[1]/text()").extract()
        thread['topic_title'] = [r.strip() for r in raw_title]

        raw_descriptions = response.xpath("//td[@class='row1']/div/div[@class='desc']").extract()
        thread['topic_description'] = [BeautifulSoup(r).text for r in raw_descriptions]

        resp = response.xpath("//div[@id='forum_topic_list']//td[@class='row2']").extract()
        thread['topic_replies'] = [BeautifulSoup(r).text.strip().replace(',', '') for r in resp[0::4]]
        thread['topic_starter'] = [BeautifulSoup(r).text for r in resp[1::4]]
        thread['topic_views'] = [BeautifulSoup(r).text.replace(',', '') for r in resp[2::4]]

        thread['topic_lastaction'] = []
        for r in resp[3::4]:
            date_time = re.split('\\s-\\s|,\\s', BeautifulSoup(r).text.strip().split('\n')[0])
            date_var = date_time[0].strip()
            if date_var == 'Today':
                date_var = time.strftime('%Y-%m-%d')
            elif date_var == 'Yesterday':
                date_var = (date.today() - timedelta(1)).strftime('%Y-%m-%d')
            time_var = date_time[1]
            clean_datetime = parser.parse(date_var + ' ' + time_var).isoformat()
            thread['topic_lastaction'].append(clean_datetime)

        thread_list = map(dict, zip(*[ [ (k, v) for v in value ] for k, value in thread.items() ]))
        for t in thread_list:
            request = scrapy.Request(t['topic_url'], callback=self.parse_firstpage)
            request.meta['thread'] = t
            yield request

        next_page = response.xpath('(//a[@title="Next page"])[1]/@href').extract()
        if len(next_page) > 0:
            request2 = scrapy.Request(urljoin(response.url, next_page[0]), callback=self.parse_thread_list)
            return request2

    def parse_firstpage(self, response):
        thread = response.meta['thread']
        
        postdetails = response.xpath("//span[@class='postdetails']").extract()
        
        thread['topic_starttime'] = self.get_isodatetime(postdetails[0])
        
        clean_datetime = [self.get_isodatetime(r) for r in postdetails[::3]]

        
        normalname = response.xpath("//span[@class='normalname']/a").extract()
        clean_username = [BeautifulSoup(user).text for user in normalname]

        clean_comment = []
        postid = []
        for sel in response.xpath("//div[@class='postcolor post_text']"):
            filtered_comment = []
            comment_lines = sel.xpath('text()').extract()
            for comment in comment_lines:
                if comment and not comment.isspace():
                    filtered_comment.append(comment.strip())

            clean_comment.append(' '.join(filtered_comment))
            if isinstance(sel.xpath('@data-postid').extract()[0], str):
                postid.append(sel.xpath('@data-postid').extract()[0])
            else:
                postid.append(sel.xpath('@data-postid').extract()[0][0])

        return self.yieldItem(thread, postid, clean_comment, clean_datetime, clean_username)
        
        next_page = response.xpath('(//a[@title="Next page"])[1]/@href').extract()
        if len(next_page) > 0:
            request = scrapy.Request(urljoin(response.url, next_page[0]), callback=self.parse_otherpage)
            request.meta['thread'] = thread
            return request

    def parse_otherpage(self, response):
        thread = response.meta['thread']
        
        postdetails = response.xpath("//span[@class='postdetails']").extract()
        
        clean_datetime = [self.get_isodatetime(r) for r in postdetails[::3]]

        normalname = response.xpath("//span[@class='normalname']/a").extract()
        
        clean_username = [BeautifulSoup(user).text for user in normalname]

        clean_comment = []
        postid = []
        for sel in response.xpath("//div[@class='postcolor post_text']"):
            filtered_comment = []
            comment_lines = sel.xpath('text()').extract()
            for comment in comment_lines:
                if comment and not comment.isspace():
                    filtered_comment.append(comment.strip())

            clean_comment.append(' '.join(filtered_comment))
            postid.append(sel.xpath('@data-postid').extract())

        return self.yieldItem(thread, postid, clean_comment, clean_datetime, clean_username)
        
        next_page = response.xpath('(//a[@title="Next page"])[1]/@href').extract()
        if len(next_page) > 0:
            request = scrapy.Request(urljoin(response.url, next_page[0]), callback=self.parse_otherpage)
            request.meta['thread'] = thread
            return request