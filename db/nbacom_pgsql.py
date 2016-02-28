import datetime
import logging

from nba.db import pgsql
from daily_fantasy import dk_points, fd_points

class NBAComPg(pgsql.NBAPostgres):
    '''

    '''


    def __init__(self, **kwargs):

        logging.getLogger(__name__).addHandler(logging.NullHandler())

        # see http://stackoverflow.com/questions/8134444
        pgsql.NBAPostgres.__init__(self, **kwargs)


    def insert_boxscores(self, player_boxscores, team_boxscores, player_table_name, team_table_name):

        omit = ['COMMENT', 'FG3_PCT', 'FG_PCT', 'FT_PCT', 'TEAM_CITY', 'TEAM_NAME']
        cleaned_players = []
        cleaned_teams = []

        for player in player_boxscores:
            clean_player = {k.lower():v for k,v in player.iteritems() if not k in omit}
            clean_player['tov'] = clean_player['to']
            clean_player.pop('to')
            clean_player.pop('team_abbreviation')
            cleaned_players.append(clean_player)

        for team in team_boxscores:
            clean_team = {k.lower():v for k,v in team.iteritems() if not k in omit}
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

    def insert_games(self, games):
        '''
        TODO: code this out
        '''
        
        for game in games:
            pass

    def insert_player_gamelogs(self, stats, table_name):
        '''
        Cleans merged list of team gamelogs base + advanced

        Arguments:
            stats(list): list of dictionaries
            table_name(str): examples -- 'stats.cs_team_gamelogs', 'stats.team_gamelogs'


        Returns:
            cleaned_items(list)

        '''

        cleaned_items = []
        omit = ['VIDEO_AVAILABLE', 'TEAM_NAME']

        # figure out the date filter
        # postgres will return object unless use to_char function
        # then need to convert it to datetime object for comparison
        q = """SELECT to_char(max(game_date), 'YYYYMMDD') from stats.cs_player_gamelogs"""
        last_gamedate = datetime.datetime.strptime(self.select_scalar(q), '%Y%m%d')

        # filter all_gamelogs by date, only want those newer than latest gamelog in table
        # have to convert to datetime object for comparison
        today = datetime.datetime.strftime(datetime.datetime.today(), '%Y-%m-%d')

        for item in stats:

            if item.get('GAME_DATE') == today:
                continue

            elif last_gamedate < datetime.datetime.strptime(item['GAME_DATE'], '%Y-%m-%d'):
                cleaned_item = {k.lower().strip(): v for k,v in item.iteritems() if not k in omit}
                cleaned_item['dk_points'] = dk_points(item)
                cleaned_item['fd_points'] = fd_points(item)

                # change wl (char) to is_win (boolean)
                if item.get('wl', None) == 'W':
                    item['is_win'] = True
                    item.pop('wl')
                else:
                    item['is_win'] = False
                    item.pop('wl')

                # change team_abbreviation to team_code
                if item.get('team_abbreviation', None):
                    item['team_code'] = item['team_abbreviation']
                    item.pop('team_abbreviation')
                else:
                    item.pop('team_abbreviation')

                # don't need season_id for cs tables
                item.pop('season_id')

                cleaned_items.append(cleaned_item)

            else:
                logging.debug('game is already in db: {0}'.format(item.get('GAME_DATE')))

        ## add cleaned items to database
        self.insert_dicts(cleaned_items, table_name)

        return cleaned_items

    def insert_playerstats(self, playerstats, table_name, game_date):
        '''
        Cleans merged list of player base + advanced stats
        
        Arguments:
            table_name(str): examples -- 'stats.cs_playerstats', 'stats.playerstats'
            playerstats(list): list of player dictionaries

        Returns:
        
        '''

        # clean data for insertion
        omit = ['CFID', 'CFPARAMS', 'COMMENT', 'FG3_PCT', 'FG_PCT', 'FT_PCT', 'FGA_PG', 'FGM_PG', 'FTA_PG' 'TEAM_CITY', 'TEAM_NAME']
        cleaned_players = []

        for player in playerstats:
            clean_player = {k.lower():v for k,v in player.iteritems() if not k in omit}

            if clean_player.get('to'):
                clean_player['tov'] = clean_player['to']
                clean_player.pop('to')

            if clean_player.get('team_abbreviation'):
                clean_player['team_code'] = clean_player['team_abbreviation']
                clean_player.pop('team_abbreviation')

            clean_player['game_date'] = game_date
            cleaned_players.append(clean_player)

        self.insert_dicts(cleaned_players, table_name)

        return cleaned_players

    def insert_team_gamelogs(self, stats, table_name):
        '''
        Cleans merged list of team gamelogs base + advanced

        Arguments:
            stats(list): list of dictionaries
            table_name(str): examples -- 'stats.cs_team_gamelogs', 'stats.team_gamelogs'


        Returns:
            cleaned_items(list)

        '''

        # clean data for insertion
        omit = ['matchup', 'season_id', 'team_name', 'video_available', 'wl']
        cleaned_items = []

        # figure out the date filter
        # postgres will return object unless use to_char function
        # then need to convert it to datetime object for comparison
        today = datetime.datetime.strftime(datetime.datetime.today(), '%Y-%m-%d')
        q = """SELECT to_char(max(game_date), 'YYYYMMDD') from stats.cs_team_gamelogs"""
        last_gamedate = datetime.datetime.strptime(self.select_scalar(q), '%Y%m%d')

        # filter all_gamelogs by date, only want those newer than latest gamelog in table but don't want today's gamelogs
        # have to convert to datetime object for comparison
        for item in stats:

            if item.get('GAME_DATE') == today:
                continue

            elif last_gamedate < datetime.datetime.strptime(item.get('GAME_DATE'), '%Y-%m-%d'):
                cleaned_item = {k.lower():v for k,v in item.iteritems() if not k.lower() in omit}

                if cleaned_item.get('team_abbreviation'):
                    cleaned_item['team_code'] = cleaned_item['team_abbreviation']
                    cleaned_item.pop('team_abbreviation')

                if cleaned_item.get('min'):
                    cleaned_item['minutes'] = cleaned_item['min']
                    cleaned_item.pop('min')

                cleaned_items.append(cleaned_item)

            else:
                logging.debug('game skipped: {0}'.format(item.get('GAME_DATE')))

        self.insert_dicts(cleaned_items, table_name)

        return cleaned_items

    def insert_teamstats(self, stats, table_name, game_date):
        '''
        Cleans merged list of team base + advanced stats

        Arguments:
            stats(list): list of dictionaries
            table_name(str): examples -- 'stats.cs_teamstats', 'stats.teamstats'
            game_date(str): date through which stats are current (usually yesterday)

        Returns:
            cleaned_items(list): list of cleaned team dictionaries
        '''

        # clean data for insertion
        omit = ['CFID', 'CFPARAMS', 'COMMENT', 'FG3_PCT', 'FG_PCT', 'FT_PCT', 'FGA_PG', 'FGM_PG', 'FTA_PG' 'TEAM_CITY', 'TEAM_NAME']
        cleaned_items = []

        for item in stats:
            clean_item = {k.lower():v for k,v in item.iteritems() if not k in omit}

            if clean_item.get('to'):
                clean_item['tov'] = clean_item['to']
                clean_item.pop('to')

            if clean_item.get('team_abbreviation'):
                clean_item['team_code'] = clean_item['team_abbreviation']
                clean_item.pop('team_abbreviation')

            clean_item['game_date'] = game_date
            cleaned_items.append(clean_item)

        self.insert_dicts(cleaned_items, table_name)

        return cleaned_items

    def update_positions(self, table_name):
        '''
        Updates gamelogs table with positions from players table
        '''
        sql = """UPDATE {0}
                SET position_group=subquery.position_group, primary_position=subquery.primary_position
                FROM (SELECT nbacom_player_id as player_id, position_group, primary_position FROM stats.players) AS subquery
                WHERE ({0}.position_group IS NULL OR {0}.primary_position IS NULL) AND {0}.player_id=subquery.player_id;
              """

        self.update(sql.format(table_name))

    def update_teamids(self, table_name):
        '''
        Updates gamelogs table with teamids
        '''

        sql = """UPDATE {0}
                SET team_id=subquery.team_id
                FROM (SELECT nbacom_team_id as team_id, team_code FROM stats.teams) AS subquery
                WHERE {0}.team_id IS NULL AND {0}.team_code=subquery.team_code;
              """

        self.update(sql.format(table_name))

if __name__ == '__main__':
    pass