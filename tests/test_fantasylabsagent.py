import datetime as dt
import logging
import random
import unittest

from nba.agents.fantasylabs import FantasyLabsNBAAgent
from nba.dates import *

class FantasyLabsNBAAgent_test(unittest.TestCase):

    def setUp(self):
        self.a = FantasyLabsNBAAgent(db=True, use_cache=True)

    def test_init(self):
        adb = FantasyLabsNBAAgent(db=True)
        self.assertIsNotNone(adb.db)
        asafe = FantasyLabsNBAAgent(safe=True)
        self.assertIsNotNone(adb.safe)
        asafe = FantasyLabsNBAAgent(use_cache=True)
        self.assertIsNotNone(adb.scraper)

    def test_past_day_models(self):
        delta = random.choice(range(1,7))
        d = dt.datetime.today() - dt.timedelta(delta)
        fmt = site_format('fl')
        models, pp_models = self.a.past_day_models(model_day=dt.datetime.strftime(d, fmt))
        logging.debug('there are {0} models'.format(len(models)))
        self.assertIsInstance(models, list)
        self.assertTrue(len(models) > 0)
        model = random.choice(models)
        self.assertIsInstance(model, dict)
        self.assertIn('Salary', model)

        pp_model = random.choice(pp_models)
        self.assertIsInstance(pp_model, dict)
        self.assertIn('salary', pp_model)


    def test_range_models(self):
        fmt = site_format('fl')
        delta = random.choice(range(7,14))
        range_start = dt.datetime.today() - dt.timedelta(delta)
        range_end = range_start + dt.timedelta(2)

        models, pp_models = self.a.range_models(range_start=dt.datetime.strftime(range_start, fmt),
                                                range_end=dt.datetime.strftime(range_end, fmt))

        logging.debug('there are {0} models'.format(len(models)))
        self.assertIsInstance(models, list)
        self.assertTrue(len(models) > 0)
        model = random.choice(models)
        self.assertIsInstance(model, dict)
        self.assertIn('Salary', model)

        pp_model = random.choice(pp_models)
        self.assertIsInstance(pp_model, dict)
        self.assertIn('salary', pp_model)

    def test_today_models(self):
        models, pp_models = self.a.today_models()
        logging.debug('there are {0} models'.format(len(models)))
        self.assertIsInstance(models, list)
        self.assertTrue(len(models) > 0)
        model = random.choice(models)
        self.assertIsInstance(model, dict)
        self.assertIn('Salary', model)

        pp_model = random.choice(pp_models)
        self.assertIsInstance(pp_model, dict)
        self.assertIn('salary', pp_model)

if __name__=='__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()