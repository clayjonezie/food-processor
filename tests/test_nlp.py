import unittest
from app.fplib import nlp
from app.models import *

"""
There are some very long tests here.
There are some tests that depend on the data in the database, this is either
NDB data or data from the test suite database setup.

"""

class NlpTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_tokenize(self):
        s1 = u'peach, hamburger, 3 apples, 12 oz coffee, hemp/chia/flax cereal.'
        l1 = [u'peach', u'hamburger', u'3 apples',
              u'12 oz coffee', u'hemp/chia/flax cereal']
        self.assertEqual(nlp.tokenize(s1), l1)
        s2 = u'peach,,.. hamburger,apples'
        l2 = [u'peach', u'hamburger', u'apples']
        self.assertEqual(nlp.tokenize(s1), l1)

    def test_search_food_descriptions(self):
        #  select id, long_desc from food_descriptions where long_desc like '%%avocado%%';
        fds = nlp.search_food_descriptions('avocado')
        correct_fds = [
            FoodDescription.get('Avocados, raw, Florida'),
            FoodDescription.get('Avocados, raw, California'),
            FoodDescription.get('Oil, avocado'),
            FoodDescription.get('Avocados, raw, all commercial varieties')
        ]
        self.assertSetEqual(set(fds), set(correct_fds))

    def test_nearby_food_descriptions(self):
        fds = nlp.nearby_food_descriptions('avocado')
        correct_fds = [
            FoodDescription.get('Avocados, raw, all commercial varieties'),
            FoodDescription.get('Avocados, raw, California'),
            FoodDescription.get('Avocados, raw, Florida'),
            FoodDescription.get('Oil, avocado')
        ]
        self.assertListEqual(fds, correct_fds)

    #todo when this is better nailed down
    def test_tag_raw_entry(self):
        pass

    # maybe don't have network dependant tests
    # (well sql is on the network!)
    def test_ask_google_for_ndb_no(self):
        self.assertEqual(nlp.ask_google_for_ndb_no("coffee"), 14209)
        self.assertEqual(nlp.ask_google_for_ndb_no("avocado"), 9037)
        self.assertEqual(nlp.ask_google_for_ndb_no("toast"), 18065)

