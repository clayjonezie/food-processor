from nltk.tokenize import RegexpTokenizer
from nltk.util import ngrams
import db, re
import operator
from string import lower

tweets = db.read_tweets()
texts = [tweet[2] for tweet in tweets]
bad_words = db.read_bad_words()

# INFO EXTRACTION PROCESS (over-trained to my own data)
#  cut on "\n|\.|,|+"
#  send all to lower
#  cut on "\d+" but keep number in there
#  ditch bad words (could impl regex here)
#  ditch "\d+/\d+/\d+"

def add_to_hist(d, word):
  if word in d.keys():
    d[word] += 1
  else:
    d[word] = 1

d = dict()
tz = RegexpTokenizer(r'\n|\.|,|\+', gaps=True)
for text in texts:
  phrases = tz.tokenize(text)
  phrases = [phrase.lower() for phrase in phrases]
  phrases = [re.sub("-*\d+/-*\d+/-*\d+", "", phrase) for phrase in phrases]
  for bad_word in bad_words:
    phrases = [re.sub(re.escape(bad_word), "", phrase) for phrase in phrases]
  phrases = [phrase for phrase in phrases if not re.match("^\s*$", phrase)]
  phrases = [re.sub("^\s+|\s+$", "", phrase) for phrase in phrases]
  
  for phrase in phrases:
    add_to_hist(d, phrase)

sorted_d = sorted(d.items(), key=operator.itemgetter(1))

max_len = max([len(word[0]) for word in sorted_d])

for word, n in sorted_d:
  print word.ljust(max_len + 1), '*' * n

