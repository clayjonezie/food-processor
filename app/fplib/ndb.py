# functions to interface with the USDA National Nutrient Database
# http://ndb.nal.usda.gov/ndb/doc/index
import requests, json, keys

api_base = "http://api.nal.usda.gov/ndb"


# http://api.nal.usda.gov/ndb/reports/?ndbno=11987&type=b&format=json&api_key=DEMO_KEY
def get_food(ndbno):
  url = api_base + '/reports/'
  payload = {'ndbno': '%05d' % ndbno, 
             'type': 'f',
             'api_key': keys.data_gov_api_key,
             'format': 'json',
             'type': 'b'}
  r = requests.get(api_base+'/reports', params=payload)
  return r.json

