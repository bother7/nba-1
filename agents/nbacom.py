import logging

from nba.dates import datetostr
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
            db (NBAPostgres): instance
            cache_name (str): for scraper cache_name
            cookies: cookie jar
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
                                'tbs': 'team_boxscores_combined', 'box2': 'game_boxscores', 'tm': 'team'}

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

    def game_boxscores(self, game_ids=None):
        '''
        Updates table with game_information
        
        Args:
            None
            
        Returns:
            None
        '''
        if not game_ids:
            game_ids = self.db.select_dict(missing_game_boxscores())

        for g in game_ids:
            try:
                content = self.scraper.boxscore_v2015(g['gid'], g['gd'])
                v, h = self.parser.boxscore_v2015(content)
                self.db._insert_dict(v, self.table_names['box2'])
                self.db._insert_dict(h, self.table_names['box2'])
                logging.info('finished {} - {}'.format(g['gd'], g['gid']))
                return [v,h]
            except Exception as e:
                logging.error('could not get {}'.format(g))
                logging.exception(e)
                return None

    def gleague_players(self, year):
        '''
        Updates player table with g-league players

        Args:
            year (int): 2017, etc.

        Returns:
            None

        '''
        content = self.scraper.gleague_players(year)
        players = self.parser.gleague_players(content)
        for glp in gleague_player_table(players):
            self.db._insert_dict(glp, self.table_names['pl'])
        return players

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
        dbpgl = self.db.select_dict('SELECT nbacom_game_id, nbacom_player_id FROM cs_player_gamelogs')
        dbpgl_s = set(['00{}-{}'.format(gl['nbacom_game_id'], gl['nbacom_player_id']) for gl in dbpgl])

        # only try to insert missing gamelogs
        missing = pgl_s - dbpgl_s
        to_ins = [gl for gl in pgl if '{}-{}'.format(gl['GAME_ID'], gl['PLAYER_ID']) in missing]
        self.db.insert_dicts(player_gamelogs_table(to_ins), 'player_gamelogs')
        return pgl

    def playerstats(self, season_code, per_mode='Totals', date_from=None, date_to=None, all_missing=False):
        '''
        Fetches playerstats and updates playerstats table

        Args:
            season_code (str): in YYYY-YY format, e.g. 2017-18
            per_mode (str): 'Totals', 'PerGame', etc.
            date_from (str): in YYYY-mm-dd format, default None
            date_to (str): in YYYY-mm-dd format, default None
            all_missing (bool): default False

        Returns:
             None

        '''
        if date_from and date_to:
            ps_base = self.parser.playerstats(self.scraper.playerstats(season_code, per_mode=per_mode, DateFrom=date_from, DateTo=date_to))
            ps_advanced = self.parser.playerstats(self.scraper.playerstats(season_code, per_mode=per_mode, DateFrom=date_from, DateTo=date_to, MeasureType='Advanced'))
            ps = [merge_two(psb, psadv) for psb, psadv in zip(ps_base, ps_advanced)]
            vals = playerstats_table(ps, date_to, per_mode)
            logging.info(vals)
            self.db.insert_dicts(vals, self.table_names['ps'])
        elif all_missing:
            start = datetostr(d=season_start(season_code=season_code), fmt='nba')
            for day in self.db.select_list(missing_playerstats(per_mode)):
                daystr = datetostr(day, 'nba')
                base_content = self.scraper.playerstats(season_code, per_mode=per_mode, DateFrom=start, DateTo=daystr)
                ps_base = self.parser.playerstats(base_content, per_mode=per_mode)
                adv_content = self.scraper.playerstats(season_code, per_mode=per_mode, DateFrom=start, DateTo=daystr, MeasureType='Advanced')
                ps_advanced = self.parser.playerstats(adv_content, per_mode)
                ps = [merge_two(psadv, psb) for psb, psadv in zip(ps_base, ps_advanced)]
                self.db.insert_dicts(playerstats_table(ps, daystr, per_mode), self.table_names['ps'])
                logging.info('completed {}'.format(daystr))
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
        dbtgl_s = set(self.db.select_list("""SELECT CONCAT(nbacom_game_id, '-', nbacom_team_id) FROM cs_team_gamelogs"""))

        # only try to insert missing gamelogs
        missing = tgl_s - dbtgl_s
        to_ins = [gl for gl in tgl if '{}-{}'.format(gl['GAME_ID'], gl['TEAM_ID']) in missing]
        for item in team_gamelogs_table(to_ins):
            self.db._insert_dict(item, self.table_names['tgl'])
        return tgl

    def team_opponent_dashboards(self, season_code, per_mode, date_from=None, date_to=None, all_missing=False):
        '''
        Downloads and parses range of team_opponents

        Arguments:
            season_code (str): in YYYY-YY format
            per_mode (str): 'Totals', 'PerGame', etc.
            date_from (str): in %Y-%m-%d format, default is actual start of season
            date_to (str): in %Y-%m-%d format, default is actual end of season
            all_missing (bool): get all missing dashboards

        Returns:
            None
            
        '''
        if date_from and date_to:
            content = self.scraper.team_opponent_dashboard(season_code, per_mode=per_mode,
                                                           date_from=date_from, date_to=date_to)
            topp = self.parser.team_opponent_dashboard(content)
            self.db.insert_dicts(team_opponent_dashboards_table(topp, date_to), self.table_names.get('tod'))
        elif all_missing:
            topps = {}
            start = datetostr(d=season_start(season_code=season_code), fmt='nba')
            for day in self.db.select_list(missing_team_opponent_dashboard(per_mode)):
                daystr = datetostr(day, 'nba')
                logging.info('starting dashboards for {}'.format(daystr))
                content = self.scraper.team_opponent_dashboard(season_code, date_from=start, date_to=date_to)
                topp = self.parser.team_opponent_dashboard(content, per_mode)
                self.db.insert_dicts(team_opponent_dashboards_table(topp, daystr, per_mode), self.table_names.get('tod'))
            return topps
        else:
            raise ValueError('need to specify dates or set all_missing to true')

    def teamstats(self, season_code, per_mode, date_from=None, date_to=None, all_missing=False):
        '''
        Fetches teamstats and updates database table

        Args:
             season_code (str): in YYYY-YY format (2015-16)
             per_mode (str): 'Totals', 'PerGame', etc.
             date_from (str): in %Y-%m-%d format
             date_to (str): in %Y-%m-%d format
             all_missing (bool): looks for all missing teamstats from season

        Returns:
             list of team dictionary of basic and advanced stats

        '''
        if date_from and date_to:
            content_base = self.scraper.teamstats(season_code, per_mode=per_mode, date_from=date_from, date_to=date_to)
            ts_base = self.parser.teamstats(content_base, per_mode)
            content_adv = self.scraper.teamstats(season_code, per_mode=per_mode,
                                                 date_from=date_from, date_to=date_to, MeasureType='Advanced')
            ts_advanced = self.parser.teamstats(content_adv, per_mode)
            ts_merged = [merge_two(tsb, tsadv) for tsb, tsadv in zip(ts_base, ts_advanced)]
            self.db.insert_dicts(teamstats_table(ts_merged, date_to, per_mode), self.table_names['ts'])
        elif all_missing:
            start = datetostr(d=season_start(season_code=season_code), fmt='nba')
            for day in self.db.select_list(missing_teamstats(per_mode)):
                logging.info('teamstats: getting {}'.format(day))
                daystr = datetostr(day, 'nba')
                content_base = self.scraper.teamstats(season_code, per_mode=per_mode,
                                                      date_from=start, date_to=daystr)
                ts_base = self.parser.teamstats(content_base, per_mode)
                content_adv = self.scraper.teamstats(season_code, per_mode=per_mode,
                                                     date_from=start, date_to=daystr, MeasureType='Advanced')
                ts_advanced = self.parser.teamstats(content_adv, per_mode)
                ts = [merge_two(tsb, tsadv) for tsb, tsadv in zip(ts_base, ts_advanced)]
                self.db.insert_dicts(teamstats_table(ts, daystr, per_mode), self.table_names['ts'])
                logging.debug('teamstats: completed {}'.format(daystr))
        else:
            raise ValueError('need to specify dates or set all_missing to true')


if __name__ == '__main__':
    pass