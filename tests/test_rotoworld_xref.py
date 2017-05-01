from __future__ import absolute_import, print_function

import logging
import os
import sys
import unittest

from configparser import ConfigParser

from nba.db.pgsql import NBAPostgres
from nba.player.rotoworldxref import update_rotoworld_xref


class Rotoworld_xref_test(unittest.TestCase):


    def setUp(self):
        config = ConfigParser()
        config.read(os.path.join(os.path.expanduser('~'), '.pgcred'))
        self.db = NBAPostgres(user=config['nbadb']['username'],
                         password=config['nbadb']['password'],
                         database=config['nbadb']['database'])


    def test_xref(self):
        '''
        
        Returns:

        '''
        rwp = update_rotoworld_xref(self.db, None)
        self.assertGreaterEqual(len(rwp), 0)
        self.db.insert_dicts(rwp, 'player_xref')


if __name__=='__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    unittest.main()