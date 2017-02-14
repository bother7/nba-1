import copy
import datetime as dt
import logging
import re

from nba.db.pgsql import NBAPostgres
from nba.pipelines.fantasylabs import salaries_table
from nba.players import NBAPlayers


class FantasyLabsNBAPg(NBAPostgres):
    '''
    FantasyLabs-specific routines for inserting data into tables
    '''

    def __init__(self, username, password, database = 'nbadb',
                 host = 'localhost', port = 5432):
        '''

        '''
        NBAPostgres.__init__(self, user=username, password=password,
                             database=database)
        logging.getLogger(__name__).addHandler(logging.NullHandler())

    def _convert(self, s0):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s0)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def _nbacom_player_id(self, site_player_id):
        '''
        Returns nbacom_player_id for site_player_id

        Args:
            site_player_id (int): id used by site such as draftkings or fantasylabs

        Returns:
            nbacom_player_id (int): id used by nba.com

        '''

        if not self.player_xref:
            self.player_xref = self.nbaplayers.player_xref('fl')

        return self.player_xref.get(site_player_id)

    def insert_models(self, models):
        '''
        TODO: code this out
        '''
        if models:
            self.insert_dicts(models, 'dfs.fantasylabs_models')

    def insert_salaries(self, sals):
        '''
        Insert list of player salaries into dfs.salaries table

        Args:
            players (list): list of player dictionaries with salaries
        '''
        q = "SELECT DISTINCT source_player_id, nbacom_player_id FROM dfs_salaries WHERE source = 'fantasylabs'"
        allp = {sal.get('source_player_id'): sal.get('nbacom_player_id') for
            sal in self.select_dict(q)}
        self.insert_dicts(salaries_table(sals, allp), 'dfs_salaries')

    def preprocess_games(self, games):
        '''
        Returns games ready for insert into dfs tables

        Args:
            games (list): list of game dictionaries

        Returns:
            fixed_games (list): list of game dictionaries ready for insert into dfs.salaries

        '''

        fixed_games = []
        wanted_keys = ['EventId', 'EventDateTime', 'EventDate', 'HomeTeamShort', 'VisitorTeamShort',
                       'ProjHomeScore', 'ProjVisitorScore']

        # get list of games from stats.games
        sql = '''SELECT game_id, gamecode FROM stats.games'''

        try:
            nbacom_games = {g['gamecode']: g['game_id'] for g in self.select_dict(sql)}
        except:
            nbacom_games = {}

        if games:
            for game in games:
                fixed_game = {self._convert(k):v for k,v in game.iteritems() if k in wanted_keys}
                away = game['VisitorTeamShort']
                home = game['HomeTeamShort']
                event_date = game.get('EventDate')
                d, t = event_date.split('T')

                if d:
                    d = dt.datetime.strftime(dt.datetime.strptime(d, '%Y-%m-%d'), '%Y%m%d')

                gamecode = '{0}/{1}{2}'.format(d, away, home)
                fixed_game['gamecode'] = gamecode
                fixed_game['nbacom_game_id'] = nbacom_games.get(gamecode)
                fixed_games.append(fixed_game)

        return fixed_games

if __name__ == '__main__':
    pass