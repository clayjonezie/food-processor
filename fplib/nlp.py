from nltk.tokenize import RegexpTokenizer
from nltk.util import ngrams
import db, re
import operator
from string import lower

tweets = db.read_tweets()

texts = [tweet[2] for tweet in tweets]

bad_words = db.read_bad_words()

def add_to_hist(d, word):
  if word in d.keys():
    d[word] += 1
  else:
    d[word] = 1

d = dict()
tz = RegexpTokenizer(r'\w+')
for text in texts:
  words = tz.tokenize(text)
  words = [word for word in words if not re.match('^[0-9]*$', word)]
  words = [word for word in words if not word in bad_words]
  words = [lower(word) for word in words]
  for ngram in list(ngrams(words, 3)) + list(ngrams(words, 2)) + list(ngrams(words, 1)):
    word = " ".join(ngram)
    add_to_hist(d, word)

sorted_d = sorted(d.items(), key=operator.itemgetter(1))
print sorted_d
for word, n in sorted_d:
  print word.ljust(30), '*' * n

