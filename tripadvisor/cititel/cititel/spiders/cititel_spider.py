import scrapy
import re
import os

from __main__ import *
from datetime import datetime
from bs4 import BeautifulSoup
from cititel.items import CititelItem
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor as LinkExtractor
from datetime import datetime
import urllib.parse


class CititelReviewSpider(CrawlSpider):
    name = "cititel_review"
    allowed_domains = ["www.tripadvisor.com.my"]

    start_urls = ["https://www.tripadvisor.com.my/Hotel_Review-g298570-d305316-Reviews-Cititel_Mid_Valley-Kuala_Lumpur_Wilayah_Persekutuan.html"]
	
    rules = (
			Rule(LinkExtractor(allow=(), restrict_xpaths =["//body[@class=' sur_layout_redesign  fall_2013_refresh_hr_top  ltr domn_en_MY lang_en globalNav2011_reset css_commerce_buttons flat_buttons sitewide xo_pin_user_review_to_top track_back']/div[@id='PAGE']/div[@id='MAINWRAP']/div[@id='MAIN']/div[@id='BODYCON']/div[@id='SHOW_USER_REVIEW']/div[@class='col balance']/div[@id='REVIEWS']/div[@class='deckTools btm']/div[@class='unified pagination ']/a[@class='nav next rndBtn ui_button primary taLnk']"]),
                 callback="parse_start_url2",follow=True),
            )
	
    def parse_start_url2(self, response):
        name = response.selector.xpath('//*[@id="WAR_CURRENT_POI"]/div/div[1]/div/img/@alt').extract()
        streetaddr = response.selector.xpath("(//span[@class='street-address'])[1]/text()").extract()
        city = response.selector.xpath("//span[@class='locality']/span[1]/text()").extract()
        postcode = response.selector.xpath("//span[@class='locality']/span[2]/text()").extract()
        country = response.selector.xpath("(//span[@class='country-name'])[1]/text()").extract()
        scrapday = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
            
        #loop
        reviewScores =  response.selector.xpath("//div[@class='rating reviewItemInline']/span[@class='rate sprite-rating_s rating_s']/img/@alt").extract()
        reviewDates1 =  response.selector.xpath("//span[@class='ratingDate relativeDate']/@title").extract()
        reviewDates2 =  response.selector.xpath("//span[@class='ratingDate']/text()").extract()
        reviewDates  =  reviewDates1 + reviewDates2
        reviewTitle =  response.selector.xpath("(//div[@class='innerBubble']/div[@class='quote'])").extract() # 5 item
        #print(reviewTitle[0].extract())
        #print(reviewTitle[9].extract())
        #raise
        reviewComments = response.selector.xpath("(//div[@class='entry']/p)").extract() # 7 items
        reviewers = response.selector.xpath("//div[contains(@id,'review')]//div[@class='username mo']/span/text()").extract() 

        for i in range(0,len(reviewDates)):
        	hotel_review = CititelItem()
        	hotel_review['name'] = name
        	hotel_review['streetaddr'] = streetaddr
        	hotel_review['city'] = city
        	hotel_review['postcode'] = postcode
        	hotel_review['country'] = country
        	hotel_review['scrapday'] = scrapday

        	hotel_review['score'] =  ''.join(BeautifulSoup(str(reviewScores[i][0])).findAll(text=True))

        	try:
        		rev_dates = ''.join(BeautifulSoup(str(reviewDates[i])).findAll(text=True)).strip()				
        		stripword = "Reviewed "
        		if stripword in rev_dates:
        			rev_dates = str(rev_dates.strip(stripword))
        			rev_dates = datetime.strptime(rev_dates, "%d %B %Y")
        			rev_dates = datetime.date(rev_dates)
        			hotel_review['post_date'] = rev_dates
        		else:
        			rev_dates = datetime.strptime(rev_dates, "%d %B %Y")
        			rev_dates = datetime.date(rev_dates)
        			hotel_review['post_date'] = rev_dates
        	except:
        		hotel_review['post_date'] = ""

        	hotel_review['review_title'] = ''.join(BeautifulSoup(str(reviewTitle[i].encode('ascii', 'ignore').decode('ascii'))).findAll(text=True)).strip()  # re.sub(r'<[^>]*?>', ' ', str(reviewTitle[0].extract().encode("utf-8")))     
        	try:
        		hotel_review['reviewer_origin'] =  ''.join(BeautifulSoup(str((response.selector.xpath("(//div[@class='member_info'])[%d]/div[@class='location']" % (i+1))).extract()[0].encode('ascii', 'ignore').decode('ascii'))).findAll(text=True)).strip()
        	except Exception as e:
        		hotel_review['reviewer_origin'] = ""
        		#print(str(e))
        		pass
        	hotel_review['review_comments'] =   ''.join(BeautifulSoup(str(reviewComments[i].encode('ascii', 'ignore').decode('ascii'))).findAll(text=True)).strip() # re.sub(r'<[^>]*?>', ' ', str(reviewComments[0].extract().encode("utf-8")))   
        	try:
        		hotel_review['reviewer'] =  reviewers[i].strip()
        	except Exception as e:
        		hotel_review['reviewer'] = ""
        		#print(str(e))
        		pass

        	yield hotel_review

        next_link = response.selector.xpath("//a[@class='nav next rndBtn ui_button primary taLnk']/@href").extract()
        #print(urlparse.urljoin(response.url, next_link[0]) + "==============================!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        if len(next_link) > 0:
        	yield scrapy.Request(urllib.parse.urljoin(response.url, next_link[0]), callback = self.parse_start_url2)

    def parse_start_url(self, response):
        first_user =  response.selector.xpath("//div[@class='innerBubble']//div[contains(@class,'quote')]//@href").extract()[0]
		#first_user = ''.join(BeautifulSoup(str(review_title[i].encode('ascii', 'ignore').decode('ascii'))).findAll(text=True)).strip() 
        first_link = urllib.parse.urljoin(response.url, first_user)
        yield scrapy.Request(first_link, callback = self.parse_start_url2)