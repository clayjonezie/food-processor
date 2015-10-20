from nltk.tokenize import RegexpTokenizer
from nltk.util import ngrams
import operator, re
from string import lower
from collections import Counter


# INFO EXTRACTION PROCESS (over-trained to my own data)
#  cut on "\n|\.|,|+"
#  send all to lower
#  cut on "\d+" but keep number in there
#  ditch bad words (could impl regex here)
#  ditch "\d+/\d+/\d+"

def histogram(texts, bad_words):
  d = Counter()
  tz = RegexpTokenizer(r'\n|\.|,|\+', gaps=True)
  for text in texts:
    phrases = tz.tokenize(text)
    phrases = [phrase.lower() for phrase in phrases]
    phrases = [re.sub("-*\d+/-*\d+/-*\d+", "", phrase) for phrase in phrases]
#    for bad_word in bad_words:
#      phrases = [re.sub(re.escape(bad_word), "", phrase) for phrase in phrases]
    phrases = [phrase for phrase in phrases if not re.match("^\s*$", phrase)]
    phrases = [re.sub("^\s+|\s+$", "", phrase) for phrase in phrases]
    
    for phrase in phrases:
      d[phrase] += 1

  sorted_d = sorted(d.items(), key=operator.itemgetter(1))
  sorted_d.reverse()
  return sorted_d


def tokenize(text):
  tokens = re.split(r',|\.', string)
  tokens = [t.strip() for t in tokens]
  tokens = [t for t in tokens if t is not '']
  return tokens
