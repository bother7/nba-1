from __future__ import absolute_import, print_function

import logging
import random
import unittest

from nba.agents.nbacom import NBAComAgent
from nba.db.mockdb import MockNBAPostgres


class NBAComAgent_test(unittest.TestCase):

    def setUp(self):
        self.a = NBAComAgent(db=MockNBAPostgres())
        self.gids = [{'gd': '20161111', 'gid': '0021600123'},
         {'gd': '20161209', 'gid': '0021600337'}, {'gd': '20151213', 'gid': '0021500353'},
         {'gd': '20171225', 'gid': '0021700497'}, {'gd': '20160226', 'gid': '0021500861'},
         {'gd': '20151214', 'gid': '0021500366'}, {'gd': '20180116', 'gid': '0021700649'},
         {'gd': '20180126', 'gid': '0021700722'}, {'gd': '20170127', 'gid': '0021600703'},
         {'gd': '20160114', 'gid': '0021500592'}, {'gd': '20161222', 'gid': '0021600438'},
         {'gd': '20151223', 'gid': '0021500428'}, {'gd': '20170316', 'gid': '0021601016'},
         {'gd': '20160325', 'gid': '0021501081'}, {'gd': '20170317', 'gid': '0021601023'}]

    def gameids(self, n):
        return [g['gid'] for g in random.sample(self.gids, n)]

    def games(self, n):
        return random.sample(self.gids, n)

    def test_combined_boxscores(self):
        pbs, tbs = self.a.combined_boxscores(self.gameids(1))
        self.assertGreaterEqual(len(pbs), 0, 'pbs should be greater than zero')
        self.assertGreaterEqual(len(tbs), 0, 'tbs should be greater than zero')

    def test_game_boxscores(self):
        boxes = self.a.game_boxscores(self.games(1))
        self.assertGreaterEqual(len(boxes), 0, 'boxes should be greater than zero')

    def test_gleague_players(self):
        pls = self.a.gleague_players(2017)
        self.assertGreaterEqual(len(pls), 0, 'g-league players should be greater than zero')



if __name__=='__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main()
