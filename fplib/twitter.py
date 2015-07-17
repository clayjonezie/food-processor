# pulls data from twitter 

# see docs for this, but put a file in this dir
# called keys with the values you see used
import keys
import tweepy

def get_tweets():
  auth = tweepy.OAuthHandler(keys.twitter_consumer_key, 
                             keys.twitter_consumer_secret)
  auth.set_access_token(keys.twitter_access_token, 
                        keys.twitter_access_token_secret)

  api = tweepy.API(auth)

  # todo count=1000 probably will not actually work
  tweets = api.user_timeline(screen_name=keys.twitter_screen_name, count=1000)
  return tweets
