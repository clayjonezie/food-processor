import sqlite3

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
