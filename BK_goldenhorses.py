import scrapy
import re
from golden_horses_booking.items import GoldenHorsesBookingItem
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor as LinkExtractor
from datetime import datetime
from bs4 import BeautifulSoup
import time
import urlparse

class GoldenHorsesReview_Booking(CrawlSpider):
    #spider name
    name = "goldenhorses_review_booking"
    allowed_domains = ["www.booking.com"]
    start_urls = ["http://www.booking.com/hotel/my/palace-of-the-golden-horses.en-gb.html"]
	
    def parse_url(self, response):
        reviewerNames =  response.selector.xpath("//div[@class='review_item_reviewer']/div/h4/text()").extract()
        reviewerCountries = response.selector.xpath("//span[contains(@class,'reviewer_country')]/text()[2]").extract()
        reviewScores =  response.selector.xpath("//div[contains(@class,'review_item_review_score')]/text()").extract()
        reviewTitles = response.selector.xpath("//div[@class='review_item_header_content_container']/div[contains(@class,'review_item_header_content')]/text()").extract()
        reviewDates = response.selector.xpath("//p[@class='review_item_date']/text()").extract()
		
        comments_raw = response.selector.xpath("//div[@class='review_item_review_content']").extract()
        comments = []
        for c in comments_raw:
             n = BeautifulSoup(c).find('p',{'class':'review_neg'})
             p = BeautifulSoup(c).find('p',{'class':'review_pos'})
             cdict = {}
             if n:
                 cdict['negative']=n.text
             if p:
                 cdict['positive']=p.text
             comments.append(cdict)
        
        #input date ************* YAYS!
        input_date = "2016-04-05"
		
        for i in range(0,len(reviewScores)):
            
             rev_date = reviewDates[i].strip()
             rev_date = datetime.strptime(rev_date, '%d %B %Y')
             rev_date = datetime.date(rev_date)
			
             if str(rev_date) >= input_date:
				hotel_review = GoldenHorsesBookingItem()
				hotel_review['name'] = self.name
				hotel_review['streetaddr'] = self.streetaddr
				hotel_review['city'] = self.city
				hotel_review['postcode'] = self.postcode
				hotel_review['country'] = self.country
				hotel_review['scrapday'] = self.scrapday
				hotel_review['score'] =  reviewScores[i].strip()
				
				try:
					rev_dates = reviewDates[i].strip()
					rev_dates = datetime.strptime(rev_dates, '%d %B %Y')
					rev_dates = datetime.date(rev_dates)
					hotel_review['post_date'] = rev_dates
				except:
					hotel_review['post_date'] =  reviewDates[i].strip()

				hotel_review['review_title'] = reviewTitles[i].strip()     
				hotel_review['reviewer_name'] = reviewerNames[i].strip()     
				hotel_review['reviewer_origin'] =  reviewerCountries[i].strip()    
				
				try:
					#print "did i try here? *****************************YES!" 
					#print "========================"
					if 'positive' in comments[i]:
						hotel_review['comment_positive'] = comments[i]['positive'].encode('ascii','ignore').replace("\n"," ")
						hotel_review['review_comments'] = hotel_review['comment_positive']
					if 'negative' in comments[i]:
						hotel_review['comment_negative'] = comments[i]['negative'].encode('ascii','ignore').replace("\n"," ")
						print hotel_review['review_comments']
						print "=============================="
						if hotel_review['review_comments']:
							hotel_review['review_comments'] += " " + hotel_review['comment_negative']
						else:
							hotel_review['review_comments'] = hotel_review['comment_negative']
				except Exception,e:
					print str(e)

				yield hotel_review
				
             else:
				break
				
			
        next_links = response.selector.xpath("//a[@id='review_next_page_link']/@href").extract()
        if len(next_links) > 0:
             yield scrapy.Request(urlparse.urljoin(response.url, next_links[0]), callback=self.parse_url)
		
	
    def parse_start_url(self, response):

        self.name = "Palace of the Golden Horses"
        alladdr = response.selector.xpath("//span[@itemprop='address']/text()").extract()[0].strip().replace("\n","").split(",")
        citypost = alladdr[len(alladdr)-2].split(" ")
        self.streetaddr = ",".join(str(e).strip() for e in alladdr[0:(len(alladdr)-2)])
        self.city = " ".join(str(e).strip() for e in citypost[2:(len(alladdr))]) 
        self.postcode = citypost[1].strip()
        self.country = "Malaysia"
        self.scrapday = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        yield scrapy.Request("http://www.booking.com/reviewlist.en-gb.html?pagename=palace-of-the-golden-horses;cc1=my;rows=100", callback=self.parse_url)
