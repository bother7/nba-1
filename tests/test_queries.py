# coding: utf-8

import logging
import unittest

from nba.db.queries import *
from nba.utility import getdb


class queries_test(unittest.TestCase):

    def setUp(self):
        self.db = getdb()

    def test_missing_game_boxscores(self):
        q = missing_game_boxscores('CST')
        vals = self.db.select_dict(q)
        self.assertIsNotNone(vals)
        logging.info(vals)

    def test_missing_player_boxscores(self):
        q = missing_player_boxscores('CST')
        vals = self.db.select_dict(q)
        self.assertIsNotNone(vals)
        logging.info(vals)

    def test_missing_player_gamelogs(self):
        q = missing_player_gamelogs('CST')
        vals = self.db.select_dict(q)
        self.assertIsNotNone(vals)
        logging.info(vals)

    def test_missing_playerstats(self):
        q = missing_playerstats('Totals')
        vals = self.db.select_dict(q)
        self.assertIsNotNone(vals)
        logging.info(vals)
        q = missing_playerstats('PerGame')
        vals = self.db.select_dict(q)
        self.assertIsNotNone(vals)
        logging.info(vals)

    def test_missing_team_gamelogs(self):
        q =missing_team_gamelogs('CST')
        vals = self.db.select_dict(q)
        self.assertIsNotNone(vals)
        logging.info(vals)

    def test_missing_teamstats(self):
        q = missing_teamstats('Totals')
        vals = self.db.select_dict(q)
        self.assertIsNotNone(vals)
        logging.info(vals)
        q = missing_teamstats('PerGame')
        vals = self.db.select_dict(q)
        self.assertIsNotNone(vals)
        logging.info(vals)

    def test_missing_team_boxscores(self):
        q = missing_team_boxscores('CST')
        vals = self.db.select_dict(q)
        self.assertIsNotNone(vals)
        logging.info(vals)

    def test_missing_team_opponent_dashboard(self):
        q = missing_team_opponent_dashboard('Totals')
        vals = self.db.select_dict(q)
        self.assertIsNotNone(vals)
        logging.info(vals)
        q = missing_team_opponent_dashboard('PerGame')
        vals = self.db.select_dict(q)
        self.assertIsNotNone(vals)
        logging.info(vals)


if __name__=='__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main()