import unittest
from app.models import *
from app import app, db
from datetime import datetime


class ModelsTest(unittest.TestCase):

    def setUp(self):
        print 'setup'

        test_user = User.query.filter(User.email=='test@test.com').first()
        if test_user is not None:
            db.session.delete(test_user)
            db.session.commit()

        user = User()
        user.email = 'test@test.com'
        user.password = 'test_password'

        self.test_user = user
        db.session.add(user)

        dateformat = "%Y-%m-%dT%H:%M:%S.%fZ"
        re = RawEntry(content='test raw entry...',
                      at=datetime.strptime("2015-01-01T12:12:12.000000Z",
                                           dateformat))
        db.session.add(re)

        apple = FoodDescription.query.get(9003)
        apple_short = FoodShort.get_or_create('apple')
        apple_large = MeasurementWeight.query.get(4003)

        orange = FoodDescription.query.get(9203)
        orange_short = FoodShort.get_or_create('orange')
        orange_size = MeasurementWeight.query.get(9309)

        tags = [Tag(re, 0, 'apple', apple_short, apple, 1, 100, 'g', apple_large),
                Tag(re, 10, 'orange', orange_short, orange, 1, 114, 'g', orange_size)]

        self.tags = tags

        db.session.add_all(tags)
        db.session.commit()


    def tearDown(self):
        [db.session.delete(tag) for tag in self.tags]
        db.session.delete(self.test_user)
        db.session.commit()


    def test_user_password(self):
        with self.assertRaises(AttributeError):
            print self.test_user.password

        self.assertEqual(self.test_user.email, 'test@test.com')
        self.assertTrue(self.test_user.verify_password('test_password'))


    def test_sum_tags(self):
        nuts_sum = FoodDescription.sum_nutrients(self.tags)
        print nuts_sum

