from nltk.tokenize import RegexpTokenizer
import db, re
import operator

tweets = db.read_tweets()

texts = [tweet[2] for tweet in tweets]

def add_to_hist(d, word):
  if word in d.keys():
    d[word] += 1
  else:
    d[word] = 1

d = dict()
tz = RegexpTokenizer(r'\w+')
for text in texts:
  words = tz.tokenize(text)
  for word in words:
    if not re.match('^[0-9]*$', word):
      add_to_hist(d, word)

sorted_d = sorted(d.items(), key=operator.itemgetter(1))

print sorted_d

for word, n in sorted_d:
  print word.ljust(20), '*' * n

