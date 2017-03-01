import nltk

import json
import csv
from operator import itemgetter
import ast
import yaml
import time
import os
 
#data = json.load(open('lowyat_item.json'))
#data = json.load(open('fb_item.json'))

#allcomment_rating_sum = 0.0
#allcomment_rating_count = 0
#comment = []


with open('mobile.csv', 'rb') as csvfile:
	data = csv.DictReader(csvfile, delimiter='|')

	word_rating_dict =  {}
	with open('word rating.csv', mode='r') as infile:
		reader = csv.reader(infile)
		word_rating_dict = {rows[0]:rows[1] for rows in reader}

	pos_tags_considered = ['RB','RBR','RBS','JJ','JJR','JJS','VB','VBD','VBG','VBN','VBP','VBZ','UH']
	file_exist = os.path.isfile('mobile_sentiment.csv')
	with open('mobile_sentiment.csv', 'ab') as fp:
		fieldname_order = ['comment_id', 'comment', 'comment_time', 'topic_id', 'topic_title', 'topic_url', 'topic_starter', 'topic_starttime', 'topic_lastaction', 'topic_replies', 'topic_views', 'topic_description', 'sentiment_type', 'sentiment_score']
		w = csv.DictWriter(fp, delimiter='|', fieldnames=fieldname_order)
		if not file_exist:
			w.writeheader()
		for r in data:
			tokens = nltk.word_tokenize(r['comment'].decode('utf-8').encode('ascii','replace'))
			tagged = nltk.pos_tag(tokens)
			filtered_tags = [t for t in tagged if t[1] in pos_tags_considered]
			rating_sum = 0.0
			rating_count = 0
			avg_rating = 0.0
			for word_tag in filtered_tags:
				word = word_tag[0].lower()
				if word_rating_dict.has_key(word):
					rating_sum += float(word_rating_dict[word])
					rating_count += 1
			if rating_count > 0:
				avg_rating = rating_sum/rating_count
			r['sentiment_score'] = avg_rating
			if avg_rating > 1:
				r['sentiment_type'] = 'positive'
			elif avg_rating < -1:
				r['sentiment_type'] = 'negative'
			else:
				r['sentiment_type'] = 'neutral'
			
			w.writerow(r)
			#allcomment_rating_sum += avg_rating
			#allcomment_rating_count += 1
			#comment.append({'comment':r['comment'],'sentiment_score':r['sentiment_score'],'sentiment_type':r['sentiment_type'],'total_rating':rating_sum})
			
			
				
	
	# for y in data:
		
		# text_joined = ''
		# print y['comment']
		# for comments in y['comment']:
			# text_joined = text_joined + comments.encode('ascii','ignore')
		# print text_joined
		# words = nltk.word_tokenize(text_joined)
		# tagged = nltk.pos_tag(words)
		# filtered_tags = [t for t in tagged if t[1] in pos_tags_used]
		# ratings_sum = 0.0
		# ratings_count = 0
		# for word_tag in filtered_tags:
			# word = word_tag[0].lower()
			# if word_rating_dict.has_key(word):
				# ratings_sum += float(word_rating_dict[word])
				# ratings_count += 1
		# if ratings_count > 0:
			# avg_rating = ratings_sum/ratings_count
			# comment.append({'comment':text_joined,'rating':avg_rating,'total_rating':ratings_sum})
			# allcomment_rating_sum += avg_rating
			# allcomment_rating_count += 1
		#print y['comment']
		#print avg_rating
		
# sorted_comment = sorted(comment, key=itemgetter('total_rating'))
# print "worst comment: " + sorted_comment[0]['comment'] + ', score: ' + str(sorted_comment[0]['sentiment_score']) + ', type: ' + sorted_comment[0]['sentiment_type']
# print "worst comment: " + sorted_comment[1]['comment'] + ', score: ' + str(sorted_comment[1]['sentiment_score']) + ', type: ' + sorted_comment[1]['sentiment_type']
# print "worst comment: " + sorted_comment[2]['comment'] + ', score: ' + str(sorted_comment[2]['sentiment_score']) + ', type: ' + sorted_comment[2]['sentiment_type']
# print "best comment: " + sorted_comment[-1]['comment'] + ', score: ' + str(sorted_comment[-1]['sentiment_score']) + ', type: ' + sorted_comment[-1]['sentiment_type']
# print "best comment: " + sorted_comment[-2]['comment'] + ', score: ' + str(sorted_comment[-2]['sentiment_score']) + ', type: ' + sorted_comment[-2]['sentiment_type']
# print "best comment: " + sorted_comment[-3]['comment'] + ', score: ' + str(sorted_comment[-3]['sentiment_score']) + ', type: ' + sorted_comment[-3]['sentiment_type']
# avg_allcomment_rating = allcomment_rating_sum/allcomment_rating_count
# print "average rating for all comment:" + str(avg_allcomment_rating)



# token2 = nltk.word_tokenize("After seeing the real device I find Note 4 is too ugly look for my liking, it is not nice.")
# tagged2 = nltk.pos_tag(token2)
# dt_tags = [t for t in tagged2 if t[1] in pos_tags_used]
# print tagged2
# print dt_tags
# entities = nltk.chunk.ne_chunk(tagged)