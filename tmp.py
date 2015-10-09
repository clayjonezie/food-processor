from __future__ import print_function
from fplib import ndb_import
from models import NutrientData

imfunc = lambda lis : db.session.add(NutrientData().from_ndb(lis))
ndb_import.parse_and_call("fplib/NUT_DATA.txt", imfunc)
db.session.commit()
