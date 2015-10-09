from fp_import import ndb_import
from models import FoodDescription

imfunc = lambda lis : db.session.add(FoodDescription().from_ndb(lis))
ndb_import.parse_and_call("fp_import/FOOD_DES.txt", imfunc)
db.session.commit()
