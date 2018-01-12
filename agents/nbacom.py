import logging

from nba.parsers.nbacom import NBAComParser
from nba.pipelines.nbacom import *
from nba.db.queries import *
from nba.scrapers.nbacom import NBAComScraper
from nba.season import season_start
from nba.utility import merge_many, merge_two, nbacom_idstr


class NBAComAgent(object):
    '''
    Performs script-like tasks using NBA.com API
    '''

    def __init__(self, db=None, cache_name='nbacom-agent', cookies=None, table_names=None):
        '''
        Args:
            cache_name (str): for scraper cache_name
            cookies: cookie jar
            db (NBAPostgres): instance
            table_names (dict): Database table names
        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.scraper = NBAComScraper(cache_name=cache_name, cookies=cookies)
        self.parser = NBAComParser()
        self.db = db

        if table_names:
            self.table_names = table_names
        else:
            self.table_names = {'pgl': 'player_gamelogs', 'tgl': 'team_gamelogs', 'seas': 'season',
                                'pl': 'player', 'ps': 'playerstats_daily', 'ts': 'teamstats_daily',
                                'tod': 'team_opponent_dashboard', 'pbs': 'player_boxscores_combined',
                                'tbs': 'team_boxscores_combined', 'box2': 'boxv2015', 'tm': 'team'}

    def combined_boxscores(self, game_ids=None):
            '''
            Combines 5 types of boxscores (traditional, advanced, misc, scoring, usage) into list of team boxscore

            Arguments:
                game_id (str): game ID, with leading '00'

            Returns:
                tuple: list of player boxscores, list of team boxscores

            '''
            player_boxscores = []
            team_boxscores = []
            if not game_ids:
                game_ids = set(self.db.select_list(missing_player_boxscores())) | \
                       set(self.db.select_list(missing_team_boxscores()))

            # need union of missing player and team
            for game_id in game_ids:
                # make sure game_id in correct format when requesting boxscores
                gid = nbacom_idstr(game_id)
                logging.info('agent.nbacom.combined_boxscores: getting {}'.format(gid))

                # get 5 types of boxscores
                traditional_players, traditional_teams, traditional_starter_bench = \
                    self.parser.boxscore_traditional(self.scraper.boxscore_traditional(gid))
                adv_players, adv_teams = self.parser.boxscore_advanced(self.scraper.boxscore_advanced(gid))
                misc_players, misc_teams = self.parser.boxscore_misc(self.scraper.boxscore_misc(gid))
                scoring_players, scoring_teams = self.parser.boxscore_scoring(self.scraper.boxscore_scoring(gid))
                usage_players = self.parser.boxscore_usage(self.scraper.boxscore_usage(gid))

                # combine player and team boxscores, respectively
                players_combined = list(merge_many(dict(), [{t['PLAYER_ID']: t for t in traditional_players},
                                              {t['PLAYER_ID']: t for t in adv_players},
                                              {t['PLAYER_ID']: t for t in misc_players},
                                              {t['PLAYER_ID']: t for t in scoring_players},
                                              {t['PLAYER_ID']: t for t in usage_players}]).values())
                teams_combined = list(merge_many(dict(),
                                   [{t['TEAM_ID']: t for t in traditional_teams}, {t['TEAM_ID']: t for t in adv_teams},
                                    {t['TEAM_ID']: t for t in misc_teams}, {t['TEAM_ID']: t for t in scoring_teams}]).values())

                # now add to the database
                self.db.safe_insert_dicts(player_boxscores_table(players_combined), self.table_names['pbs'])
                self.db.safe_insert_dicts(team_boxscores_table(teams_combined), self.table_names['tbs'])
            return (player_boxscores, team_boxscores)

    def linescores(self):
        '''
        Updates table with game_information
        
        Args:
            None
            
        Returns:
            None
        '''
        for g in self.db.select_dict(missing_linescores()):
            try:
                content = self.scraper.boxscore_v2015(g['gid'], g['gd'])
                v, h = self.parser.boxscore_v2015(content)
                self.db.insert_dicts([v, h], self.table_names['box2'])
                logging.info('finished {} - {}'.format(g['gd'], g['gid']))
            except Exception as e:
                logging.error('could not get {}'.format(g))
                logging.exception(e)

    def new_players(self, season_code):
        '''
        Updates player table with missing players

        Arguments:
            season_code (str): in YYYY-YY format

        Returns:
            list: players to add to player table

        '''
        content = self.scraper.players_v2015(season_code)
        players = players_v2015_table(self.parser.players_v2015(content))

        # use set difference to identify missing ids
        # then list comprehension to filter players
        currids = set([int(p.get('nbacom_player_id', 0)) for p in players])
        allids = set(self.db.select_list('SELECT nbacom_player_id from player'))
        missing = currids - allids
        if missing:
            np = [p for p in players if int(p['nbacom_player_id']) in missing]
            for p in players_v2015_table(np):
                logging.info('nbacom.agent.new_players: adding {}'.format(p))
                self.db._insert_dict(p, 'player')
            return np
        else:
            logging.info('nbacom.agent.new_players: no players to add')
            return None

    def player_gamelogs(self, season_code, date_from=None, date_to=None):
        '''
        Fetches player_gamelogs and updates player_gamelogs table

        Args:
            season_code (str): in YYYY-YY format (2017-18)
            date_from (str): in YYYY-mm-dd format, default None
            date_to (str): in YYYY-mm-dd format, default None

        Returns:
             list: of player dict

        '''
        # get all player gamelogs from nba.com
        content = self.scraper.season_gamelogs(season_code, 'P', date_from=date_from, date_to=date_to)
        pgl = self.parser.season_gamelogs(content, 'P')
        pgl_s = set(['{}-{}'.format(gl['GAME_ID'], gl['PLAYER_ID']) for gl in pgl])

        # compare to gamelogs in database: refresh view then compare
        self.db.execute('refresh materialized view cs_player_gamelogs;')
        dbpgl = self.db.select_dict('SELECT game_id, nbacom_player_id FROM cs_player_gamelogs')
        dbpgl_s = set(['00{}-{}'.format(gl['game_id'], gl['nbacom_player_id']) for gl in dbpgl])

        # only try to insert missing gamelogs
        missing = pgl_s - dbpgl_s
        to_ins = [gl for gl in pgl if '00{}-{}'.format(gl['GAME_ID'], gl['PLAYER_ID']) in missing]
        for gl in player_gamelogs_table(to_ins):
            self.db._insert_dict(gl, 'player_gamelogs')

        # update season_year column in database
        self.db.execute('select player_gamelogs_season_year();')
        return pgl

    def playerstats(self, season_code, date_from=None, date_to=None, all_missing=False):
        '''
        Fetches playerstats and updates playerstats table

        Args:
            season_code: str in YYYY-YY format, e.g. 2017-18
            date_from (str): in YYYY-mm-dd format, default None
            date_to (str): in YYYY-mm-dd format, default None
            all_missing (bool): default False

        Returns:
             list: of dict

        '''
        if date_from and date_to:
            ps_base = self.parser.playerstats(self.scraper.playerstats(season_code, DateFrom=date_from, DateTo=date_to))
            ps_advanced = self.parser.playerstats(self.scraper.playerstats(season_code, DateFrom=date_from, DateTo=date_to, MeasureType='Advanced'))
            ps = [merge_two(psb, psadv) for psb, psadv in zip(ps_base, ps_advanced)]
            for p in playerstats_table(ps, date_to):
                self.db._insert_dict(p, 'playerstats_daily')
            return ps
        elif all_missing:
            pstats = []
            start = datetostr(d=season_start(season_code=season_code), fmt='nba')
            for day in self.db.select_list(missing_playerstats()):
                daystr = datetostr(day, 'nba')
                ps_base = self.parser.playerstats(self.scraper.playerstats(season_code, DateFrom=start, DateTo=daystr))
                ps_advanced = self.parser.playerstats(self.scraper.playerstats(season_code, DateFrom=start, DateTo=daystr, MeasureType='Advanced'))
                ps = [merge_two(psadv, psb) for psb, psadv in zip(ps_base, ps_advanced)]
                pstats.append(ps)
                self.db.insert_dicts(playerstats_table(ps, daystr), self.table_names['ps'])
                logging.info('completed {}'.format(daystr))
            return [item for sublist in pstats for item in sublist]
        else:
            raise ValueError('agent.nbacom.playerstats: need to specify dates or set all_missing to true')

    def refresh_materialized(self):
        '''
        Calls postgres function to refresh all materialized views.
        
        '''
        refreshq = """SELECT RefreshAllMaterializedViews('*', true);"""
        try:
            self.db.execute(refreshq)
        except Exception as e:
            logging.exception('could not refresh materialized views: {}'.format(e))

    def team_gamelogs(self, season_code, date_from=None, date_to=None):
        '''
        Fetches team_gamelogs and updates team_gamelogs table

        Args:
            season_code (str): in YYYY-YY format (2017-18)
            date_from (str): in YYYY-mm-dd format, default None
            date_to (str): in YYYY-mm-dd format, default None
            
        Returns:
            list: of dict

        '''
        content = self.scraper.season_gamelogs(season_code, 'T', date_from, date_to)
        tgl = self.parser.season_gamelogs(content, 'T')
        tgl_s = set(['{}-{}'.format(gl['GAME_ID'], gl['TEAM_ID']) for gl in tgl])

        # compare team gamelogs to those already in database
        self.db.execute('refresh materialized view cs_team_gamelogs;')
        dbtgl_s = set(self.db.select_list("""SELECT '00'::text || game_id::text || '-' || team_id::text FROM cs_team_gamelogs"""))

        # only try to insert missing gamelogs
        missing = tgl_s - dbtgl_s
        to_ins = [gl for gl in tgl if '{}-{}'.format(gl['GAME_ID'], gl['TEAM_ID']) in missing]
        for item in team_gamelogs_table(to_ins):
            logging.info(item)
            self.db._insert_dict(item, self.table_names['tgl'])
        return tgl

    def team_opponent_dashboards(self, season_code, date_from=None, date_to=None, all_missing=False):
        '''
        Downloads and parses range of team_opponents

        Arguments:
            season_code (str): in YYYY-YY format
            date_from (str): in %Y-%m-%d format, default is actual start of season
            date_to (str): in %Y-%m-%d format, default is actual end of season
            all_missing (bool): get all missing dashboards

        Returns:
             list: of dict

        TODO:
            Change execute statement to database trigger

        '''
        if date_from and date_to:
            content = self.scraper.team_opponent_dashboard(season_code, DateFrom=date_from, DateTo=date_to)
            topp = self.parser.team_opponent_dashboard(content)
            self.db.insert_dicts(team_opponent_dashboards_table(topp, date_to), self.table_names.get('tod'))
            self.db.execute('select tod_season_year();') # fill in season_year field in table
            return topp
        elif all_missing:
            topps = {}
            start = datetostr(d=season_start(season_code=season_code), fmt='nba')
            for day in self.db.select_list(missing_team_opponent_dashboard()):
                daystr = datetostr(day, 'nba')
                logging.info('starting dashboards for {}'.format(daystr))
                content = self.scraper.team_opponent_dashboard(season_code, DateFrom=start, DateTo=daystr)
                topp = self.parser.team_opponent_dashboard(content)
                self.db.insert_dicts(team_opponent_dashboards_table(topp, daystr), self.table_names.get('tod'))
                topps[daystr] = topp
            self.db.execute('select tod_season_year();') # fill in season_year field in table
            return topps
        else:
            raise ValueError('need to specify dates or set all_missing to true')

    def teamstats(self, season_code, date_from=None, date_to=None, all_missing=False):
        '''
        Fetches teamstats and updates database table

        Args:
             season_code (str): in YYYY-YY format (2015-16)
             date_from (str): in %Y-%m-%d format, default beginning of season
             date_from (str): in %Y-%m-%d format, default yesterday
             all_missing (bool): looks for all missing teamstats from season

        Returns:
             list of team dictionary of basic and advanced stats

        '''
        if date_from and date_to:
            ts_base = self.parser.teamstats(self.scraper.teamstats(season_code, DateFrom=date_from, DateTo=date_to))
            ts_advanced = self.parser.teamstats(self.scraper.teamstats(season_code, DateFrom=date_from, DateTo=date_to, MeasureType='Advanced'))
            ts_merged = [merge_two(tsb, tsadv) for tsb, tsadv in zip(ts_base, ts_advanced)]
            self.db.insert_dicts(teamstats_table(ts_merged, date_to), self.table_names['ts'])
        elif all_missing:
            tstats = {}
            start = datetostr(d=season_start(season_code=season_code), fmt='nba')
            for day in self.db.select_list(missing_teamstats()):
                daystr = datetostr(day, 'nba')
                ts_base = self.parser.teamstats(self.scraper.teamstats(season_code, DateFrom=start, DateTo=daystr))
                ts_advanced = self.parser.teamstats(self.scraper.teamstats(season_code, DateFrom=start, DateTo=daystr, MeasureType='Advanced'))
                ts = [merge_two(tsb, tsadv) for tsb, tsadv in zip(ts_base, ts_advanced)]
                self.db.insert_dicts(teamstats_table(ts, daystr), self.table_names['ts'])
                tstats[daystr] = ts
                logging.debug('teamstats: completed {}'.format(daystr))
            return tstats
        else:
            raise ValueError('need to specify dates or set all_missing to true')


if __name__ == '__main__':
    pass