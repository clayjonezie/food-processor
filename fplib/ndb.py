# functions to interface with the USDA National Nutrient Database
# http://ndb.nal.usda.gov/ndb/doc/index
import requests

api_base = "http://api.nal.usda.gov/ndb"
headers = {'Content-Type': 'application/json'}

def get_food(ndbno):
  r = requests.get(""Content-Type:application/json" -d '{"ndbno":"01009","type":"f"}' DEMO_KEY@api.nal.usda.gov/ndb/reports

