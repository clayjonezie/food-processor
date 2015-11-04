from nltk.tokenize import RegexpTokenizer
from nltk.util import ngrams
from nltk.metrics.distance import edit_distance
from nltk.stem import WordNetLemmatizer
import re
import fractions
import operator
import re
from string import lower
from collections import Counter

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


# sorts the search results by edit distance with the query
# we split on comma and return the best dist of these for better results.
def nearby_food_descriptions(query):
    """

    :param query: the string to be passed to search_food_descriptions
    :return:
    """
    lemer = WordNetLemmatizer()
    query = lemer.lemmatize(query)
    nearnesses = list()
    for food in search_food_descriptions(query):
        food_parts = food.long_desc.split(',')
        best_nearness = min(
            [edit_distance(lemer.lemmatize(c.strip()), query) for c in food_parts])
        total_nearness = edit_distance(food.long_desc, query)
        nearnesses.append((best_nearness, total_nearness, food))

    key = lambda i: (i[0], i[1])
    sorted_nearnesses = sorted(nearnesses, key=key)
    return map(operator.itemgetter(2), sorted_nearnesses)


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
        tag = Tag(raw_entry=raw_entry, text=token,
                  food_description=best_fd, count=quantity)
        tags.append(tag)

    return tags
