from nltk.tokenize import RegexpTokenizer
from nltk.util import ngrams
from nltk.metrics.distance import edit_distance
from nltk.stem import WordNetLemmatizer
import re, fractions, operator
from string import lower
from collections import Counter
from fuzzywuzzy import fuzz
import requests
import re

from ..models import FoodDescription, FoodShort, Tag


def tokenize(text):
    """
    First splits on r',|\.|and', strips the result, and removes empty tokens
    :param text:
    :return: list of string tokens
    """
    tokens = re.split(r',|\.|and', text)
    tokens = [t.strip() for t in tokens]
    tokens = [t for t in tokens if t is not u'']
    return tokens


# performs simple existance search against the 'long_desc'
# field of FoodDescription
def search_food_descriptions(query):
    """
    :param query: the string to be in the raw sql
    :return: a list of FoodDescription objects whose long_desc field contaians
    query
    """
    return FoodDescription.query.filter(
        FoodDescription.long_desc.like("%%%s%%" % query)).all()


def nearby_food_descriptions(query):
    """
    Performs a ranking algorithm based on the 'closest food' to this
    query. See implementation.
    :param query: the string to be passed to search_food_descriptions
    :return: a list sorted by nearness
    """
    nearnesses = list()
    query = query.strip()

    good_words = ["raw"]
    good_measurements = ["NLEA"]
    for food in search_food_descriptions(query):
        desc_parts = [part.strip() for part in food.long_desc.split(",") if part is not ""]
        weight = 100
        score = 0
        # weigh the earlier matches more
        for part in desc_parts:
            score += weight * (fuzz.ratio(query, part) - 50)
            weight -= 25

        # another heuristic, if there is an NLEA measurement its a common food
        if any(["NLEA" in ms.description for ms in food.measurements]):
            score += 50

        # if there is "raw" in the desc, its more common hopefully
        if any(["NLEA" in ms.description for ms in food.measurements]):
            score += 25

        nearnesses.append((score, food))

    # coming from google gives you a great score...
    google_resp = ask_google_for_ndb_no(query)
    if google_resp is not None:
        nearnesses.append((10000, FoodDescription.query.get(google_resp)))
        print 'google_resp: ', google_resp

    sorted_nearnesses = sorted(nearnesses, reverse=True)
    print sorted_nearnesses
    return map(lambda i: i[1], sorted_nearnesses)


def tag_raw_entry(raw_entry):
    lemer = WordNetLemmatizer()
    tags = list()
    for token in tokenize(raw_entry.content):
        quantity = 1
        parts = re.split("\s+", token)
        parts = [lemer.lemmatize(part) for part in parts]
        for i, part in enumerate(parts):
            if re.match(r'[0-9]', part) is not None:
                try:
                    quantity = float(fractions.Fraction(part))
                    del parts[i]
                except:
                    pass

        token = ' '.join(parts)
        best_fd = FoodShort.get_food(token, raw_entry.user)
        if (best_fd):
            measurement = best_fd.best_measurement()
        tag = Tag(raw_entry=raw_entry, text=token,
                  food_description=best_fd, count=quantity,
                  measurement=measurement)
        tags.append(tag)

    return tags


def ask_google_for_ndb_no(query):
    text = requests.get('http://www.google.com/search?q=%s+food' % query).text
    if 'USDA' not in text:
        text = requests.get('http://www.google.com/search?q=%s' % query).text
        if 'USDA' not in text:
            return None

    # limit between these two (see html of that url for reference)
    first = text.find('Sources include:')
    second = text.find('USDA')
    if first < 0 or second < 0:
        return None
    text = text[first:second]
    resp = re.search('qlookup%3D[0-9]+', text)
    if resp is None: 
        return None
    print 'resp group is', resp.group(0)
    return int(resp.group(0).replace("qlookup%3D",""))

