import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from iproperty.items import IpropertyItem
import time
import re

class IpropertySpider(CrawlSpider):
    states=['KL',
     'JO',
     'KE',
     'KT',
     'MA',
     'NS',
     'OT',
     'PA',
     'PE',
     'PK',
     'PL',
     'PJ',
     'SA',
     'SW',
     'SE',
     'TR']

    name = "iproperty"
    allowed_domains = ["www.iproperty.com.my"]
    # query = 'kuala lumpur'
    #"http://www.iproperty.com.my/property/searchresult.aspx?t=S&gpt=AR&k=%s" % query.replace(' ','+')
    start_urls = ["http://www.iproperty.com.my/property/searchresult.aspx?t=S&gpt=AR&st={}".format(x) for x in states]

    rules = (
        ###navigate to next page
        Rule(LinkExtractor(allow=('/property/searchresult.aspx'), restrict_xpaths=("//div[@class='pagination-silver']/div[@class='pagination light-theme simple-pagination']/ul//li[@class='active']/a[contains(text(),'Next')]"))),
        ###parse the page
        Rule(LinkExtractor(allow=('/propertylisting/')), callback='parse_item')

    )

    def parse_item(self, response):
        print ("--------------------------------------------------------------------------")
        self.log('Hi, this is an item page! %s' % response.url)
        item = IpropertyItem()
        #item['id'] = response.xpath('//td[@id="item_id"]/text()').re(r'ID: (\d+)')
        #extracted_name = response.xpath("//h1[@class='main-title']/text()").extract()[0]
        #item['name'] = extracted_name.split(', ')[0]
        
        carpark = response.xpath("//li[@class='ld_mis_detail']//p[@class='room']/span[@class='no-nonbedroom' and contains(@title, 'Car parks')]/text()").extract()
        if carpark:
            item['CarParks'] = carpark[0].encode('ascii','ignore')
        
        facilities_raw = response.xpath("//div[@class='detail-info-wide-container-wrap']/div[@class='container']/div[@class='details-info-container']/ul[@class='infos']/li/text()").extract()
        item['Facilities'] = ','.join([f.strip() for f in facilities_raw]).encode('ascii','ignore')
        
        prop_features_raw = response.xpath("//div[@class='main']/section[@class='details-info']/div[@class='container']/div[@class='details-info-container']/ul[@class='infos']/li/text()").extract()
        features = {}
        for f in prop_features_raw:
            k,v = f.split(' : ')
            features[k.replace(':','').strip()] = v.strip()
        
        for k,v in features.items():
            key = k.replace(' ','').replace('-','')
            """
            if key not in item.fields:
                with open('missing_scrapy_field.csv', "a") as myfile:
                    myfile.write("Features - {}\n".format(key))"""
            try:
                item[key] = v.encode('ascii','ignore')
            except:
                pass
        
        otherInfo_raw = response.xpath("//script[contains(text(), 'var gvObjProp')]/text()").extract()[0]
        otherInfo_list = [f.strip() for f in re.search(r'var gvObjProp = {(.*)};',otherInfo_raw,re.S).group(0).splitlines()][1:-1]

        for i in otherInfo_list:
            k,v = i.split(': ')
            key = k.strip()
            """
            if key not in item.fields:
                with open('missing_scrapy_field.csv', "a") as myfile:
                    myfile.write("otherInfo - {}\n".format(key))"""
            try:
                item[key] = v.replace('"','')[:-1].strip().encode('ascii','ignore')
            except:
                pass

        
        #item['agent_name'] = response.xpath("//div[@class='box-280w-orange']/div[2]/span[@class='title_text']/a/text()").extract()[0]
        #item['agent_contact'] = response.xpath("//input[@id='agentPhone']/@value").extract()[0]
        #item['area'] = extracted_name.split(',')[len(extracted_name-1)]
        #item['image'] = response.xpath("//a[@class='group1 cboxElement']/img/@src").extract()[0]

        return item