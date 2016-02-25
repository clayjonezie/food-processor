from nltk.stem import WordNetLemmatizer
import fractions
import operator
from fuzzywuzzy import fuzz, process
import requests
import re

from ..models import FoodDescription, Tag
from . import fpdb

lemmer = WordNetLemmatizer()

def tokenize(text):
    """
    First splits on r',|\.|and', strips the result, and removes empty tokens
    :param text: the text to tokenize
    :return: list of string tokens
    """
    tokens = re.split(r',|\.(?![0-9])|and', text)
    tokens = [t.strip() for t in tokens]
    tokens = [t for t in tokens if t is not u'']
    return tokens



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
    return int(resp.group(0).replace("qlookup%3D", ""))


def realtime_parse(query):
    """ 
    returns a dictionary of parsed entry 
    dictionary has food item, quantity, and measure
    """
    parts = re.split("\s+", query)
    parts = [lemmer.lemmatize(part) for part in parts]
    quantity, parts = get_quantity(parts)

    item = FoodDescription.query.get(9040)
    measure = item.measurements[0]

    return {'item': {'id': item.id, 'desc': item.long_desc},
            'measure': {'id': measure.id, 'desc': measure.description},
            'quantity': quantity}

def get_quantity(parts):
    """ returns a tuple (quantity, parts without quantity) """
    quantity = 1
    for i, part in enumerate(parts):
        if re.match(r'[0-9]*\.*[0-9]', part) is not None:
            try:
                quantity = float(fractions.Fraction(part))
                del parts[i]
            except:
                pass
    
    return (quantity, parts)

def realtime_parse_autocomplete(db, query):
    parts = re.split("\s+", query)
    parts = [lemmer.lemmatize(part) for part in parts]
    quantity, parts = get_quantity(parts)

    db_query = ' '.join(parts)
    foods = fpdb.desc_fts(db, db_query, 15)

    res = []
    for f in foods:
        for ms in f.measurements:
            res.append({'value': str(quantity) + " " +  ms.description + " x " + f.long_desc,
                        'data': {
                            'food-id': f.id,
                            'measure-id': ms.id,
                            'quantity': quantity
                            }})

    return {"suggestions": res}


def food_parse(db, query):
    """
    returns a jsonable dict for the autocomplete js library we are using
    for a text field used to select a food item
    :param db:
    :param query:
    :return:
    """
    parts = re.split("\s+", query)
    parts = [lemmer.lemmatize(part) for part in parts]

    db_query = ' '.join(parts)
    foods = fpdb.desc_fts(db, db_query, 15)

    res = []
    for f in foods:
        res.append({'value': f.long_desc,
                    'data': {
                        'food-id': f.id
                    }})

    return {"suggestions": res}
