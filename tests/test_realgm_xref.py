from __future__ import absolute_import, print_function

import logging
import os
import sys
import unittest

from configparser import ConfigParser

from nba.db.pgsql import NBAPostgres
from nba.player.realgmxref import *



class realgm_xref_test(unittest.TestCase):

    def setUp(self):
        config = ConfigParser()
        config.read(os.path.join(os.path.expanduser('~'), '.pgcred'))
        self.db = NBAPostgres(user=config['nbadb']['username'],
                         password=config['nbadb']['password'],
                         database=config['nbadb']['database'])


    def test_xref(self):
        q = """SELECT source, source_player_id, source_player_name
               FROM player_xref
               WHERE source = 'realgm'
               LIMIT 20
        """
        players = self.db.select_dict(q)
        players = nbacom_ids(self.db, players)
        count = 0
        for p in players:
            if p.get('nbacom_player_id', 0) > 0:
                count +=1
        self.assertGreaterEqual(len(players), 0)
        self.assertGreaterEqual(count, 10)
        logging.info('there are {} ids'.format(count))

if __name__=='__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    unittest.main()