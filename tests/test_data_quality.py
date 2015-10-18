import unittest

class NutritionDataQualityTest(unittest.TestCase):
  def setUp(self):
    d = models.NutritionalData.query.all()
    pass

  def tearDown(self):
    pass

  def testPotato(self):
    pass

  def testMultiply(self):
    self.assertEqual((0 * 10), 0)
    self.assertEqual((5 * 8), 40)

