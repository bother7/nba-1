from collections import defaultdict
import copy
import datetime
from datetime import date
from datetime import timedelta
import logging

try:
    import cPickle as pickle

except:
    import pickle

from nba.agents.agent import NBAAgent
from nba.scrapers.nbacom import NBAComScraper
from nba.parsers.nbacom import NBAComParser


class NBAComAgent(NBAAgent):
    '''
    Performs script-like tasks using NBA.com API
    Intended to replace standalone scripts so can use common API and tools

    Examples:
        a = NBAComAgent()
        gamelogs = a.current_season_player_gamelogs('2015-16')
        site = a.website(webdir='/var/www/nbadata')

    '''

    def __init__(self, db=True, safe=True):
        NBAAgent.__init__(self, db=db, safe=safe)
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.scraper = NBAComScraper()
        self.parser = NBAComParser()

    def cs_player_gamelogs(self, season, date_from=None, date_to=None):
        '''
        Fetches player_gamelogs and updates cs_player_gamelogs table

        Arguments:
             season (str): in YYYY-YY format (2015-16)

        Returns:
             players (list): player dictionary of stats + dfs points
        '''

        new_gamelogs = []
        exclude_keys = ['VIDEO_AVAILABLE', 'TEAM_NAME']

        # step one: figure out the date filter
        # postgres will return object unless use to_char function
        # then need to convert it to datetime object for comparison
        if self.nbadb:
            q = """SELECT to_char(max(game_date), 'YYYYMMDD') from stats.cs_player_gamelogs"""
            last_gamedate = self.nbadb.select_scalar(q)
            last_gamedate = datetime.datetime.strptime(last_gamedate, '%Y%m%d')

        else:
            last_gamedate = datetime.datetime.today() - datetime.timedelta(days=7)

        # step two: get player gamelogs from nba.com
        # game_date is in %Y-%m-%d format
        # don't want partial updates - that is get game from noon when you call it at 5:00 p.m
        all_gamelogs = self.parser.season_gamelogs(self.scraper.season_gamelogs(season, 'P'), 'P')
        today = datetime.datetime.strftime(date.today(), '%Y-%m-%d')
        all_gamelogs = [gamelog for gamelog in all_gamelogs if not gamelog.get('GAME_DATE') == today]

        # step three: filter all_gamelogs by date, only want those newer than latest gamelog in table
        # have to convert to datetime object for comparison
        # TODO: can possibly use upsert feature in postgres 9.5, make last_gamedate <= instead of <
        for gl in all_gamelogs:
            if last_gamedate < datetime.datetime.strptime(gl['GAME_DATE'], '%Y-%m-%d'):
                player = {k.lower().strip(): v for k,v in gl.iteritems() if not k in exclude_keys}
                player['dk_points'] = self.dfs.dk_points(player)
                player['fd_points'] = self.dfs.fd_points(player)

                # change wl (char) to is_win (boolean)
                if player.get('wl', None) == 'W':
                    player['is_win'] = True
                    player.pop('wl')
                else:
                    player['is_win'] = False
                    player.pop('wl')

                # change team_abbreviation to team_code
                if player.get('team_abbreviation', None):
                    player['team_code'] = player['team_abbreviation']
                    player.pop('team_abbreviation')
                else:
                    player.pop('team_abbreviation')
                    
                new_gamelogs.append(player)

            else:
                logging.debug('game is already in db: {0}'.format(gl['GAME_DATE']))

        # step four: backup table
        table_name = 'stats.cs_player_gamelogs'
        if self.safe:
            self.nbadb.postgres_backup_table(self.nbadb.database, table_name)
    
        if self.nbadb:
            # step five: update table
            if len(new_gamelogs) > 0:
                self.nbadb.insert_dicts(new_gamelogs, table_name)

            # step six: add in missing positions
            sql = """UPDATE stats.cs_player_gamelogs
                    SET position_group=subquery.position_group, primary_position=subquery.primary_position
                    FROM (SELECT nbacom_player_id as player_id, position_group, primary_position FROM stats.players) AS subquery
                    WHERE (stats.cs_player_gamelogs.position_group IS NULL OR stats.cs_player_gamelogs.primary_position IS NULL) AND stats.cs_player_gamelogs.player_id=subquery.player_id;
                  """
            self.nbadb.update(sql)

            # step seven: add in team_ids
            sql = """UPDATE stats.cs_player_gamelogs
                    SET team_id=subquery.team_id
                    FROM (SELECT nbacom_team_id as team_id, team_code FROM stats.teams) AS subquery
                    WHERE stats.cs_player_gamelogs.team_id IS NULL AND stats.cs_player_gamelogs.team_code=subquery.team_code;
                  """
            self.nbadb.update(sql)

        return new_gamelogs

    def cs_playerstats(self, season, date_from=None, date_to=None):
        '''
        Fetches cs_player_stats and updates database table

        Arguments:
             season (str): in YYYY-YY format (2015-16)
             date_from (str): in %Y-%m-%d format, default beginning of season
             date_from (str): in %Y-%m-%d format, default yesterday

        Returns:
             player_stats (list): player dictionary of basic and advanced stats
        '''

        if not date_from:
            date_from = self.nbas.season_start(season)

        if not date_to:
            date_to = datetime.datetime.strftime(datetime.datetime.today() - timedelta(1), '%Y-%m-%d')

        ps_base = self.parser.playerstats(self.scraper.playerstats(season, DateFrom=date_from, DateTo=date_to))
        ps_advanced = self.parser.playerstats(self.scraper.playerstats(season, DateFrom=date_from, DateTo=date_to, MeasureType='Advanced'))

        return ps_base, ps_advanced

    def cs_team_gamelogs(self, season, date_from=None, date_to=None):
        '''
        Fetches team_gamelogs and updates cs_team_gamelogs table

        Arguments:
             season (str): in YYYY-YY format (2015-16)

        Returns:
             team_gl (list): player dictionary of stats
        '''

        exclude = ['matchup', 'season_id', 'team_name', 'video_available', 'wl']
        team_gl = []
        today = datetime.datetime.strftime(date.today(), '%Y-%m-%d')

        # figure out the date filter
        # postgres will return object unless use to_char function
        # then need to convert it to datetime object for comparison
        if self.nbadb:
            q = """SELECT to_char(max(game_date), 'YYYYMMDD') from stats.cs_team_gamelogs"""
            last_gamedate = self.nbadb.select_scalar(q)
            last_gamedate = datetime.datetime.strptime(last_gamedate, '%Y%m%d')

        else:
            last_gamedate = datetime.datetime.today() - datetime.timedelta(days=7)

        # filter all_gamelogs by date, only want those newer than latest gamelog in table but don't want today's gamelogs
        # have to convert to datetime object for comparison
        for gl in self.parser.season_gamelogs(self.scraper.season_gamelogs(season='2015-16', player_or_team='T'), 'T'):

            if gl.get('GAME_DATE') == today:
                continue

            elif last_gamedate < datetime.datetime.strptime(gl.get('GAME_DATE'), '%Y-%m-%d'):
                fixed = {k.lower():v for k,v in gl.iteritems() if not k in exclude}
                fixed['team_code'] = fixed['team_abbreviation']
                fixed.pop('team_abbreviation')
                fixed['minutes'] = fixed['min']
                fixed.pop('min')
                team_gl.append(fixed)

            else:
                logging.debug('game skipped: {0}'.format(gl.get('game_date')))

        if self.nbadb:

             # step four: backup table
            table_name = 'stats.cs_team_gamelogs'
            if self.safe:
                self.nbadb.postgres_backup_table(self.nbadb.database, table_name)

            # step five: update table
            if len(team_gl) > 0:
                self.nbadb.insert_dicts(team_gl, table_name)

        return team_gl

    def cs_team_stats(self, season, date_from=None, date_to=None):
        '''
        Fetches leaguedashteamstats and updates cs_leaguedashteamstats table

        Arguments:
             season (str): in YYYY-YY format (2015-16)
             date_from (str): in %Y-%m-%d format, default beginning of season
             date_from (str): in %Y-%m-%d format, default yesterday

        Returns:
             teamstats (list): team dictionary of basic and advanced stats
        '''

        if not date_from:
            date_from = self.nbas.season_start(season)

        if not date_to:
            date_to = datetime.datetime.strftime(datetime.datetime.today() - timedelta(1), '%Y-%m-%d')

        ldts_base = self.parser.teamstats(self.scraper.teamstats(season, DateFrom=date_from, DateTo=date_to))
        ldts_advanced = self.parser.teamstats(self.scraper.teamstats(season, DateFrom=date_from, DateTo=date_to, MeasureType='Advanced'))

        return ldts_base, ldts_advanced

    def players_to_add(self):
        '''
        TODO: Adapt to postgres
        Purpose is to compare current_season_gamelogs and players tables to see if missing players in latter
        '''

        sql = '''
            SELECT  DISTINCT player_id, player_name
            FROM    current_season_player_gamelogs AS c
            WHERE   NOT EXISTS
                    (
                    SELECT  1
                    FROM    players p
                    WHERE   p.person_id = c.player_id
                    )
        '''

        cursor = self.conn.cursor()

        try:
            cursor.execute(sql)
            return cursor.fetchall()

        except Exception as e:
            logging.error('sql statement failed: {0}'.format(sql))
            return None

        finally:
            cursor.close()

    def scoreboards(self, season_start, season_end, pkl_fname=None):
        '''
        Downloads and parses range of scoreboards, optionally saves to pickle file
        '''
        scoreboards = []

        for day in reversed(self.date_list(season_end, season_start)):
            game_date = datetime.datetime.strftime(day, '%Y-%m-%d')
            scoreboard_json = self.nbas.scoreboard(game_date=game_date)
            scoreboard = self.nbap.scoreboard(scoreboard_json, game_date=game_date)
            scoreboards.append(scoreboard)       

        if pkl_fname:
            try:
                with open('/home/sansbacon/scoreboards_20160108.pkl', 'wb') as outfile:
                    pickle.dump(scoreboards, outfile)

            except:
                logging.error('could not save scoreboards to {0}'.format(pkl_fname))

        return scoreboards
        
    def teamgames(self, games):
        '''
        Converts list of games into list in teamgames format, where there are2 teamgames for every game

        Arguments:
            games(list): list of games from nba.com where two teams are in 1 row (visitor, home)

        Returns:
            teamgames(list): list of games in teamgames format, 2 teamgames per game row
            
        Usage:
            # is in format {'game_id', 'visitor_team_id', 'home_team_id', . . . }
            games = NBAPostgres.select_dict('SELECT * FROM games')

            # is in format {'game_id', 'team_id', 'opponent_team_id', 'is_home' . . . }
            teamgames = NBAComAgent.teamgames(games)

        '''

        teamgames = []
        to_drop = ['home_team_code', 'home_team_id', 'visitor_team_code', 'visitor_team_id']

        for game in games:
            tg1 = copy.deepcopy(game)
            tg1['team_code'] = game['home_team_code']
            tg1['team_id'] = game['home_team_id']
            tg1['opponent_team_code'] = game['visitor_team_code']   
            tg1['opponent_team_id'] = game['visitor_team_id']
            tg1['is_home'] = True

            teamgames.append({k:v for k,v in tg1.iteritems() if not k in to_drop})

            tg2 = copy.deepcopy(game)
            tg2['team_code'] = game['visitor_team_code']
            tg2['team_id'] = game['visitor_team_id']
            tg2['opponent_team_code'] = game['home_team_code']
            tg2['opponent_team_id'] = game['home_team_id']
            tg2['is_home'] = False

            teamgames.append({k:v for k,v in tg2.iteritems() if not k in to_drop})

        return teamgames

if __name__ == '__main__':
    pass