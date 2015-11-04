import unittest
from app import models

class NutritionDataQualityTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testApple(self):
        apple = models.FoodDescription.query.get(9003)
        nutrients = apple.nutrients
        self.assertEqual(nutrients[0].nutrient.desc, u"Protein")
        self.assertEqual(nutrients[0].nutr_val, 0.26)
        self.assertEqual(nutrients[1].nutrient.desc, u"Total lipid (fat)")
        self.assertEqual(nutrients[1].nutr_val, 0.17)
        self.assertEqual(nutrients[2].nutrient.desc, u"Carbohydrate, by difference")
        self.assertEqual(nutrients[2].nutr_val, 13.81)

        self.assertEqual(nutrients[4].nutrient.desc, u"Energy")
        self.assertEqual(nutrients[4].nutr_val, 52)



