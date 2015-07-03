import sqlite3

from nltk.corpus import stopwords
from twitter import get_tweets

import datetime
import dateutil.parser

def twitter2db():
  conn = sqlite3.connect('food-processor.db')
  cur = conn.cursor()
  create_table_sql = "CREATE TABLE entries (twitter_id integer, date text, contents text)"

  try:
    cur.execute(create_table_sql)
  except sqlite3.OperationalError:
    pass

  tweets = get_tweets()
  tweets = [(tweet.id, tweet.created_at.isoformat(), tweet.text) for tweet in tweets]

  cur.executemany('INSERT INTO entries VALUES (?, ?, ?)', tweets)

  conn.commit()

def read_tweets():
  conn = sqlite3.connect('food-processor.db')
  cur = conn.cursor()
  rows = cur.execute('SELECT * FROM entries')
  return [(row[0], dateutil.parser.parse(row[1]), row[2]) for row in rows]

def write_bad_words_db():
  conn = sqlite3.connect('food-processor.db')
  cur = conn.cursor()

  create_table_sql = "CREATE TABLE bad_words (word text)"
  try:
    cur.execute(create_table_sql)
  except sqlite3.OperationalError:
    pass

  bad_words = stopwords.words('english')
  bad_words = bad_words + ["w", "ClayEatsFood", "cup", "x"]
  bad_words = [(word,) for word in bad_words]
  cur.executemany('INSERT INTO bad_words VALUES (?)', bad_words)
  conn.commit()

def read_bad_words():
  conn = sqlite3.connect('food-processor.db')
  cur = conn.cursor()
  rows = cur.execute('SELECT * FROM bad_words')
  return [row[0] for row in rows]
