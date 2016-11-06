import copy
import datetime as dt
import logging

try:
    import cPickle as pickle

except:
    import pickle

from nba.agents.agent import NBAAgent
from nba.db.nbacom import NBAComPg
from nba.scrapers.nbacom import NBAComScraper
from nba.parsers.nbacom import NBAComParser
from nba.seasons import NBASeasons
from nba.dates import *


class NBAComAgent(NBAAgent):
    '''
    Performs script-like tasks using NBA.com API
    Intended to replace standalone scripts so can use common API and tools

    Examples:
        a = NBAComAgent()
        gamelogs = a.cs_player_gamelogs('2015-16')

    '''

    def __init__(self, db=True, safe=True):
        '''

        Args:
            db (bool): compose NBAComPg object as self.nbadb
            safe (bool): create backups of tables prior to inserts

        '''

        NBAAgent.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.scraper = NBAComScraper()
        self.parser = NBAComParser()
        self.safe = safe
        self.nbas = NBASeasons()

        if db:
            self.nbadb = NBAComPg()
        else:
            self.nbadb = None

    def combine_boxscores(self, boxes, advanced_boxes):
        '''
        Combines NBAComScraper.boxscores() and boxscores_advanced()

        Arguments:
            boxscores(list): list of 'base' boxscores
            boxscores(list): list of 'advanced' boxscores

        Returns:
            merged_players (list): base and advanced combined
            merged_teams (list): base and advanced combined

        Examples:
            a = NBAComAgent()
            combined = a.combine_boxscores(boxes, advanced_boxes)

        '''

        merged_players = []
        merged_teams = []

        for gid, box in boxes.iteritems():

            # players and teams are lists of dicts
            players, teams, starterbench = self.parser.boxscore(box)

            # players_adv and teams_adv are lists of dicts
            adv_box = advanced_boxes.get(gid)
            players_adv, teams_adv = self.parser.boxscore_advanced(adv_box)

            # need to transform into dicts
            players_dict = {p['PLAYER_ID']: p for p in players}
            players_adv_dict = {p['PLAYER_ID']: p for p in players_adv}
            teams_dict = {t['TEAM_ID']: t for t in teams}
            teams_adv_dict = {t['TEAM_ID']: t for t in teams_adv}

            # now loop through players
            for pid, player in players_dict.iteritems():
                player_adv = players_adv_dict.get(pid)

                if player_adv:
                    merged_players.append(self.merge_boxes(player, player_adv))

            # now loop through teams
            for tid, team in teams_dict.iteritems():
                team_adv = teams_adv_dict.get(tid)

                if team_adv:
                    merged_teams.append(self.merge_boxes(team, team_adv))

        self.nbadb.insert_boxscores(merged_players, merged_teams)


    def commonallplayers(self, season):
        '''
        Solves problem of players changing teams
        nba.com updates player teams regularly, so i look every day to make sure lists accurate

        Arguments:
            season (str): in YYYY-YY format

        Returns:
            to_insert (list): list of players that needed to be updated

        Examples:
            a = NBAComAgent()
            combined = a.commonallplayers('2015-16')

        '''

        game_date = dt.datetime.today()
        players = self.parser.players(self.scraper.players(season=season, cs_only='1'))

        to_insert = []

        convert = {
            "PERSON_ID": 'nbacom_player_id',
            "DISPLAY_LAST_COMMA_FIRST": '',
            "DISPLAY_FIRST_LAST": 'display_first_last',
            "ROSTERSTATUS": 'rosterstatus',
            "FROM_YEAR": '',
            "TO_YEAR": '',
            "PLAYERCODE": '',
            "TEAM_ID": 'team_id',
            "TEAM_CITY": '',
            "TEAM_NAME": '',
            "TEAM_ABBREVIATION": 'team_code',
            "TEAM_CODE": '',
            "GAMES_PLAYED_FLAG": ''
        }

        for p in players:
            pti = {'game_date': game_date, 'nbacom_season_id': 22015, 'season': 2016}

            for k,v in p.iteritems():
                converted = convert.get(k)
                if converted:
                    pti[converted] = v

            to_insert.append(pti)

        if self.nbadb:
            if to_insert:
                self.nbadb.insert_dicts(to_insert, 'stats.playerteams')

        return to_insert

    def cs_player_gamelogs(self, season, date_from=None, date_to=None):
        '''
        Fetches player_gamelogs and updates cs_player_gamelogs table

        Arguments:
             season (str): in YYYY-YY format (2015-16)

        Returns:
             players (list): player dictionary of stats + dfs points
        '''

        gamelogs = self.parser.season_gamelogs(self.scraper.season_gamelogs(season, 'P'), 'P')

        table_name = 'stats.cs_player_gamelogs'

        if self.nbadb:
            if self.safe:
                self.nbadb.postgres_backup_table(self.nbadb.database, table_name)
    
            gamelogs = self.nbadb.insert_player_gamelogs(gamelogs, table_name)
            self.nbadb.update_positions(table_name)
            self.nbadb.update_teamids(table_name)

        return gamelogs

    def cs_playerstats(self, season, date_from=None, date_to=None):
        '''
        Fetches cs_player_stats and updates database table

        Arguments:
             season (str): in YYYY-YY format (2015-16)
             date_from (str): in %Y-%m-%d format, default beginning of season
             date_from (str): in %Y-%m-%d format, default yesterday

        Returns:
             player_stats (list): player dictionary of basic and advanced stats

        Examples:
            a = NBAComAgent()
            ps = a.cs_playerstats('2015-16')
            ps = a.cs_playerstats(season='2015-16', date_from='2016-03-01', date_to='2016-03-08')

        '''

        # default is to get entire season through yesterday
        yesterday = dt.datetime.strftime(dt.datetime.today() - dt.timedelta(1), '%Y-%m-%d')

        if not date_from:
            date_from = self.nbas.season_start(season)

        if not date_to:
            date_to = yesterday

        ps_base = self.parser.playerstats(self.scraper.playerstats(season, DateFrom=date_from, DateTo=date_to))
        ps_advanced = self.parser.playerstats(self.scraper.playerstats(season, DateFrom=date_from, DateTo=date_to, MeasureType='Advanced'))

        # now need to merge base and advanced
        ps_base = {p['PLAYER_ID']: p for p in ps_base}

        for ps_adv in ps_advanced:
            pid = ps_adv['PLAYER_ID']
            base = ps_base.get(pid)

            if base:
                base.update(ps_adv)
                ps_base[pid] = base       

        return self.nbadb.insert_playerstats(ps_base.values(), table_name='stats.cs_playerstats', game_date=yesterday)

    def cs_team_gamelogs(self, season, date_from=None, date_to=None):
        '''
        Fetches team_gamelogs and updates cs_team_gamelogs table

        Arguments:
             season (str): in YYYY-YY format (2015-16)

        Returns:
             team_gl (list): player dictionary of stats

        Examples:
            a = NBAComAgent()
            tgl = a.cs_team_gamelogs('2015-16')
            tgl = a.cs_playerstats(season='2015-16', date_from='2016-03-01', date_to='2016-03-08')

        '''

        gamelogs = self.parser.season_gamelogs(self.scraper.season_gamelogs(season='2015-16', player_or_team='T'), 'T')
        self.logger.debug('there are {0} team gamelogs'.format(len(gamelogs)))

        if self.nbadb:

            table_name = 'stats.cs_team_gamelogs'

            if self.safe:
                self.nbadb.postgres_backup_table(self.nbadb.database, table_name)

            gamelogs = self.nbadb.insert_team_gamelogs(gamelogs, table_name)
            self.logger.debug('there are now {0} team gamelogs'.format(len(gamelogs)))

        return gamelogs

    def cs_teamstats(self, season, date_from=None, date_to=None):
        '''
        Fetches leaguedashteamstats and updates cs_leaguedashteamstats table

        Arguments:
             season (str): in YYYY-YY format (2015-16)
             date_from (str): in %Y-%m-%d format, default beginning of season
             date_from (str): in %Y-%m-%d format, default yesterday

        Returns:
             teamstats (list): team dictionary of basic and advanced stats
             
         Examples:
            a = NBAComAgent()
            ps = a.cs_teamstats('2015-16')
            ps = a.cs_teamstats(season='2015-16', date_from='2016-03-01', date_to='2016-03-08')

        '''

        # default is to get entire season through yesterday
        yesterday = dt.datetime.strftime(dt.datetime.today() - dt.timedelta(1), '%Y-%m-%d')

        if not date_from:
            date_from = self.nbas.season_start(season)

        if not date_to:
            date_to = yesterday

        ts_base = self.parser.teamstats(self.scraper.teamstats(season, DateFrom=date_from, DateTo=date_to))
        ts_adv = self.parser.teamstats(self.scraper.teamstats(season, DateFrom=date_from, DateTo=date_to, MeasureType='Advanced'))

        # now need to merge base and advanced
        ts_base = {t['TEAM_ID']: t for t in ts_base}

        for ts_adv in ts_adv:
            tid = ts_adv['TEAM_ID']
            base = ts_base.get(tid)

            if base:
                base.update(ts_adv)
                ts_base[tid] = base

        self.nbadb.insert_teamstats(ts_base.values(), table_name='stats.cs_teamstats', game_date=yesterday)

        return ts_base, ts_adv

    def merge_boxes(self, b1, b2):
        '''
        Combines base and advanced player or team boxscores from same game

        Arguments:
            base_box(dict): base boxscore
            adv_box(dict): advanced boxscore

        Returns:
            merged (dict) or None

        Examples:
            a = NBAComAgent()
            merged = a.merge_boxes(base_box, adv_box)

        '''

        z = b1
        z.update(b2)
        return z

    def players_to_add(self):
        '''
        Compare current_season_gamelogs and players tables to see if missing players in latter

        Arguments:
            None

        Returns:
            list
        '''

        sql = '''SELECT * FROM vw_add_players_table'''
        return self.nbadb.select_dict(sql)

    def scoreboards(self, season_start, season_end, pkl_fname=None):
        '''
        Downloads and parses range of scoreboards, optionally saves to pickle file

        Arguments:
            season_start (str): in %Y-%m-%d format
            season_end (str): in %Y-%m-%d format
            pkl_fname (optional [str]): example - 'scoreboards_2015-16.pkl'

        Returns:
             scoreboards (list): scoreboard dicts

         Examples:
            a = NBAComAgent()
            sb = a.scoreboards()
            sb = a.scoreboards(pkl_fname = 'scoreboards_2015-16.pkl')
            sb = a.scoreboards(season_start='2015-10-27', season_end='2016-04-15')
        '''

        scoreboards = []

        for day in reversed(self.date_list(season_end, season_start)):
            game_date = dt.datetime.strftime(day, '%Y-%m-%d')
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
            
        Examples:
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

    def team_opponents(self, season, season_start=None, season_end=None, pkl_fname=None):
        '''
        Downloads and parses range of team_opponents, optionally saves to pickle file

        Arguments:
            season (str): in YYYY-YY format
            season_start (str): in %Y-%m-%d format, default is actual start of season
            season_end (str): in %Y-%m-%d format, default is actual end of season
            pkl_fname (optional [str]): example - 'scoreboards_2015-16.pkl'

        Returns:
             topp (list): dicts

         Examples:
            a = NBAComAgent()
            topp = a.team_opponents('2014-15')

        '''

        topp = []

        # figure out season_start, season end
        if season_start is None:
            days = self.nbas.season_dates('2014-15')
            season_start = dt.datetime.strftime(days[-1], '%Y-%m-%d')
        else:
            days = date_list(season_end, season_start)

        for day in reversed(days):
            content = self.scraper.team_opponent_dashboard(season, DateFrom=season_start, DateTo=day)
            teamstats_opp = self.parser.team_opponent_dashboard(content)

            for team in teamstats_opp:
                fixed_team = {k.lower():v for k,v in team.iteritems()}
                fixed_team['game_date'] = dt.datetime.strftime(day, '%Y-%m-%d')
                topp.append(fixed_team)

        if pkl_fname:
            try:
                with open(pkl_fname, 'wb') as outfile:
                    pickle.dump(topp, outfile)

            except:
                self.logger.error('could not save scoreboards to {0}'.format(pkl_fname))

        return topp

if __name__ == '__main__':
    pass
