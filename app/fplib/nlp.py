from nltk.tokenize import RegexpTokenizer
from nltk.util import ngrams
from nltk.metrics.distance import edit_distance
from nltk.stem.snowball import SnowballStemmer
import operator, re
from string import lower
from collections import Counter
from ..models import FoodDescription, Tag, RawEntry, FoodShort


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
  tokens = re.split(r',|\.|and', text)
  tokens = [t.strip() for t in tokens]
  tokens = [t for t in tokens if t is not '']
  return tokens


# performs simple existnace search against the 'long_desc'
# field of FoodDescription
def search_food_descriptions(query):
  return FoodDescription.query.filter(
    FoodDescription.long_desc.like("%%%s%%" % query)).all()


# sorts the search results by edit distance with the query
# we split on comma and return the best dist of these for better results. 
def nearby_food_descriptions(query):
  stemmer = SnowballStemmer('english')
  query = stemmer.stem(query)
  nearnesses = list()
  for food in search_food_descriptions(query):
    food_comp = food.long_desc.split(',')
    best_nearness = min([edit_distance(stemmer.stem(c.strip()), query) for c in food_comp])
    total_nearness = edit_distance(food.long_desc, query)
    nearnesses.append((best_nearness, total_nearness, food))

  key = lambda i : (i[0], i[1])
  sorted_nearnesses = sorted(nearnesses, key=key)
  return [i[2] for i in sorted_nearnesses]

def tag_raw_entry(raw_entry):
  tags = list()
  for token in tokenize(raw_entry.content):
    tag = Tag(raw_entry=raw_entry, text=token)
    tags.append(tag)

  return tags
