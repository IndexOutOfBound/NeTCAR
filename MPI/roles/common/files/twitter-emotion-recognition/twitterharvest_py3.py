# twitter harvester: use streaming api to collect active user who is located at australia, 
#then use search api to explore the user's timeline
#only tweet with "place" in state capital city and tweets in English are collected
#coding:utf-8


import tweepy
import json
import threading
import twitter
import time
import couchdb
import subprocess
from mpi4py import MPI
import sys

from emojificate.filter import emojificate
from emotion_predictor import EmotionPredictor
from PreprocessTweet import preprocess_tweet
import re


starttime=time.clock()
model = EmotionPredictor(classification='ekman', setting='mc')
starttime=time.process_time()
print (starttime)

comm=MPI.COMM_WORLD
size=comm.Get_size()
rank=comm.Get_rank()
#count=0
db=couchdb.Server("http://admin:admin@localhost:5984")
#http://admin:admin@localhost:5984
if rank == 0:
	try:
		database=db["twitter"]
		#print(len(database))
	except:
		database=db.create("twitter")
	consumer_key = 'qFG8UE2HNdKLxrQqGmRuvM2GW'
	consumer_secret='UqSbasxKHPofBxIVj7FdE8iLMgqBkRnw5j0FmuZXdD3bwlNnRu'
	access_token='1354151035-18BfMJ0MpptHyMPAoXKJtct2Y79ADzxFh55KQQl'
	access_token_secret='X2AEvMCwfg0doGu8hdZ5T5GBVln8yuzgvvRD4VtuPfC8k'
	coordinate=[144.5532, -38.2250, 145.5498, -37.5401] # melb
	#database=db["twitter"]
	#coordinate=[138.4421, -35.3490, 138.7832, -34.6481 ] # canberra
if rank == 1:
	consumer_key= 'VoOUcfsuU2Xw74Dp6OmdVaAx5'
	consumer_secret='t1OVXZM4VXcdDArFykv7uDx65GOutpD9QeV3VMKXplSpYUvRsq'
	access_token='1354151035-fUiaFz46uoToUQC3JwFJLTt7O7QshSHSqctAOEs'
	access_token_secret='dCPVUfsGp9rA8PRbHRLIEOUzV34WFR6r3S6U7ox1T2Zc2'
	coordinate=[150.6396, -34.1399, 151.3439, -33.5780] # sydney
	#database=db["twitter"]

if rank == 2:
	consumer_key='rKju67MkpCg55cOmGiEmi5efO'
	consumer_secret='tqY3bYyRZHa6tJCCpehbroOifndV1rgmNU82qq0UID4ukQkynh'
	access_token='3009384632-HVYfglhGG3XNlBTLTdVnn5uj5EBBuoqqrGPlbgV'
	access_token_secret='27HLpkVdEEwaVk4A6yuzJDHxwcWpUMYX9gfq9bIE4YSlt'
	coordinate=[138.4421, -35.3490, 138.7832, -34.6481, 115.5607, -32.4824, 116.4151, -31.4552] # Adelaide + perth
	#database=db["twitter"]
if rank == 3:
	consumer_key='RXNJkCTQF4FXdyISue0M5RCSj'
	consumer_secret='kXSzoVBEU3bnFweWHE624NPn3T7GrGilwfbm1EBCzqR1CAYYCl'
	access_token='1354151035-rHMuSXWGSWDV6XPlOLIhtK3lKueMCXPzOXtse6G'
	access_token_secret='3AkzeTCPcVcqT5cDwndcjpN9nBhmHB5vMuQLZhjQYjfOd'
	coordinate=[144.5937, -38.4338, 145.5125, -37.5112] # Brisbane
	#database=db["twitter"]
if(rank!=0):
	while (True):
		try:
			database=db["twitter"]
			break
		except:
			continue

auth1=tweepy.OAuthHandler(consumer_key, consumer_secret)

auth1.set_access_token(access_token,access_token_secret,)

auth2=twitter.Api(consumer_key=consumer_key,consumer_secret=consumer_secret,access_token_key=access_token,access_token_secret=access_token_secret,sleep_on_rate_limit=True)

api=tweepy.API(auth1,wait_on_rate_limit=True,wait_on_rate_limit_notify=True)

userlist=[]

capitalCity=["Melbourne","Sydney","Perth","Brisbane","Adelaide"] #5 cities

def emoji_mapper(tweet):
    tweet = tweet.replace('\"', ' ')
    returned_text = emojificate(tweet)

    emojis = re.findall(r'<img.*?>', str(returned_text))
    if emojis:

        for emoji in emojis:
            matched_emoji = re.match(r'.*title="(.*?)".*', emoji).group(1)
            returned_text = returned_text.replace(emoji, ' '+matched_emoji+' ')
    return returned_text


class StreamListener(tweepy.StreamListener):
	def on_status(self,tweet):
		print("ran on status")

	def on_error (self,status_code):
		print ('error' + repr(status_code))
		if status_code==420:
			#returning False in on_data disconnects the stream
			return False
		return False

	def on_data(self,data):
		try:
			j=json.loads(data,encoding='utf-8')
			if(j["user"]["lang"]=="en"):
				username=j["user"]["screen_name"]
				print(username)
				userlist.append(username)

			return True
		except Exception as e:
			print(str(e))


def streamingUserId():
	l=StreamListener()
	streamer = tweepy.Stream(auth=auth1,listener=l)
	streamer.filter(locations=coordinate)
def searchUserHistory(user):
	#print recent tweet of the user
	user_tweets=auth2.GetUserTimeline(screen_name=user,count=100)
	for tweet in user_tweets:
		j={}
		try:
			j=json.loads(str(tweet),encoding='utf-8')
			doc={}
			text=j["text"]
			#print(j)
			matched = re.findall(r'https?://t\.co/.{10}', text, re.MULTILINE)
			if matched:
				for strip_str in matched:
					text = text.replace(strip_str, '')

			location=j["place"]["full_name"]
			#print("begin to map")
			text_returned=emoji_mapper(text)
			emotion = preprocess_tweet(text_returned, model)
			#print(text_returned)
			doc["emotion"]=emotion
			city=location.split(",", 1)
			if(city[0] in capitalCity):
				doc["location"]=city[0]
			if(city[1] in capitalCity):
				doc["location"]=city[1]

			if(doc["location"] is not None and j["lang"]=="en" and doc["emotion"] is not None):
				
				doc["_id"]=str(j["id"])
				doc["text"]=text_returned
				print(doc)
				database.save(doc)


		except BaseException as e:
			#print(e)
			continue

		except couchdb.http.Resource:
			#handle duplicate tweet
			continue
		except Exception as e1:
			#print(e1)
			continue
	print("-------------------------------------------------")
	#file_handle.write('------------------------------------------')

try:
	t1=threading.Thread(target=streamingUserId,args=())
	t1.setDaemon(True)
	t1.start()
except:
	print("thread error")

while True:
	for user in userlist:
		searchUserHistory(user)
		userlist.remove(user)
		if (int(len(database))>int(sys.argv[1])):
			exit()
#print(count)
exit()

#144.5532, -38.2250, 145.5498, -37.5401 # melb y
#150.6396, -34.1399, 151.3439, -33.5780 # sydney y
#138.4421, -35.3490, 138.7832, -34.6481 # Adelaide y

#115.5607, -32.4824, 116.4151, -31.4552 # Perth y

#144.5937, -38.4338, 145.5125, -37.5112 # Brisbane y
