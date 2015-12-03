from __future__ import print_function
from unidecode import unidecode
from ..models import *
from .. import db


def import_nutrient_data():
    import_function = lambda lis: db.session.add(NutrientData().from_ndb(lis))

    parse_and_call("app/fplib/NUT_DATA_0-99999.txt", import_function)
    db.session.commit()
    parse_and_call("app/fplib/NUT_DATA_100000-199999.txt", import_function)
    db.session.commit()
    parse_and_call("app/fplib/NUT_DATA_200000-399999.txt", import_function)
    db.session.commit()
    parse_and_call("app/fplib/NUT_DATA_400000-679044.txt", import_function)
    db.session.commit()


def import_food_description():
    import_function = lambda lis: db.session.add(
        FoodDescription().from_ndb(lis))
    parse_and_call("app/fplib/FOOD_DES.txt", import_function)
    db.session.commit()


def import_nutrient_definition():
    import_function = lambda lis: db.session.add(
        NutrientDefinition().from_ndb(lis))
    parse_and_call("app/fplib/NUTR_DEF.txt", import_function)
    db.session.commit()


def import_measurement_weights():
    def import_function(lis):
        db.session.add(MeasurementWeight().from_ndb(lis))
    parse_and_call("app/fplib/WEIGHT.txt", import_function)
    db.session.commit()


def parse_and_call(filename, func):
    i = 0
    for line in open(filename):
        i = i + 1
        vals = line.split('^')
        vals = map(lambda s: s.replace('~', ''), vals)
        vals = map(lambda s: s.replace('\xB5', 'u'), vals)
        vals = map(lambda s: unidecode(s), vals)
        vals = map(lambda s: s.strip(), vals)
        func(vals)

    print("read %s rows" % i)


def import_users():
    me = User(email='c@c.com', password='phil')
    db.session.add(me)
    db.session.commit()
