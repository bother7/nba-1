import datetime as dt

from nba.parsers.nbacom import NBAComParser
from nba.scrapers.nbacom import NBAComScraper
from nba.seasons import *
from nba.dates import *


class NBAComAgent(object):
    '''
    Performs script-like tasks using NBA.com API
    '''

    def __init__(self, db=None, cache_name=None, cookies=None):
        '''
        Arguments:
            cache_name: str for scraper cache_name
            cookies: cookie jar
            db: NBAComPg instance
        '''
        self.scraper = NBAComScraper(cache_name=cache_name, cookies=cookies)
        self.parser = NBAComParser()
        if db:
            self.db = db
            self.insert_db = True
        else:
            self.insert_db=False

    def _merge(self, merge_dico, dico_list):
        '''
        See http://stackoverflow.com/questions/28838291/merging-multiple-dictionaries-in-python
        Args:
            merge_dico:
            dico_list:
        Returns:
            merged dictionary
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
        Combines 5 types of boxscores from nba.com API into list of boxscores
        Arguments:
            gid: string game ID, with leading '00'
        Returns:
            list of player boxscores combined - traditional, advanced, misc, scoring, usage
        Examples:
            a = NBAComAgent()
            playerboxes = a.combined_player_boxscores('0020161001')
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
        Combines 5 types of boxscores from nba.com API into list of boxscores
        Arguments:
            gid: string game ID, with leading '00'
        Returns:
            list of team boxscores - combined traditional, advanced, misc, scoring
        Examples:
            a = NBAComAgent()
            teamboxes = a.combined_team_boxscores('0020161001')
        '''
        traditional_players, traditional_teams, traditional_starter_bench = self.parser.boxscore_traditional(self.scraper.boxscore_traditional(gid))
        adv_players, adv_teams = self.parser.boxscore_advanced(self.scraper.boxscore_advanced(gid))
        misc_players, misc_teams = self.parser.boxscore_misc(self.scraper.boxscore_misc(gid))
        scoring_players, scoring_teams = self.parser.boxscore_scoring(self.scraper.boxscore_scoring(gid))

        # now need to combine player and team boxscores
        teams = self._merge(dict(), [{t['TEAM_ID']: t for t in traditional_teams}, {t['TEAM_ID']: t for t in adv_teams},
                                       {t['TEAM_ID']: t for t in misc_teams}, {t['TEAM_ID']: t for t in scoring_teams}])
        return list(teams.values())

    def new_players(self, season):
        '''
        Updates players table with missing players

        Arguments:
            season (str): in YYYY-YY format
        Returns:
            list of players to add to stats.players
        Examples:
            a = NBAComAgent(cache_name='newplayers', cookies=httplib.CookieJar(), db=NBAComPg(...))
            np = a.new_players(season='2015-16')
        '''
        content = self.scraper.players(season, cs_only=1)
        players = self.parser.players(content)
        currids = set([int(p.get('PERSON_ID',0)) for p in players])
        allids = set(self.db.select_list('SELECT nbacom_player_id from players'))
        missing = currids - allids
        if missing:
            np = [self.parser.player_info(self.scraper.player_info(pid, season)) for pid in missing]
            if self.insert_db:
                self.db.insert_players(np)
            return np
        else:
            return None

    def player_gamelogs(self, season, date_from=None, date_to=None):
        '''
        Fetches player_gamelogs and updates player_gamelogs table

        Arguments:
            season: str in YYYY-YY format (2015-16)
            date_from: str in YYYY-mm-dd format
            date_to: str in YYYY-mm-dd format
            insert_db: add list to database

        Returns:
             players (list): player dictionary of stats + dfs points

        Examples:
            a = NBAComAgent()
            np = a.player_gamelogs(season='2015-16', date_from='2016-03-01', date_to='2016-03-08', insert_db=True)
        '''
        # mpgl -> list of game_ids for which there are no player gamelogs
        # filter gamelogs to those from missing game_ids
        pgl = self.parser.season_gamelogs(self.scraper.season_gamelogs(season, 'P'), 'P')
        mpgl = self.db.missing_pgl()
        pgl = [gl for gl in pgl if gl.get('GAME_ID', None) in mpgl]

        # now make sure you have no new players
        currids = set([int(p.get('PERSON_ID', 0)) for p in pgl])
        allids = set(self.db.select_list('SELECT nbacom_player_id from players'))

        if self.insert_db
            self.db.insert_players([self.parser.player_info(self.scraper.player_info(pid, season)) for pid in currids - allids])
            self.db.insert_player_gamelogs(pgl)
        return pgl

    def playerstats(self, season, date_from=None, date_to=None):
        '''
        Fetches playerstats and updates player_gamelogs table

        Arguments:
            season: str in YYYY-YY format (2015-16)
            date_from: str in YYYY-mm-dd format
            date_to: str in YYYY-mm-dd format

        Returns:
             players (list): player dictionary of stats + dfs points

        Examples:
            a = NBAComAgent()
            np = a.playerstats(season='2015-16', date_from='2016-03-01', date_to='2016-03-08')
        '''
        # gd -> list of game_dates for which there are no playerstats
        # get only those missing dates

        yesterday = dt.datetime.strftime(dt.datetime.today() - dt.timedelta(1), '%Y-%m-%d')
        if not date_from:
            date_from = season_start(season)
        if not date_to:
            date_to = yesterday
        ps_base = self.parser.playerstats(self.scraper.playerstats(season, DateFrom=date_from, DateTo=date_to))
        ps_advanced = self.parser.playerstats(self.scraper.playerstats(season, DateFrom=date_from, DateTo=date_to, MeasureType='Advanced'))
        ps = [self._merge(dict(), [psb, psadv]) for psb, psadv in zip(ps_base, ps_advanced)]
        if self.insert_db:
            self.db.insert_playerstats(ps, as_of=date_to)
        return ps

    def scoreboards(self, season_start, season_end):
        '''
        Downloads and parses range of scoreboards

        Arguments:
            season_start (str): in %Y-%m-%d format
            season_end (str): in %Y-%m-%d format

        Returns:
             scoreboards (list): scoreboard dicts

         Examples:
            a = NBAComAgent()
            sb = a.scoreboards(season_start='2015-10-27', season_end='2016-04-15')
        '''
        scoreboards = []
        for day in reversed(date_list(season_end, season_start)):
            game_date = dt.datetime.strftime(day, '%Y-%m-%d')
            scoreboard_json = self.scraper.scoreboard(game_date=game_date)
            scoreboard = self.parser.scoreboard(scoreboard_json, game_date=game_date)
            scoreboards.append(scoreboard)

        if self.insert_db:
            self.db.insert_scoreboards(scoreboards)
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
            tgl = a.team_gamelogs(season='2015-16', date_from='2016-03-01', date_to='2016-03-08', insert_db=True)

        '''
        content = self.scraper.season_gamelogs(season=season, player_or_team='T')
        tgl = self.parser.season_gamelogs(content, 'T')
        mtgl = self.db.missing_tgl()
        toins = [gl for gl in tgl if gl.get('GAME_ID', None) in mtgl]
        if self.insert_db:
            self.db.insert_team_gamelogs(toins)
        return toins

    def teamstats(self, season, date_from=None, date_to=None):
        '''
        Fetches teamstats and updates database table

        Arguments:
             season (str): in YYYY-YY format (2015-16)
             date_from (str): in %Y-%m-%d format, default beginning of season
             date_from (str): in %Y-%m-%d format, default yesterday

        Returns:
             list of team dictionary of basic and advanced stats

         Examples:
            a = NBAComAgent()
            ps = a.teamstats(season='2015-16', date_from='2016-03-01', date_to='2016-03-08')
        '''
        if not date_from:
            date_from = season_start(season)
        if not date_to:
            date_to = yesterday(site_format('nba'))
        ts_base = self.parser.teamstats(self.scraper.teamstats(season, DateFrom=date_from, DateTo=date_to))
        ts_advanced = self.parser.teamstats(self.scraper.teamstats(season, DateFrom=date_from, DateTo=date_to, MeasureType='Advanced'))
        ts = [self._merge(dict(), [tsb, tsadv]) for tsb, tsadv in zip(ts_base, ts_advanced)]
        if self.insert_db:
            self.db.insert_playerstats(ts, as_of=date_to)
        return ts

    def team_opponent_dashboards(self, season, start=None, end=None):
        '''
        TODO: refactor into database class
        Downloads and parses range of team_opponents

        Arguments:
            season (str): in YYYY-YY format
            season_start (str): in %Y-%m-%d format, default is actual start of season
            season_end (str): in %Y-%m-%d format, default is actual end of season

        Returns:
             topp (list): dicts

         Examples:
            a = NBAComAgent()
            topp = a.team_opponent_dashboards('2014-15')
        '''
        topp = []
        if not start:
            start = season_start(season)
        if not end:
            end = yesterday(site_format('nba'))
        for day in date_list(end, start):
            content = self.scraper.team_opponent_dashboard(season, DateFrom=start, DateTo=day)
            teamstats_opp = self.parser.team_opponent_dashboard(content)
            for team in teamstats_opp:
                fixed_team = {k.lower():v for k,v in team.items()}
                fixed_team['as_of'] = datetostr(day, 'nba')
                topp.append(fixed_team)
        topp = [item for sublist in topp for item in sublist]
        if self.insert_db:
            self.db.insert_dicts(team_opponent_dashboards_table(topp), 'team_opponent_dashboards')
        return topp

    def update_player_positions(self):
        '''
        Trying to make sure all position data is current
        Only info in nba.com is PLAYER key, this is only Guard, etc.
        Unclear where the PG, etc. comes from
        TODO: this is not functional yet
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