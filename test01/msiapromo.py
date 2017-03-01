#!/usr/bin/env python
# -*- coding: utf-8 -*- 
from bs4 import BeautifulSoup
import pandas as pd
import requests
import googlemaps
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

html=requests.get("http://msiapromos.com/").content

soup=BeautifulSoup(html)

links = [x["href"] for x in soup.select("ul.sideCategorylist a")]

domain="http://msiapromos.com"

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
		'key': 'AIzaSyBNsNWRIGvCtmQe3DMQHVqxzzdwb0asmFg'
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



def has_next(soup):
    try:
        result = soup.select(".nav-pageText")[0].text.encode('ascii')=='Next Page →'.encode('ascii')
        return(result)
    except:
        False

result = []
for i in links:
    i = i + "page/{}/"
    for j in range(1,1000):
        url  = (domain + i).format(j)
        print(url)
        html = requests.get(url).content
        soup = BeautifulSoup(html)
        link = [x["href"] for x in soup.select(".vevent > .ablock")]
        result = result + link
        if has_next(soup):
            pass
        else:
            break
df = pd.DataFrame(result)

df.to_csv("links.csv",encoding='utf8')

def get_data(soup):
	
	title = None
	start = None
	end = None
	loc = None
	encoded_image = None
	desc = None
	try:
		title = [x for x in soup.select(".entry-title")][0].text
	except:
		pass
	try:
		start_raw = [x.select("td") for x in soup.select(".eventDetailsTable")][0][0].text
		parsed_date = re.match(r'\d{1,2}\s\w{3}\s\d{4}',start_raw)
		#print parsed_date.group()
		if parsed_date:
			start = datetime.strptime(parsed_date.group(), '%d %b %Y').isoformat()
	except:
		pass
	try:
		end_raw = [x.select("td") for x in soup.select(".eventDetailsTable")][0][1].text
		parsed_date = re.match(r'\d{1,2}\s\w{3}\s\d{4}',end_raw)
		#print parsed_date.group()
		if parsed_date:
			end = datetime.strptime(parsed_date.group(), '%d %b %Y').isoformat()
	except:
		pass
	try:
		loc_raw = soup.select(".fn")[1].text.strip()
		print loc_raw
		if loc_raw:
			loc = geocode(address = loc_raw)
			time.sleep(1)
	except:
		pass
	try:
		image = [x ["src"] for x in soup.select(".alignnone")][0]
		image_name = path_leaf(image)
		urllib.urlretrieve(image, "images/"+image_name)
		with open("images/"+image_name, "rb") as image_file:
			encoded_image = base64.b64encode(image_file.read())
	except:
		pass
	try:
		desc = soup.select(".description")[0].text.split("Advertisement")[0]
	except:
		pass
	
	#user_profile_list = ['54c10610e4b02388960d57af','54c83e44e4b02388960d6042']
	user_profile_list = ['54c10610e4b02388960d57af','54c83e44e4b02388960d6042','54db67b7e4b0746041b58a9c','54f6a59fe4b06228a10b98f3','54b93685e4b071097a83c71d','54ba1c0be4b071097a83c75e']
		
	event = {}
	event['clientId'] = 'bcb8a8a3173642408ff118845a7bb947'
	event['userProfId'] = random.choice(user_profile_list)
	event['title'] = title
	event['desc'] = desc
	event['source'] = 1
	event['startDateTime'] = start
	event['endDateTime'] = end
	event['eventTypeId'] = 1
	event['eventType'] = "excite"
	if loc:
		event['loc'] = loc
	else:
		event['loc'] = {}
		event['loc']['locNm'] = ""
	
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

	#return([title,start,end,loc,image,desc])

#data = []
for i in range(0,len(df)):
	html = requests.get(df[0][i]).content
	soup = BeautifulSoup(html)
	get_data(soup)
	#dt = get_data(soup)
	#print dt
	#data = data + [dt]
	
# msiapromo = pd.DataFrame(data)

# msiapromo.columns = ['title','startDateTime','endDateTime','location','image','desc']

# msiapromo.to_csv("msiapromo.txt",encoding='utf8')

# msiapromo=pd.read_csv("msiapromo.txt")

# for row in range(len(msiapromo)):
    # if type(msiapromo.ix[row,2]) == float:
        # msiapromo.ix[row,2] = msiapromo.ix[row,1]

# gmaps = googlemaps.Client(key='AIzaSyBNsNWRIGvCtmQe3DMQHVqxzzdwb0asmFg')

# def f(x):
	# try:
		# location = gmaps.geocode(x)[0]
		# time.sleep(1)
		# if [item for item in location["address_components"] if item['types'] == ['country', 'political']][0]["long_name"] == 'Malaysia':
			# city=next((item for item in location["address_components"] if item['types'] == ['locality', 'political']), None)["long_name"]
			# country=next((item for item in location["address_components"] if item['types'] == ['country', 'political']), None)["long_name"]
			# vicinity=location['formatted_address']
			# longtitude = location["geometry"]["location"]["lng"]
			# locNm=next((item for item in location["address_components"] if item['types'] == ['point_of_interest', 'establishment']), None)["long_name"]
			# state=next((item for item in location["address_components"] if item['types'] == ['administrative_area_level_1', 'political']), None)["long_name"]
			# postCode=next((item for item in location["address_components"] if item['types'] == ['postal_code']), None)["long_name"]
			# lattitude = location["geometry"]["location"]["lat"]
		# else:
			# city=""
			# country=""
			# vicinity=""
			# longtitude=""
			# locNm=""
			# state=""
			# postCode=""
			# lattitude=""
	# except:
		# city=""
		# country=""
		# vicinity=""
		# longtitude=""
		# locNm=""
		# state=""
		# postCode=""
		# lattitude=""
	# print [city,country,vicinity,longtitude,locNm,state,postCode,lattitude]
	# return([city,country,vicinity,longtitude,locNm,state,postCode,lattitude])

#place = [f(x) for x in msiapromo.ix[:,3]]



