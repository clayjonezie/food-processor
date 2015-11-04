import unittest
from app.fplib import nlp

class NlpTest(unittest.TestCase):
  def setUp(self):
    pass

  def tearDown(self):
    pass

  def testTokenize(self):
    s1 = u'peach, hamburger, 3 apples, 12 oz coffee, hemp/chia/flax cereal.'
    l1 = [u'peach', u'hamburger', u'3 apples', u'12 oz coffee', u'hemp/chia/flax cereal']
    self.assertEqual(nlp.tokenize(s1), l1)
    s2 = u'peach,,.. hamburger,apples'
    l2 = [u'peach', u'hamburger', u'apples']
    self.assertEqual(nlp.tokenize(s1), l1)

