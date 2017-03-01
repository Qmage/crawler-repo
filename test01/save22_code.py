import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import math
import pprint
import re
import datetime
from datetime import datetime
import urllib
import simplejson
import json
import requests
import ntpath
import base64
import random

pp = pprint.PrettyPrinter(indent=4)

GEOCODE_BASE_URL = 'https://maps.googleapis.com/maps/api/geocode/json'

domain = "http://www.save22.com.my"

web = requests.get(domain + "/malaysia/").content

web = BeautifulSoup(web)

link = [x.select("a")[0]["href"] for x in web.select(".quick-categories")[0].find_all("li")] +\
[x.select("a")[0]["href"] for x in web.select(".quick-categories")[1].find_all("li")]

link = [x.replace("/widget/et_slug", "") for x in link 
        if x!= "javascript:void(0);"][1: ]

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def geocode(address, **geo_args):

	geo_args.update({
		'address': address,
		'language' : 'en',
		'region': 'my',
		'components': 'country:MY',
		'bounds': '3.0362,101.6151|3.2452,101.7582',
		'key': 'AIzaSyATojLAIh4vXbWbQ-fSrYuu9s10TOgkxYM'
	})
	#print address
	
	#print simplejson.dumps([s['formatted_address'] for s in result['results']], indent=2)
	
	loc = {}
	loc['locNm'] = address
	
	url = GEOCODE_BASE_URL + '?' + urllib.urlencode(geo_args)
	#print url
	result = simplejson.load(urllib.urlopen(url))
	#print result
	
	if result['results']:
		desired_result = result['results'][0]
		
		if desired_result['formatted_address'] != 'Malaysia':
			loc['vicinity'] = desired_result['formatted_address']
			if desired_result['geometry']['location']['lat']:
				loc['latitude'] = desired_result['geometry']['location']['lat']
			if desired_result['geometry']['location']['lng']:
				loc['longitude'] = desired_result['geometry']['location']['lng']
			if desired_result['address_components']:
				loc['types'] = desired_result['address_components'][0]['types']
				for item in desired_result['address_components']:
					if 'country' in item['types']:
						loc['country'] = item['long_name']
					elif 'postal_code' in item['types']:
						loc['postCode'] = item['long_name']
					elif 'administrative_area_level_1' in item['types']:
						loc['state'] = item['long_name']
					elif 'locality' in item['types']:
						loc['city'] = item['long_name']
				
	return loc
		
def get_detail(Soup):
	title = None
	start = None
	stop = None
	location = None
	encoded_image = None
	desc = None
	try:
		title = soup.select(".promo-title")[0].select("a")[0].text
	except:
		pass
	try:
		company = soup.select(".store-link")[0].select("a")[0].text
	except:
		pass
	try:
		category =  soup.select(".establishment_type-link")[0].select("a")[0].text
	except:
		pass
	try:
		location_raw =  soup.find_all('p')[1].select("span")[3].text
		if location_raw:
			location = geocode(address = location_raw)
			time.sleep(1)
	except:
		pass
	try:
		start_raw = soup.find_all('p')[0].select("span")[1].text
		parsed_date = re.match(r'\w{3,9}\s\d{1,2},\s\d{4}',start_raw)
		if parsed_date:
			start = datetime.strptime(parsed_date.group(), '%B %d, %Y').isoformat()
	except:
		pass
	try:
		stop_raw = soup.find_all('p')[0].select("span")[2].text
		parsed_date = re.match(r'\w{3,9}\s\d{1,2},\s\d{4}',stop_raw)
		if parsed_date:
			stop = datetime.strptime(parsed_date.group(), '%B %d, %Y').isoformat()
	except:
		pass
	try:
		desc = '\n'.join([x.text for x in soup.findAll('p')])
	except:
		pass
	#try:
	#print soup.select("span")
	#print image
	# image_name = path_leaf(image)
	# urllib.urlretrieve(image, "images/"+image_name)
	# with open("images/"+image_name, "rb") as image_file:
		# encoded_image = base64.b64encode(image_file.read())
	#except:
		#pass
	
	#user_profile_list = ['54c10610e4b02388960d57af','54c83e44e4b02388960d6042']
	user_profile_list = ['54c10610e4b02388960d57af','54c83e44e4b02388960d6042','54db67b7e4b0746041b58a9c','54f6a59fe4b06228a10b98f3','54b93685e4b071097a83c71d','54ba1c0be4b071097a83c75e']
		
	event = {}
	event['clientId'] = 'bcb8a8a3173642408ff118845a7bb947'
	event['userProfId'] = random.choice(user_profile_list)
	event['title'] = title
	event['desc'] = desc
	event['source'] = 1
	event['startDateTime'] = start
	event['endDateTime'] = stop
	event['eventTypeId'] = 1
	event['eventType'] = "excite"
	if location:
		event['loc'] = location
	else:
		event['loc'] = {}
		event['loc']['locNm'] = ""
	
	pp.pprint(event)
	
	return event
	#return((title,company,category,location,start,stop,desc)) 

