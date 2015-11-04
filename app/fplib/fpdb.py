# fpdb.py - Food Processor database operations

from nltk.corpus import stopwords
import sys
import datetime
import dateutil.parser
from ..models import *
import twitter


def me():
    return User.query.get(0)


def print_tags():
    for tag in Tag.query.all():
        print tag.__repr__()


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