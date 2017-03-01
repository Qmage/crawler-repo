import simplejson
import urllib

GEOCODE_BASE_URL = 'https://maps.googleapis.com/maps/api/geocode/json'

def geocode(address, **geo_args):

	geo_args.update({
		'address': address,
		'language' : 'en',
		'region': 'my',
		'components': 'country:MY',
		'bounds': '3.0362,101.6151|3.2452,101.7582'
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