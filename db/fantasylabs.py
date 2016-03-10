import copy
import logging

from nba.db import pgsql
from nba.players import NBAPlayers

class FantasyLabsNBAPg(pgsql.NBAPostgres):
    '''
    FantasyLabs-specific routines for inserting data into tables
    '''

    def __init__(self, **kwargs):

        # see http://stackoverflow.com/questions/8134444
        pgsql.NBAPostgres.__init__(self, **kwargs)
        self.logger = logging.getLogger(__name__)
        self.nbap = NBAPlayers()
        self.player_xref = {}

    def _nbacom_player_id(self, site_player_id):
        '''
        Returns nbacom_player_id for site_player_id

        Args:
            site_player_id (int): id used by site such as draftkings or fantasylabs

        Returns:
            nbacom_player_id (int): id used by nba.com

        '''

        if not self.player_xref:
            self.player_xref = self.nbap.player_xref('fantasylabs')

        return self.player_xref.get(site_player_id)

    def _preprocess(self, players):
        '''
        Returns players ready for insert into dfs tables

        Args:
            players (list): list of player dictionaries

        Returns:
            fixed_players (list): list of player dictionaries ready for insert into dfs.salaries

        '''

        fixed_players = []

        for player in players:
            fixed_player = copy.deepcopy(player)

            try:
                site_player_id = int(player.get('PlayerId'))
                nbacom_player_id = self._nbacom_player_id(site_player_id)
                fixed_player['nbacom_player_id'] = nbacom_player_id

            except:
                pass

            fixed_player['site'] = 'dk'
            fixed_player['site_position'] = player.get('FirstPosition')
            fixed_player['site_player_name'] = player.get('Player_Name')
            fixed_player['site_player_id'] = player.get('PlayerId')
            fixed_player['nbacom_season_id'] = 22015
            fixed_player['season'] = 2016
            fixed_player['game_date'] = player.get('gamedate')

            fixed_players.append(fixed_player)

        wanted_keys = ['game_date', 'season', 'nbacom_season_id', 'site_player_id', 'site_player_name', 'site', 'Salary', 'site_position', 'nbacom_player_id']
        return [{k.lower(): v for k,v in player.iteritems() if k in wanted_keys} for player in fixed_players]

    def insert_models(self, models):
        '''
        TODO: code this out
        '''
        self.insert_dicts(models, 'dfs.fantasylabs_models')

    def insert_salaries(self, players):
        '''
        Insert list of player salaries into dfs.salaries table

        Args:
            players (list): list of player dictionaries with salaries

        '''

        self.insert_dicts(self._preprocess(players), 'dfs.salaries')

if __name__ == '__main__':
    pass
