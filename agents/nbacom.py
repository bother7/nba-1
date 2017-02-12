import datetime as dt
import logging
import time

try:
    import cPickle as pickle
except:
    import pickle

from nba.scrapers.nbacom import NBAComScraper
from nba.parsers.nbacom import NBAComParser
from nba.seasons import *
from nba.dates import *


class NBAComAgent(object):
    '''
    Performs script-like tasks using NBA.com API
    Intended to replace standalone scripts so can use common API and tools

    Examples:
        a = NBAComAgent()
        gamelogs = a.cs_player_gamelogs('2015-16')

    '''

    def __init__(self, cache_name='nbacom-cache', cookies=None, db=None, safe=False):
        '''
        Args:
            db (bool): compose NBAComPg object as self.db
            safe (bool): create backups of tables prior to inserts
        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.scraper = NBAComScraper(cache_name=cache_name, cookies=cookies)
        self.parser = NBAComParser()
        self.safe = safe

        if db:
            self.db = db
        else:
            self.db = None

    def _merge(self, merge_dico, dico_list):
        '''
        See http://stackoverflow.com/questions/28838291/merging-multiple-dictionaries-in-python
        Args:
            merge_dico:
            dico_list:

        Returns:

        '''
        for dico in dico_list:
            for key, value in dico.items():
                if type(value) == type(dict()):
                    merge_dico.setdefault(key, dict())
                    self._merge(merge_dico[key], [value])
                else:
                    merge_dico[key] = value
        return merge_dico

    def combined_player_boxscores(self, gid):
        '''
        Arguments:
            gid(str): game ID, with leading '00'
        Returns:
            players (list): combined traditional, advanced, misc, scoring, usage

        Examples:
            a = NBAComAgent()
            players = a.combined_player_boxscores('0020161001')
        '''
        traditional_players, traditional_teams, traditional_starter_bench = self.parser.boxscore_traditional(self.scraper.boxscore_traditional(gid))
        adv_players, adv_team = self.parser.boxscore_advanced(self.scraper.boxscore_advanced(gid))
        misc_players, misc_team = self.parser.boxscore_misc(self.scraper.boxscore_misc(gid))
        scoring_players, scoring_team = self.parser.boxscore_scoring(self.scraper.boxscore_scoring(gid))
        usage_players = self.parser.boxscore_usage(self.scraper.boxscore_usage(gid))

        # now need to combine player and team boxscores
        players = self._merge(dict(), [{t['PLAYER_ID']: t for t in traditional_players}, {t['PLAYER_ID']: t for t in adv_players},
                                       {t['PLAYER_ID']: t for t in misc_players}, {t['PLAYER_ID']: t for t in scoring_players},
                                       {t['PLAYER_ID']: t for t in usage_players}])

        return list(players.values())

    def combined_team_boxscores(self, gid):
        '''
        Arguments:
            gid(str): game ID, with leading '00'
        Returns:
            teams (list): combined traditional, advanced, misc, scoring

        Examples:
            a = NBAComAgent()
            players = a.combined_team_boxscores('0020161001')
        '''
        traditional_players, traditional_teams, traditional_starter_bench = self.parser.boxscore_traditional(self.scraper.boxscore_traditional(gid))
        adv_players, adv_teams = self.parser.boxscore_advanced(self.scraper.boxscore_advanced(gid))
        misc_players, misc_teams = self.parser.boxscore_misc(self.scraper.boxscore_misc(gid))
        scoring_players, scoring_teams = self.parser.boxscore_scoring(self.scraper.boxscore_scoring(gid))

        # now need to combine player and team boxscores
        teams = self._merge(dict(), [{t['TEAM_ID']: t for t in traditional_teams}, {t['TEAM_ID']: t for t in adv_teams},
                                       {t['TEAM_ID']: t for t in misc_teams}, {t['TEAM_ID']: t for t in scoring_teams}])
        #teams = self._merge(dict(), traditional_teams, adv_team, misc_team, scoring_team)
        return list(teams.values())

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

    def new_players(self, season, cs_only=1):
        '''
        Arguments:
            season (str): in YYYY-YY format
            cs_only(bool): default is current season only
        Returns:
            to_insert (list): list of players that were added to stats.players
        Examples:
            a = NBAComAgent()
            combined = a.new_players('2015-16')
        '''
        to_insert = []
        if self.db:
            q = 'SELECT * FROM stats.players_to_add'
            for id in self.db.select_list(q):
                content = self.scraper.player_info(id, season)
                to_insert.append(self.parser.player_info(content))

        return to_insert

    def player_gamelogs(self, season, table_name=None, date_from=None, date_to=None):
        '''
        Fetches player_gamelogs and updates cs_player_gamelogs table

        Arguments:
             season (str): in YYYY-YY format (2015-16)

        Returns:
             players (list): player dictionary of stats + dfs points
        '''

        return self.parser.season_gamelogs(self.scraper.season_gamelogs(season, 'P'), 'P')

    def playerstats(self, season, date_from=None, date_to=None):
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
            date_from = season_start(season)

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
                base['as_of'] = date_to
                ps_base[pid] = base

        return list(ps_base.values())

    def players_to_add(self):
        '''
        Compare current_season_gamelogs and players tables to see if missing players in latter

        Arguments:
            None

        Returns:
            list
        '''


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

        for day in reversed(date_list(season_end, season_start)):
            game_date = dt.datetime.strftime(day, '%Y-%m-%d')
            scoreboard_json = self.scraper.scoreboard(game_date=game_date)
            scoreboard = self.parser.scoreboard(scoreboard_json, game_date=game_date)
            scoreboards.append(scoreboard)

        if pkl_fname:
            try:
                with open('/home/sansbacon/scoreboards_20160108.pkl', 'wb') as outfile:
                    pickle.dump(scoreboards, outfile)

            except:
                logging.error('could not save scoreboards to {0}'.format(pkl_fname))

        return scoreboards

    def team_gamelogs(self, season, date_from=None, date_to=None):
        '''
        Fetches team_gamelogs and updates cs_team_gamelogs table

        Arguments:
             season (str): in YYYY-YY format (2015-16)

        Returns:
             team_gl (list): player dictionary of stats

        Examples:
            a = NBAComAgent()
            tgl = a.team_gamelogs('2015-16')
            tgl = a.team_gamelogs(season='2015-16', date_from='2016-03-01', date_to='2016-03-08')

        '''
        content = self.scraper.season_gamelogs(season=season, player_or_team='T')
        if content:
            return self.parser.season_gamelogs(content, 'T')
        else:
            return None

    def teamstats_daily_range(self, season, date_from, date_to):
        '''
        Bulk daily teamstats for days from date_from to date_to
        Arguments:
             season (str): in YYYY-YY format (2015-16)
             date_from (str): in %Y-%m-%d format, default beginning of season
             date_from (str): in %Y-%m-%d format, default yesterday

        Returns:
             teamstats (list): team dictionary of basic and advanced stats
        '''
        vals = []
        for d in list(reversed(date_list(date_to, date_from))):
            vals.append(self.teamstats_daily(season, date_from=date_from, date_to=dt.datetime.strftime(d, '%Y-%m-%d')))
        return [item for sublist in vals for item in sublist]

    def teamstats_daily(self, season, date_from, date_to):
        '''

        Arguments:
             season (str): in YYYY-YY format (2015-16)
             date_from (str): in %Y-%m-%d format, default beginning of season
             date_from (str): in %Y-%m-%d format, default yesterday

        Returns:
             teamstats (list): team dictionary of basic and advanced stats

         Examples:
            a = NBAComAgent()
            ps = a.cs_teamstats(season='2015-16', date_from='2016-03-01', date_to='2016-03-08')
        '''

        # default is to get entire season through yesterday
        s1, s2 = season.split('-')
        if not s1 and s2:
            raise ValueError('season parameter must be in YYYY-YY format')

        ts_base = self.parser.teamstats(self.scraper.teamstats(season, DateFrom=date_from, DateTo=date_to))
        ts_adv = self.parser.teamstats(self.scraper.teamstats(season, DateFrom=date_from, DateTo=date_to, MeasureType='Advanced'))

        # now need to merge base and advanced
        ts_base = {t['TEAM_ID']: t for t in ts_base}

        for ts_adv in ts_adv:
            tid = ts_adv['TEAM_ID']
            base = ts_base.get(tid)

            if base:
                base.update(ts_adv)
                base['season'] = int(s1) + 1
                base['nbacom_season_id'] = int(s2) + 22000 - 1
                base['as_of'] = date_to
                ts_base[tid] = base

        return list(ts_base.values())

    def teamstats(self, season, date_from=None, date_to=None):
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
        s1, s2 = season.split('-')
        yesterday = dt.datetime.strftime(dt.datetime.today() - dt.timedelta(1), '%Y-%m-%d')

        if not date_from:
            date_from = season_start(season)

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
                base['season'] = int(s1) + 1
                base['nbacom_season_id'] = int(s2) + 22000 - 1
                ts_base[tid] = base

        return ts_base

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
            days = season_dates('2014-15')
            season_start = dt.datetime.strftime(days[-1], '%Y-%m-%d')
        else:
            days = date_list(season_end, season_start)

        for day in reversed(days):
            content = self.scraper.team_opponent_dashboard(season, DateFrom=season_start, DateTo=day)
            teamstats_opp = self.parser.team_opponent_dashboard(content)

            for team in teamstats_opp:
                fixed_team = {k.lower():v for k,v in team.items()}
                fixed_team['game_date'] = dt.datetime.strftime(day, '%Y-%m-%d')
                topp.append(fixed_team)

        if pkl_fname:
            try:
                with open(pkl_fname, 'wb') as outfile:
                    pickle.dump(topp, outfile)

            except:
                logging.error('could not save scoreboards to {0}'.format(pkl_fname))

        return topp

    def update_player_positions(self):
        '''
        Trying to make sure all position data is current
        Only info in nba.com is PLAYER key, this is only Guard, etc.
        Unclear where the PG, etc. comes from
        '''
        if not self.db:
            raise ValueError('need database connection to update players')
        q = """SELECT nbacom_player_id FROM stats.players2 WHERE nbacom_position IS NULL or nbacom_position = ''"""
        uq = """UPDATE stats.players2 SET nbacom_position = '{}' WHERE nbacom_player_id = {}"""

        for pid in self.db.select_list(q):
            logging.info('getting {}'.format(pid))
            pinfo = self.parser.player_info(self.scraper.player_info(pid, '2015-16'))
            if pinfo.get('POSITION'):
                self.db.update(uq.format(pinfo.get('POSITION'), pid))
                logging.info('inserted {}'.format(pinfo.get('DISPLAY_FIRST_LAST')))

if __name__ == '__main__':
    pass
    '''
    from nba.db.nbacom import NBAPostgres
    import time

    a = NBAComAgent(cache_name='nbacom-boxes')
    nbap = NBAPostgres(user='postgres', password='cft091146', database='nba')
    q = 'SELECT game_id from stats.games where game_date <= now()::date order by game_date DESC'
    with open('/home/sansbacon/gameids.txt', 'r') as infile:
        ids_complete = infile.read().splitlines()
        ids_complete = [int(id) for id in ids_complete if id != '']

    for gid in set(nbap.select_list(q)) - set(ids_complete):
        gid = '00' + str(gid)
        a.combined_player_boxscores(gid)
        a.combined_team_boxscores(gid)
        print('completed game {}'.format(gid))
        time.sleep(2)
    '''

    '''
    dashboards = []
    season = '1999-00'
    st = season_start(season)
    for d in date_list(season_end(season), st):
        content = s.team_opponent_dashboard(season=season, DateFrom=st, DateTo=datetime.datetime.strftime(d, '%Y-%m-%d'))
        as_of = datetime.datetime.strftime(d, '%Y-%m-%d')
        for dash in p.team_opponent_dashboard(content):
            dash['as_of'] = as_of
            dashboards.append(dash)
        print 'completed {}'.format(d)
        time.sleep(1)

    for idx, d in enumerate(dashboards):
        dashboards[idx].pop('cfid', None)
        dashboards[idx].pop('cfparams', None)
    db.insert_dicts(dashboards, 'stats.team_opponent_dashboard')
    '''