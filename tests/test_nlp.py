import unittest
from app.fplib import nlp

class NlpTest(unittest.TestCase):
  def setUp(self):
    pass

  def tearDown(self):
    pass

  def testTokenize(self):
    s1 = "peach, hamburger, 3 apples, 12 oz coffee, hemp/chia/flax cereal."
    l1 = ["peach", "hamburger", "3 apples", "12 oz coffee", "hemp/chia/flax cereal"]
    self.assertEqual(nlp.tokenize(s1), l1)
    s2 = "peach,,.. hamburger,apples"
    l2 = ["peach", "hamburger", "apples"]
    self.assertEqual(nlp.tokenize(s1), l1)

