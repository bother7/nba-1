import copy
import datetime as dt
import logging
import re

from nba.db.pgsql import NBAPostgres
from nba.players import NBAPlayers


class FantasyLabsNBAPg(NBAPostgres):
    '''
    FantasyLabs-specific routines for inserting data into tables
    '''

    def __init__(self):
        NBAPostgres.__init__(self)
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.nbaplayers = NBAPlayers(db=True)
        self.player_xref = {}

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

    def insert_salaries(self, players):
        '''
        Insert list of player salaries into dfs.salaries table

        Args:
            players (list): list of player dictionaries with salaries

        '''

        if players:
            self.insert_dicts(players, 'dfs.salaries')

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

    def preprocess_salaries(self, players):
        '''
        Returns players ready for insert into dfs tables

        Args:
            players (list): list of player dictionaries

        Returns:
            fixed_players (list): list of player dictionaries ready for insert into dfs.salaries

        '''

        fixed_players = []

        if players:
            for player in players:

                fixed_player = copy.deepcopy(player)
                site_player_id = int(player.get('PlayerId'))
                nbacom_player_id = self._nbacom_player_id(site_player_id)
                fixed_player['nbacom_player_id'] = nbacom_player_id
                fixed_player['source'] = 'fl'
                fixed_player['dfs_site'] = 'dk'
                fixed_player['salary'] = player.get('Salary')
                fixed_player['site_position'] = player.get('FirstPosition')
                fixed_player['source_player_name'] = player.get('Player_Name')
                fixed_player['source_player_id'] = player.get('PlayerId')
                fixed_player['nbacom_season_id'] = 22015
                fixed_player['season'] = 2016
                fixed_player['game_date'] = player.get('gamedate')
                fixed_players.append(fixed_player)

            wanted_keys = ['game_date', 'season', 'nbacom_season_id', 'source_player_id', 'source_player_name', 'source', 'dfs_site',
                           'salary', 'site_position', 'nbacom_player_id']

            return [{k.lower(): v for k,v in player.iteritems() if k in wanted_keys} for player in fixed_players]

        else:
            return fixed_players

if __name__ == '__main__':
    pass