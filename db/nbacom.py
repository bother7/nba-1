from __future__ import print_function

import datetime
import logging

from nba.db.pgsql import NBAPostgres
from nba.dfs import dk_points, fd_points


class NBAComPg(NBAPostgres):
    '''
    Usage:
        from nba.agents.nbacom import NBAComAgent
        from nba.db.nbacom import NBAComPg

        nbap = NBAComPg(username=un, password=pw, database=db)
        a = NBAComAgent()
        tgl = a.cs_team_gamelogs('2016-17')
        nbap.insert_team_gamelogs(tgl, season=2017, nbacom_season_id=22016, table_name)
    '''

    def __init__(self, username, password, database, table_names=None):
        '''
        TODO: add table_names as property
        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        NBAPostgres.__init__(self, username, password, database)
        if table_names:
            self.table_names = table_names
        else:
            self.table_names = {'pgl': None, 'tgl': None, 'pl': None}

    def insert_boxscores(self, player_boxscores, team_boxscores, player_table_name, team_table_name):

        omit = ['COMMENT', 'FG3_PCT', 'FG_PCT', 'FT_PCT', 'TEAM_CITY', 'TEAM_NAME']
        cleaned_players = []
        cleaned_teams = []

        for player in player_boxscores:
            clean_player = {k.lower():v for k,v in player.iteritems() if k not in omit}
            clean_player['tov'] = clean_player['to']
            clean_player.pop('to')
            clean_player.pop('team_abbreviation')
            cleaned_players.append(clean_player)

        for team in team_boxscores:
            clean_team = {k.lower():v for k,v in team.iteritems() if k not in omit}
            clean_team['tov'] = clean_team['to']
            clean_team.pop('to')
            clean_team['team_code'] = clean_team['team_abbreviation']
            clean_team.pop('team_abbreviation')

            # fix minutes, are in mm:ss format
            minutes, sec = clean_team['min'].split(':')
            clean_team['min'] = minutes

            cleaned_teams.append(clean_team)

        self.insert_dicts(cleaned_players, player_table_name)
        self.insert_dicts(cleaned_teams, team_table_name)

        return cleaned_players, cleaned_teams

    def insert_games(self, games, table_name):
        '''

        Args:
            games(list): of dict
            table_name(str):

        Returns:
            status
        '''
        return self.insert_dicts(games, table_name)

    def insert_player_gamelogs(self, stats, table_name, check_date=True):
        '''

        Arguments:
            stats(list): list of dictionaries
            table_name(str): examples -- 'stats.cs_team_gamelogs', 'stats.team_gamelogs'

        Returns:
            cleaned_items(list)

        '''

        cleaned_items = []
        omit = ['VIDEO_AVAILABLE', 'TEAM_NAME', 'MATCHUP']

        if check_date:
        # figure out the date filter
        # postgres will return object unless use to_char function
        # then need to convert it to datetime object for comparison
        q = """SELECT to_char(max(game_date), 'YYYYMMDD') from stats.player_gamelogs"""
        last_gamedate = datetime.datetime.strptime(self.select_scalar(q), '%Y%m%d') #- datetime.timedelta(days=7)

        # filter all_gamelogs by date, only want those newer than latest gamelog in table
        # have to convert to datetime object for comparison
        today = datetime.datetime.strftime(datetime.datetime.today(), '%Y-%m-%d')

        for item in stats:

            if item.get('GAME_DATE') == today:
                continue

            elif last_gamedate < datetime.datetime.strptime(item['GAME_DATE'], '%Y-%m-%d'):
                cleaned_item = {k.lower().strip(): v for k,v in item.iteritems() if k.upper() not in omit}
                cleaned_item['dk_points'] = dk_points(item)
                cleaned_item['fd_points'] = fd_points(item)

                # convert wl to is_win (boolean)
                if cleaned_item.get('wl') == 'W':
                    cleaned_item['is_win'] = True

                else:
                    cleaned_item['is_win'] = False

                cleaned_item.pop('wl', None)

                # change team_abbreviation to team_code
                if 'team_abbreviation' in cleaned_item:
                    cleaned_item['team_code'] = cleaned_item['team_abbreviation']
                    cleaned_item.pop('team_abbreviation')

                # cleanup season_id
                if 'season_id' in cleaned_item:
                    cleaned_item['nbacom_season_id'] = int(cleaned_item['season_id'])
                    cleaned_item['season'] = cleaned_item['nbacom_season_id'] - 20000 + 1
                    cleaned_item.pop('season_id')

                cleaned_items.append(cleaned_item)

            else:
                logging.debug('game is already in db: {0}'.format(item.get('GAME_DATE')))

        # add cleaned items to database
        if cleaned_items:
            self.insert_dicts(cleaned_items, table_name)

        return cleaned_items

    def insert_playerstats_daily(self, playerstats, season, nbacom_season_id, as_of, table_name):
        '''
        Cleans merged list of player base + advanced stats

        Arguments:
            table_name(str): examples -- 'stats.cs_playerstats', 'stats.playerstats'
            playerstats(list): list of player dictionaries

        Returns:

        '''

        # clean data for insertion
        omit = ['CFID', 'CFPARAMS', 'COMMENT']

        cleaned_players = []

        for player in playerstats:
            clean_player = {k.lower(): v for k, v in player.iteritems() if k not in omit}

            if 'to' in clean_player:
                clean_player['tov'] = clean_player['to']
                clean_player.pop('to', None)

            if 'team_abbreviation' in clean_player:
                clean_player['team_code'] = clean_player['team_abbreviation']
                clean_player.pop('team_abbreviation', None)

            clean_player['as_of'] = as_of
            clean_player['season'] = season
            clean_player['nbacom_season_id'] = nbacom_season_id
            cleaned_players.append(clean_player)

        if cleaned_players:
            self.insert_dicts(cleaned_players, table_name)

        return cleaned_players

    def insert_team_gamelogs(self, stats, season, nbacom_season_id, table_name=None):
        '''
        Cleans merged list of team gamelogs base + advanced
        Arguments:
            stats(list): list of dictionaries
            table_name(str): examples -- 'stats.cs_team_gamelogs', 'stats.team_gamelogs'
        Returns:
            cleaned_items(list)
        '''
        if not table_name:
            table_name = self.table_name.get('tgl')

        omit = ['matchup', 'season_id', 'team_name', 'video_available', 'wl']
        cleaned_items = []

        # figure out the date filter
        # postgres will return object unless use to_char function
        # then need to convert it to datetime object for comparison
        today = datetime.datetime.strftime(datetime.datetime.today(), '%Y-%m-%d')
        q = """SELECT to_char(max(game_date), 'YYYYMMDD') from stats.cs_team_gamelogs"""
        last_gamedate = self.select_scalar(q)
        logging.debug(today, last_gamedate)

        # filter all_gamelogs by date, only want those newer than latest gamelog in table but don't want today's gamelogs
        # have to convert to datetime object for comparison
        for item in stats:
            game_date = item.get('GAME_DATE')

            if game_date == today:
                continue

            elif datetime.datetime.strptime(last_gamedate, '%Y%m%d') < datetime.datetime.strptime(item.get('GAME_DATE'), '%Y-%m-%d'):
                cleaned_item = {k.lower(): v for k,v in item.iteritems() if k.lower() not in omit}
                if cleaned_item.get('team_abbreviation'):
                    cleaned_item['team_code'] = cleaned_item['team_abbreviation']
                    cleaned_item.pop('team_abbreviation', None)
                if cleaned_item.get('min'):
                    cleaned_item['minutes'] = cleaned_item['min']
                    cleaned_item.pop('min', None)
                cleaned_item['season'] = season
                cleaned_item['nbacom_season_id'] = nbacom_season_id
                cleaned_items.append(cleaned_item)
            else:
                logging.debug('game skipped: {0}'.format(item.get('GAME_DATE')))

        if cleaned_items:
            self.insert_dicts(cleaned_items, table_name)

        return cleaned_items

    def insert_teamstats_daily(self, stats, table_name, as_of):
        '''
        Cleans merged list of team base + advanced stats

        Arguments:
            stats(list): list of dictionaries
            table_name(str): examples -- 'stats.cs_teamstats', 'stats.teamstats'
            as_of(str): in YYYY-MM-DD format
        Returns:
            cleaned_items(list): list of cleaned team dictionaries
        '''
        omit = ['CFID', 'CFPARAMS', 'COMMENT', 'TEAM_CITY']
        cleaned_items = [{k.lower(): v for k,v in item.iteritems() if k not in omit} for item in stats]
        for idx, item in enumerate(cleaned_items):
            cleaned_items[idx]['as_of'] = as_of
        self.insert_dicts(cleaned_items, table_name)
        return cleaned_items

    def update_players(self, players, table_name=None):
        '''
        Inserts new players into players table
        Args:
            players(list): of player dict
            table_name(str): full name of table, like stats.players
        Returns:
            None
        '''
        if not table_name:
            table_name = self.table_names.get('pl')
        self.insert_dicts(players, table_name)

    def update_positions(self, table_name=None):
        '''
        Updates gamelogs table with positions from players table
        '''
        if not table_name:
            table_name = self.table_name.get('pgl')
        sql = """UPDATE {0}
                SET position_group=subquery.position_group, primary_position=subquery.primary_position
                FROM (SELECT nbacom_player_id as player_id, position_group, primary_position FROM stats.players) AS subquery
                WHERE ({0}.position_group IS NULL OR {0}.primary_position IS NULL) AND {0}.player_id=subquery.player_id;
              """
        self.update(sql.format(table_name))

    def update_teamids(self, table_name=None):
        '''
        Updates gamelogs table with teamids
        '''
        if not table_name:
            table_name = self.table_name.get('pgl')
        sql = """UPDATE {0}
                SET team_id=subquery.team_id
                FROM (SELECT nbacom_team_id as team_id, team_code FROM stats.teams) AS subquery
                WHERE {0}.team_id IS NULL AND {0}.team_code=subquery.team_code;
              """
        self.update(sql.format(table_name))

if __name__ == '__main__':
    pass
