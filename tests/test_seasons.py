import random
import unittest

from nba.season import *


class NBASeasons_test(unittest.TestCase):


    def setUp(self):
        self.keys = list(seasons().keys())

    @property
    def day(self):
        return random.choice(range(1, 28))

    @property
    def month(self):
        return random.choice(range(1, 12))

    @property
    def season_code(self):
        return random.choice(self.keys)

    @property
    def year(self):
        return random.choice(range(2010, 2018))

    def test_in_what_season_year(self):
        d = datetime.datetime(self.year, self.month, self.day)
        sy = in_what_season_year(d)
        self.assertIsInstance(sy, int)
        d = datetime.datetime.today()
        sy = in_what_season_year(d)
        self.assertEqual(d.year, sy)

    def test_season_year_to_season_code(self):
        sy = self.year
        sc = season_year_to_season_code(sy)
        try:
            self.assertIsInstance(sc, basestr)
        except:
            self.assertIsInstance(sc, str)
        sy = 2016
        self.assertEqual('2015-16', season_year_to_season_code(sy))

    def test_season_code_to_season_year(self):
        sc = self.season_code
        sy = season_code_to_season_year(sc)
        self.assertIsInstance(sy, int)
        sc = '2015-16'
        self.assertEqual(2016, season_code_to_season_year(sc))

    def test_season(self):
        sc = self.season_code
        seas = season(season_code=sc)
        self.assertIsInstance(seas, dict)
        seas = season(season_year=self.year)
        self.assertIsInstance(seas, dict)
        sy = 2014
        seas = season(season_year=sy)
        self.assertIsInstance(seas, dict)
        sc = '2015-16'
        seas = season(season_code=sc)
        self.assertIsInstance(seas, dict)

    def test_season_dates(self):
        d = season_dates(season_year=self.year)
        self.assertIsInstance(d, list)
        self.assertGreaterEqual(len(d), 1)

    def test_season_gamedays(self):
        """
        TODO: need to implement and then test
        """
        pass

    def test_season_end(self):
        self.assertIsInstance(season_end(season_year=self.year), datetime.datetime)
        self.assertIsInstance(season_end(season_code=self.season_code), datetime.datetime)

    def test_season_start(self):
        self.assertIsInstance(season_start(season_year=self.year), datetime.datetime)
        self.assertIsInstance(season_start(season_code=self.season_code), datetime.datetime)


if __name__=='__main__':
    unittest.main()