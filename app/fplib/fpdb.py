from nltk.corpus import stopwords
import sys
import datetime
import dateutil.parser
from ..models import *
from sqlalchemy.sql import text
from fuzzywuzzy import process



def me():
    """ returns the first user (c@c.me) """
    return User.query.get(0)


def print_tags():
    """ prints every tag in the system """
    for tag in Tag.query.all():
        print tag.__repr__()


def save_bad_words(db):
    bad_words = stopwords.words('english')
    bad_words = [word.lower() for word in bad_words]

    for word in bad_words:
        bw = BadWord(word=word)
        db.session.add(bw)

    db.session.commit()


def desc_fts(db, word, limit=25, thresh=60):
    results = FoodDescription.query.from_statement(text("SELECT *, MATCH (common_name) \
            AGAINST ('" + word + "' IN NATURAL LANGUAGE MODE) AS score\
            FROM food_descriptions WHERE MATCH \
            (common_name) AGAINST ('" + word + "' IN NATURAL LANGUAGE MODE)\
            LIMIT " + str(limit) + ";"))
    
    all_results = results.all()
    processed = process.extract(word, all_results, processor=lambda x: x.common_name, limit=len(all_results))
    return [p[0] for p in processed if p[1] >= thresh]


def measure_desc_fts(db, word, food, limit=5):
    results = MeasurementWeight.query.from_statement(text("SELECT *, MATCH (description) \
            AGAINST ('" + word + "' IN NATURAL LANGUAGE MODE) AS score\
            FROM measurement_weights WHERE MATCH \
            (description) AGAINST ('" + word + "' IN NATURAL LANGUAGE MODE)\
            AND ndb_no=" + str(food.id) + "\
            LIMIT " + str(limit) + ";"))
    return results.all()
