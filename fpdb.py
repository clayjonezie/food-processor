import sqlite3

from nltk.corpus import stopwords
import sys
import datetime
import dateutil.parser
from models import *
from fplib import twitter

def save_tweets(db, user, screen_name):
  tweets = twitter.download_tweets(screen_name)
  raw_entries = [RawEntry().from_tweet(tweet, user) for tweet in tweets]
  db.session.add_all(raw_entries)
  db.session.commit()
  return len(raw_entries)

def save_bad_words(db):
  bad_words = stopwords.words('english')
  bad_words = [word.lower() for word in bad_words]

  for word in bad_words:
    bw = BadWord(word=word)
    db.session.add(bw)

  db.session.commit()

 
# depricated
# def read_bad_words():
#   conn = sqlite3.connect('food-processor.db')
#   cur = conn.cursor()
#   rows = cur.execute('SELECT * FROM bad_words')
#   return [row[0] for row in rows]
# 
# if __name__ == '__main__':
#   if len(sys.argv) > 1:
#     try:
#       ans = locals()[sys.argv[1]]()
#       if (isinstance(ans, list)):
#         for a in ans:
#           print a
#     except KeyError:
#       print sys.argv[1], "does not exist"
#   else:
#     ls = dict(locals())
#     for k in ls:
#       if hasattr(ls[k], '__call__'):
#         print k
