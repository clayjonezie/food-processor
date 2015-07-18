import sqlite3

from nltk.corpus import stopwords
import twitter
import sys
import datetime
import dateutil.parser

def create_entries_table():
  conn = sqlite3.connect('food-processor.db')
  cur = conn.cursor()
  create_table_sql = "CREATE TABLE entries (twitter_id integer, date text, contents text)"

  try:
    cur.execute(create_table_sql)
  except sqlite3.OperationalError:
    print "didn't make entries table, already created"

def save_tweets():
  conn = sqlite3.connect('food-processor.db')
  cur = conn.cursor()

  tweets = twitter.download_tweets()
  tweets = [(tweet.id, tweet.created_at.isoformat(), tweet.text) for tweet in tweets]

  cur.executemany('INSERT INTO entries VALUES (?, ?, ?)', tweets)
  conn.commit()

def read_tweets():
  conn = sqlite3.connect('food-processor.db')
  cur = conn.cursor()
  rows = cur.execute('SELECT * FROM entries')
  return [(row[0], dateutil.parser.parse(row[1]), row[2]) for row in rows]

def create_bad_words_table():
  conn = sqlite3.connect('food-processor.db')
  cur = conn.cursor()

  create_table_sql = "CREATE TABLE bad_words (word text)"
  try:
    cur.execute(create_table_sql)
  except sqlite3.OperationalError:
    print "didn't make bad words table, already created"

def save_bad_words():
  conn = sqlite3.connect('food-processor.db')
  cur = conn.cursor()

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

if __name__ == '__main__':
  if len(sys.argv) > 1:
    try:
      ans = locals()[sys.argv[1]]()
      if (isinstance(ans, list)):
        for a in ans:
          print a
    except KeyError:
      print sys.argv[1], "does not exist"
  else:
    ls = dict(locals())
    for k in ls:
      if hasattr(ls[k], '__call__'):
        print k
