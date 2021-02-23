import tweepy
from tweepy.streaming import StreamListener
import pandas as pd
import os
path = #

OAUTH_TOKEN = #
OAUTH_TOKEN_SECRET = #
CONSUMER_SECRET = #
CONSUMER_KEY = #

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)

access_token = #
access_token_secret = #

auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

import json


class MyListener(StreamListener):
    def __init__(self, api, terms):
        self.api = api
        self.terms = terms
        print('Looking for:')
        print(terms)
        try:
            with open('%s/disinformation_already_tweeted.txt' % path) as f:
                self.already = f.read().splitlines()
        except:
            self.already = []

        try:
            with open('%s/disinformation_already_tweeted_urls.txt' % path) as f:
                self.already_urls = f.read().splitlines()
        except:
            self.already_urls = []

    def on_data(self, data):
        try:
            tweet = json.loads(data)
            hit = ""

            if ('text' in tweet and 'quoted_status' not in tweet and tweet['lang'] == 'en'):
                found = False

                if (tweet['text'].startswith('RT @')):
                    if('retweeted_status' in tweet):
                        tweet = tweet['retweeted_status']

                for term in self.terms:
                    if (term.lower() in tweet['text'].lower()):
                        found = True
                        hit = term.lower()

                if (found and len(tweet['entities']['urls']) > 0 and
                    tweet['in_reply_to_status_id_str'] == None):

                    id = tweet['id_str']
                    url = tweet['entities']['urls'][0]['expanded_url']

                    if('twitter.com' not in url):
                        if id not in self.already[-500:] and url not in self.already_urls[-500:]:
                            print('#Retweeted: ' + tweet['text'])
                            print('#Due to ' + hit)
                            api.retweet(id)

                            with open('%s/disinfo_tweets.json' % path, 'a') as f:
                                f.write(json.dumps(tweet) + "\n")

                            with open('%s/disinformation_already_tweeted.txt' % path, 'a') as f:
                                f.write(str(id) + "\n")

                            with open('%s/disinformation_already_tweeted_url.txt' % path, 'a') as f:
                                f.write(str(url) + "\n")

                            self.already.append(id)
                            self.already_urls.append(url)

                found = False


        except BaseException as e:
            print("Error on_data: %s" % str(e))
        return True

    def on_error(self, status):
        print("Error!")
        print(status)
        return True


with open('%s/disinformation_keywords.txt' % path) as f:
    liste_keywords = f.read().splitlines()

df = pd.read_csv('%s/disinfo_users.csv' % path)
liste_users = list(df.id.astype(str))
print('Following:')
print(liste_users)

twitter_stream = tweepy.Stream(auth, MyListener(api, liste_keywords))

while(True):
    try:
        twitter_stream.filter(follow=liste_users)
    except Exception as e:
        print(e)
        continue