result = []
for categories in link:
    categories = categories + "/page/{}/"
    for page in range (1,50):
        url = (domain + categories).format(page)
        try:
            html = requests.get(url).content
            soup = BeautifulSoup(html)
            items = [(x.text, x["href"], x.img["src"]) for x in soup.select("#widget-promos-grid")[0].select("a")]  
            result = result + items
            print("Crawling " + url)
        except: 
            break

df = pd.DataFrame(result)        

#result = []
for i in range(len(df)):
	url = df[1][i]
	encoded_image = None
	image = df[2][i]
	if image:
		try:
			image_name = path_leaf(image)
			urllib.urlretrieve(image, "images/"+image_name)
			with open("images/"+image_name, "rb") as image_file:
				encoded_image = base64.b64encode(image_file.read())
		except:
			pass
	html = requests.get(domain + url).content
	soup = BeautifulSoup(html)
	event = get_detail(soup)
	print json.dumps(event)
	
	if 'latitude' in event['loc']:
		
		#url = 'http://172.16.53.40:8080/ExcServiceTestE/eventInternal/populateEvent'
		#url = 'http://52.74.121.155:8080/ExcService_1_0/eventInternal/populateEvent'
		url = 'http://apil.8excite.com:8080/ExcService_1_0/eventInternal/populateEvent'
		headers = {'content-type': 'application/json'}
		response = requests.post(url, data=json.dumps(event), headers=headers)
		
		json_response = json.loads(response.text)
		print json_response
		event_reponse = json_response['eventList'][0]
		
		if encoded_image and json_response['statusList'][0]['statusCode'] == 0:
			event_image = {}
			event_image['clientId'] = event['clientId']
			event_image['userProfId'] = event['userProfId']
			event_image['eventId'] = event_reponse['eventId']
			event_image['title'] = event_reponse['title']
			event_image['images'] = []
			event_image['images'].append(str(encoded_image))
			#url = 'http://172.16.53.40:8080/ExcServiceTestE/eventInternal/populateEventImages'
			#url = 'http://52.74.121.155:8080/ExcService_1_0/eventInternal/populateEventImages'
			url = 'http://apil.8excite.com:8080/ExcService_1_0/eventInternal/populateEventImages'
			headers = {'content-type': 'application/json'}
			
			with open('bigsale_image.json', 'w') as outfile:
				json.dump(event_image, outfile)
			
			response = requests.post(url, data=json.dumps(event_image), headers=headers)
			print response.text.encode("utf-8")
	else:
		print "SKIPPING upload, due to lack of coordinate"
	
    #detail = get_detail(soup)
    #result = result + [detail] 

# save22 = pd.DataFrame(result)   

# save22.columns = ["Title", "CompanyName", "Category", "Location", "StartDate", "EndDate", "Desc"]

# save22['image'] = df[2]

# save22 = save22[save22.ix[:, 1]!= ""]

# save22.to_csv("save22.csv", encoding="utf8")



# gmaps = googlemaps.Client(key='AIzaSyATojLAIh4vXbWbQ-fSrYuu9s10TOgkxYM')

# result = []
# for i in range(len(save22)):
    # try:
        # lat = gmaps.geocode(save22['Location'][i])[0]
        # latitude = lat['geometry']['location']['lat']
        # longtitude = lat['geometry']['location']['lng']
        # Vicinity = lat["formatted_address"]
        # City = next((item for item in lat["address_components"] if item['types'] == ['locality', 'political']), None)["long_name"]
        # State = next((item for item in lat["address_components"] if item['types'] == ['administrative_area_level_1', 'political']), None)["long_name"]
        # Country = next((item for item in lat["address_components"] if item['types'] == ['country', 'political']), None)["long_name"]
        # Postcode = next((item for item in lat["address_components"] if item['types'] == ['postal_code']), None)["long_name"]
    # except:
        # try:
            # lat = gmaps.geocode(save22['CompanyName'][i] + "Selangor")[0]
            # latitude = lat['geometry']['location']['lat']
            # longtitude = lat['geometry']['location']['lng']
            # Vicinity = lat["formatted_address"]
            # City = next((item for item in lat["address_components"] if item['types'] == ['locality', 'political']), None)["long_name"]
            # State = next((item for item in lat["address_components"] if item['types'] == ['administrative_area_level_1', 'political']), None)["long_name"]
            # Country = next((item for item in lat["address_components"] if item['types'] == ['country', 'political']), None)["long_name"]
            # Postcode = next((item for item in lat["address_components"] if item['types'] == ['postal_code']), None)["long_name"]
        # except:
            # latitude = ""
            # longtitude = ""
            # Vicinity = ""
            # City = ""
            # State = ""
            # Country = ""
            # Postcode = ""
    # print([latitude, longtitude])
    # result = result + [(latitude, longtitude, Vicinity, City, State, Country, Postcode)]
    # time.sleep(1)

# lat = pd.DataFrame(result)

# lat.columns = ["latitude", "longtitude", "Vicinity", "City", "State", "Country", "Postcode"]

# save22 = save22.join(lat)

# save22.to_csv("save22.csv", encoding="utf8")

# save22


