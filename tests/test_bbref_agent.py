from __future__ import absolute_import, print_function

import datetime
import logging
import unittest

from nba.agents.bbref import BBRefAgent


class BBRefAgent_test(unittest.TestCase):

    def setUp(self):
        self.a = BBRefAgent()


    def test_match_gamelog_player(self):
        gamelog_player = {'PLAYER_ID': 2544, 'PLAYER_NAME': 'LeBron James',
                          'TEAM_ABBREVIATION': 'CLE', 'TEAM_NAME': 'Cleveland Cavaliers'}
        bbref_player = self.a.match_gamelog_player(gamelog_player)
        self.assertEqual(gamelog_player['PLAYER_NAME'], bbref_player['source_player_name'])

    def test_match_nbacom_player(self):
        nbacom_player = {'birthdate': datetime.datetime(1993, 8, 1, 0, 0), 'country': 'Spain',
                        'display_first_last': 'Alex Abrines', 'draft_number': 32, 'draft_round': 2, 'draft_year': 2013,
                        'first_name': 'Alex', 'from_year': 2016, 'height': 42, 'jersey': 8,
                        'last_affiliation': 'Spain/Spain', 'last_name': 'Abrines', 'nbacom_player_id': 203518,
                        'nbacom_position': 'G', 'school': '', 'weight': 190}
        bbref_player = self.a.match_nbacom_player(nbacom_player)
        self.assertEqual(nbacom_player['display_first_last'], bbref_player['source_player_name'])

    def test_bbref_position(self):
        '''
        nbacom_player = {'birthdate': datetime.datetime(1993, 8, 1, 0, 0), 'country': 'Spain',
                         'display_first_last': 'Nigel Hayes', 'draft_number': 32, 'draft_round': 2, 'draft_year': 2013,
                         'first_name': 'Nigel', 'from_year': 2016, 'height': 80, 'jersey': 8,
                         'last_affiliation': 'Spain/Spain', 'last_name': 'Hayes', 'nbacom_player_id': 203518,
                         'nbacom_position': 'G', 'school': '', 'weight': 190}
        bbref_player = self.a.match_nbacom_player(nbacom_player)
        if bbref_player['source_player_position'] == 'Guard':

        self.assertEqual(nbacom_player['display_first_last'], bbref_player['source_player_name'])

        nbacom_player = {'birthdate': datetime.datetime(1993, 8, 1, 0, 0), 'country': 'Spain',
                         'display_first_last': 'Nigel Hayes', 'draft_number': 32, 'draft_round': 2, 'draft_year': 2013,
                         'first_name': 'Nigel', 'from_year': 2016, 'height': 73, 'jersey': 8,
                         'last_affiliation': 'Spain/Spain', 'last_name': 'Hayes', 'nbacom_player_id': 203518,
                         'nbacom_position': 'G', 'school': '', 'weight': 190}
        bbref_player = self.a.match_nbacom_player(nbacom_player)
        if bbref_player['source_player_position'] == 'Guard':

        self.assertEqual(nbacom_player['display_first_last'], bbref_player['source_player_name'])
        '''


if __name__=='__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main()
