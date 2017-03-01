import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy_bookingdotcom.items import ScrapyBookingdotcomItem
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from selenium.common.exceptions import NoSuchElementException 

chromeOptions = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images":2}
chromeOptions.add_experimental_option("prefs",prefs)
browser = webdriver.Chrome(chrome_options=chromeOptions)



def check_exists_by_xpath(xpath):
        try:
            browser.find_element_by_xpath(xpath)
        except NoSuchElementException:
            return False
        return True
    
def browser_doa(urlnow):
        try:
            browser.get(urlnow)
        except:
            return False
        
        return True

def chromeCrashes(urlnow):
    chromeOptions = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images":2}
    chromeOptions.add_experimental_option("prefs",prefs)
    browser = webdriver.Chrome(chrome_options=chromeOptions)
    browser.get(urlnow)
        

class Expedia_Spider(scrapy.Spider):
      
    name = "bookingdotcom"
    allowed_domains = ["http://www.booking.com/"]
     
    def start_requests(self):  
        
#         chromeOptions = webdriver.ChromeOptions()
#         prefs = {"profile.managed_default_content_settings.images":2}
#         chromeOptions.add_experimental_option("prefs",prefs)
#         browser = webdriver.Chrome(chrome_options=chromeOptions)

        browser.get("http://www.booking.com/searchresults.html?sid=b80dccb347dfcbcb039132faacbd3963;dcid=1;checkin_monthday=23;checkin_year_month=2015-9;checkout_monthday=24;checkout_year_month=2015-9;city=-2403010;class_interval=1;group_adults=2;no_rooms=1;room1=A%2CA;sb_price_type=total;&;selected_currency=USD")
        
        try:
            browser.find_element_by_css_selector("#growl_squash > div > div > div").click()
        except:
            pass
        
        try:
            browser.find_element_by_css_selector("#inspire_filter_block > span").click()
        except:
            pass ##
        
        try:
            browser.find_element_by_css_selector("b2searchresultsPage > div.modal-wrapper.notification-lightbox-container > div.modal-mask-closeBtn").click() 
        except:
            pass
        
        pattern1 = False
        
        try:
            WebDriverWait(browser, 10).until( EC.presence_of_element_located((By.CLASS_NAME, "hotellist")) )
        except:
            print "error waiting for first page load" 
            pattern1 = True
         
        if pattern1:
            elements = browser.find_elements_by_xpath("//div[@id='hotellist_inner']//div[@class='sr_property_block_main_row']/div[@class='sr_item_main_block']/h3")
        else:
            elements = browser.find_elements_by_xpath("//a[@class='hotel_name_link url']")
            
        all_urls = []
        for e in elements:
            url = e.get_attribute("href")
            all_urls.append(url)
        print "hotel urls retreived so far - " + str(len(all_urls))

#        //div[@id='hotellist_inner']//div[@class='sr_property_block_main_row']/div[@class='sr_item_main_block']/h3

#         try:
#             while (check_exists_by_xpath("//div[@class='results-paging']/a[contains(text(),'Next page')]")):
#                 next_page = browser.find_element_by_xpath("//div[@class='results-paging']/a[contains(text(),'Next page')]").click()
#                 time.sleep(5)
#                 WebDriverWait(browser, 30).until( EC.invisibility_of_element_located((By.CLASS_NAME, "js-ups-tick-loading--signin")))
#                 elements = browser.find_elements_by_xpath("//a[@class='hotel_name_link url']")
#                 for e in elements:
#                     url = e.get_attribute("href")
#                     all_urls.append(url)
#                 WebDriverWait(browser, 20)
#                 print "hotel urls retrieved so far - " + str(len(all_urls))
#         except:
#             pass
#         
#         time.sleep(1)
        
        
        print "FINAL - total hotel urls retrieved - " + str(len(all_urls))
        myurl = sorted(all_urls)

        f = open("hotellistbooking_23Sept.csv","w")
        for u in myurl:
            print u
            f.write(u+"\n") 
        f.close()
        
        i = 1
        t = len(myurl)
        for u in myurl: # do something 
            print "%d over %d" % (i,t)
            i = i + 1
            yield scrapy.Request(u, callback=self.parse_hotel_page,meta = {'dont_redirect': True,'handle_httpstatus_list': [301]})
                 
     
   
    def parse_hotel_page(self, response):
        
        if browser_doa(response.url)==False:
            print "crash liao"
            print response.url
            chromeCrashes(response.url)
        
        try:
            WebDriverWait(browser, 60).until( EC.presence_of_element_located((By.ID, "hp_hotel_name")) )
        except:
            print "error waiting for load 2: hotel not found"
       
        addrstr1 = map(str.strip,str(browser.find_element_by_xpath("//span[@id='hp_address_subtitle']").text).strip().split(','))
        addrstr2 = addrstr1[len(addrstr1)-2].split(' ') #1 postcode
        hotel_info = ScrapyBookingdotcomItem()
        hotel_info['name'] = str(browser.find_element_by_xpath("//span[@id='hp_hotel_name']").text).strip()
        hotel_info['streetaddr'] = " ".join(addrstr1[0:len(addrstr1)-2])
        hotel_info['city'] = " ".join(addrstr2[1::])
        hotel_info['postcode'] = addrstr2[0]
        hotel_info['country'] = addrstr1[len(addrstr1)-1]
        hotel_info['amenities'] = browser.find_element_by_xpath("(//span[@class='highlighted_facilities_reinforcement'])[1]").text
        hotel_info['scrapday'] = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        
        prices = []
        
        today = date.today()  #2015-09-22
        lastUrl1 = today.strftime("%Y-%m-%d")
        
        
        for i in range(1,8):
            itemday = "price_day%d" % i
            
            
            try:
                browser.find_element_by_css_selector("#b2hotelPage > div.modal-wrapper.notification-lightbox-container > div.modal-mask-closeBtn").click() 
            except:
                pass
            
            try:
                WebDriverWait(browser, 5).until( EC.presence_of_element_located((By.ID,"room_availability_container")) )
            except:
                print "error waiting for load 2: hotel not found"
       
            cprice = "NA"
            
            try: #get price
                gibberish = (str(browser.find_element_by_xpath('//*[@id="room_availability_container"]/tr[3]/td[2]').text).strip().replace('\n',' ')).replace('US$','')
                gibberish = gibberish.split(" ")
                cprice = min(gibberish)
            except: pass
            
                
            hotel_info[itemday] = cprice
            if cprice == "NA":
                prices.append(float(0))
            else:
                prices.append(float(cprice)) 
                
            today = today + timedelta(days=1) #23
            tomorrow = today + timedelta(days=1) #24
            todayUrl1 = today.strftime("%Y-%m-%d")

            tomorrowUrl1 = tomorrow.strftime("%Y-%m-%d")
            
            theUrl = str(browser.current_url)
            if i == 1:
                theUrl = str(response.url)
            nextUrl = theUrl.replace(todayUrl1, tomorrowUrl1)
            nextUrl = nextUrl.replace(lastUrl1, todayUrl1)
 
            lastUrl1 = todayUrl1
#             if "&multiCurrencyCode=USD" not in nextUrl:
#                 nextUrl = nextUrl + "&multiCurrencyCode=USD"
            
#             print nextUrl
            time.sleep(2)
    
            try: 
                browser.get(nextUrl)
            except:
                browser.refresh()
                time.sleep(2)

        if 0 in prices:
            averagePrice = "NA"
        else:
            averagePrice = sum(prices)/len(prices)
        
        hotel_info['price_avg'] = averagePrice
        print hotel_info
        return hotel_info
    
    
