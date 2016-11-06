from collections import defaultdict
import json
import logging
import os

from nba.scrapers.scraper import EWTScraper


class NBAComScraper(EWTScraper):
    '''
    Usage:
        s = NBAComScraper()
        content = s.team_dashboard(team_id='1610612738', season='2015-16')
    '''

    def __init__(self,**kwargs):

        '''
        EWTScraper parameters: 'dldir', 'expire_time', 'headers', 'use_cache'
        '''

        # see http://stackoverflow.com/questions/8134444
        EWTScraper.__init__(self, **kwargs)
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

    def boxscore(self, game_id, season):
        '''
        Boxscore from a single game

        Arguments:
            game_id: numeric identifier of game
            season: string in YYYY-YY format (2015-16)

        Returns:
            content: python data structure of json documnt
        '''
        
        base_url = 'http://stats.nba.com/stats/boxscoretraditionalv2?'

        params = {
          'EndPeriod': '10',
          'EndRange': '100000',
          'GameID': game_id,
          'RangeType': '2',
          'Season': season,
          'SeasonType': 'Regular Season',
          'StartPeriod': '1',
          'StartRange': '0'
        }

        content = self.get_json(url=base_url, payload=params)

        if not content: logging.error('could not get content from url: {0}'.format(base_url))

        return content

    def boxscore_advanced(self, game_id):
        '''
        Boxscore from a single game

        Arguments:
            game_id: numeric identifier of game (has to be 10-digit, may need two leading zeroes)

        Returns:
            content: python data structure of json document
        '''

        base_url = 'http://stats.nba.com/stats/boxscoreadvancedv2?'

        if len(str(game_id)) == 8:
            game_id = '00' + str(game_id)

        params = {
            'GameID': game_id,
            'StartPeriod': 1,
            'EndPeriod': 10,
            'StartRange': 0,
            'EndRange': 28800,
            'RangeType': 0
        }

        content = self.get_json(url=base_url, payload=params)

        if not content: logging.error('could not get content from url: {0}'.format(base_url))

        return content

    def boxscores(self, gids, season, box_type='both', save=False, savedir=None):
        '''
        Download boxscores for all of the game_ids provided

        Arguments:
            gids(list): nba.com game_ids
            season(str): in '2014-15' format
            box_type(str): ['base', 'advanced', 'both']

        Returns:
            boxes(dict): keys are the game_id, value is a dictionary with 'base' and 'adv' keys, that value is parsed json resource

        '''

        boxes = defaultdict(dict)
        box_types = ['base', 'advanced', 'both']

        if box_type.lower() not in box_types:
            raise ValueError('{0} is not a valid box_type'.format(box_type))

        for gid in gids:

            # transform to string with leading zeroes
            if len(gid) == 8:
                gid = '00{0}'.format(gid)

            # each game id has a key for base, advanced, or both
            if box_type in ('both', 'base'):
                content = self.boxscore(gid, season)
                boxes[gid]['base'] = content

                if save and savedir:
                    try:
                        fname = os.path.join(savedir, '{0}_box.json'.format(gid))

                        with open(fname, 'w') as outfile:
                            json.dump(content, outfile)
                    except:
                        logging.exception('could not save {0} to file'.format(gid))

            # each game id has a key for base and advanced box
            if box_type in ('both', 'advanced'):
                content = self.boxscore_advanced(gid)
                boxes[gid]['advanced'] = content

                if save and savedir:
                    try:
                        fname = os.path.join(savedir, '{0}_box_advanced.json'.format(gid))
                        with open(fname, 'w') as outfile:
                            json.dump(content, outfile)
                    except:
                        logging.exception('could not save {0} to file'.format(gid))

        return boxes

    def one_player_gamelogs(self, player_id, season, **kwargs):

        # step two: get player_gamelogs
        base_url = 'http://stats.nba.com/stats/playergamelog?'

        params = {
          'LeagueID': '00',
          'PlayerID': player_id,
          'Season': season,
          'SeasonType': 'Regular Season'
        }

        # override defaults with **kwargs
        for key, value in kwargs.iteritems():
            if params.has_key(key):
                params[key] = value

        content = self.get_json(url=base_url, payload=params)

        if not content: logging.error('could not get content: {0}'.format(base_url))

        return content

    def one_team_gamelogs(self, team_id, season):

        base_url = 'http://stats.nba.com/stats/teamgamelog?'

        params = {
          'LeagueID': '00',
          'TeamID': team_id,
          'Season': season,
          'SeasonType': 'Regular Season'
        }

        content = self.get_json(url=base_url, payload=params)

        if not content: logging.error('could not get content: {0}'.format(base_url))

        return content

    def player_info(self, player_id, season, **kwargs):

        player_info = None
        base_url = 'http://stats.nba.com/stats/commonplayerinfo?'

        params = {
          'LeagueID': '00',
          'PlayerID': player_id,
          'Season': season,
          'SeasonType': 'Regular Season'
        }

        # override defaults with **kwargs
        for key, value in kwargs.iteritems():
            if params.has_key(key):
                params[key] = value

        content = self.get_json(url=base_url, payload=params)

        if not content:
            logging.error('could not get content: {0}'.format(base_url))

        return content

    def players (self, season, cs_only=False):

        base_url = 'http://stats.nba.com/stats/commonallplayers?'

        # default is all players, can specify only this season
        params = {
          'IsOnlyCurrentSeason': '0',
          'LeagueID': '00',
          'Season': season,
        }

        if cs_only:
            params['IsOnlyCurrentSeason'] = 1

        content = self.get_json(url=base_url, payload=params)

        if not content: logging.error('could not get content: {0}'.format(base_url))

        return content

    def playerstats(self, season, **kwargs):
        '''
        Document has one line of stats per player

        Arguments:
            season(str): such as 2015-16

        Returns:
            content: parsed json response from nba.com
        '''

        base_url = 'http://stats.nba.com/stats/leaguedashplayerstats?'

        # measure_type allows you to choose between Base and Advanced
        # per_mode can be Totals or PerGame
        # date_from and date_to allow you to select a specific day or a range of days
        # last_n_games allows picking 3, 5, 10, etc. game window='2014-15',per_mode='Totals',season_type='Regular Season',date_from='',date_to='',measure_type='Base',
        # last_n_games=0,month=0,opponent_team_id=0

        params = {
          'DateFrom': '',
          'DateTo': '',
          'GameScope': '',
          'GameSegment': '',
          'LastNGames': '0',
          'LeagueID': '00',
          'Location': '',
          'MeasureType': 'Base',
          'Month': '0',
          'OpponentTeamID': '0',
          'Outcome': '',
          'PaceAdjust': 'N',
          'PerMode': 'Totals',
          'Period': '0',
          'PlayerExperience': '',
          'PlayerPosition': '',
          'PlusMinus': 'N',
          'Rank': 'N',
          'Season': season,
          'SeasonSegment': '',
          'SeasonType': 'Regular Season',
          'StarterBench': '',
          'VsConference': '',
          'VsDivision': ''
        }

        # override defaults with **kwargs
        for key, value in kwargs.iteritems():
            if params.has_key(key):
                params[key] = value

        content = self.get_json(url=base_url, payload=params)

        if not content: logging.error('could not get content from file or url\n' + fn + '\n' + url)

        return content

    def scoreboard(self, game_date, **kwargs):
        '''
        :param kwargs:
        :return: content(str): json response
        '''

        # setup
        base_url = 'http://stats.nba.com/stats/scoreboardV2?'

        params = {
          'DayOffset': '0',
          'LeagueID': '00',
          'GameDate': game_date,
        }

        # override defaults with **kwargs
        for key, value in kwargs.iteritems():
            if params.has_key(key):
                params[key] = value

        content = self.get_json(url=base_url, payload=params)

        if not content: logging.error('could not get content: {0}'.format(base_url))

        return content

    def season_gamelogs(self, season, player_or_team, **kwargs):

        base_url = 'http://stats.nba.com/stats/leaguegamelog?'

        params = {
          'Counter': '0',
          'Direction': 'DESC',
          'LeagueID': '00',
          'PlayerOrTeam': player_or_team,
          'Season': season,
          'SeasonType': 'Regular Season',
          'Sorter': 'PTS'
        }

        # override defaults with **kwargs
        for key, value in kwargs.iteritems():
            if params.has_key(key):
                params[key] = value

        content = self.get_json(url=base_url, payload=params)

        if not content:
            logging.error('could not get content: {0}'.format(url))

        return content

    def team_dashboard(self, team_id, season, **kwargs):
        '''
          measure_type allows you to choose between Base and Advanced
          per_mode can be Totals or PerGame
          date_from and date_to allow you to select a specific day or a range of days
          last_n_games allows picking 3, 5, 10, etc. game window
        '''

        base_url = 'http://stats.nba.com/stats/teamdashboardbygeneralsplits?'

        params = {
          'DateFrom': '',
          'DateTo': '',
          'GameSegment': '',
          'LastNGames': '0',
          'LeagueID': '00',
          'Location': '',
          'MeasureType': 'Base',
          'Month': '0',
          'OpponentTeamID': '0',
          'Outcome': '',
          'PORound': '0',
          'PaceAdjust': 'N',
          'PerMode': 'PerGame',
          'Period': '0',
          'PlusMinus': 'N',
          'Rank': 'N',
          'Season': season,
          'SeasonSegment': '',
          'SeasonType': 'Regular Season',
          'ShotClockRange': '',
          'TeamID': team_id,
          'VsConference': '',
          'VsDivision': ''
        }

        # override defaults with **kwargs
        for key, value in kwargs.iteritems():
            if params.has_key(key):
                params[key] = value

        content = self.get_json(url=base_url, payload=params)

        # if not from web either, then log an error
        if not content:
            logging.error('could not get content: {0}'.format(base_url))

        return content

    def team_opponent_dashboard(self, season, **kwargs):
        '''
        Returns team_opponent stats for every team in league
        '''

        base_url = 'http://stats.nba.com/stats/leaguedashteamstats?'

        params = {
          'DateFrom': '',
          'DateTo': '',
          'GameSegment': '',
          'LastNGames': '0',
          'LeagueID': '00',
          'Location': '',
          'MeasureType': 'Opponent',
          'Month': '0',
          'OpponentTeamID': '0',
          'Outcome': '',
          'PORound': '0',
          'PaceAdjust': 'N',
          'PerMode': 'PerGame',
          'Period': '0',
          'PlusMinus': 'N',
          'Rank': 'N',
          'Season': season,
          'SeasonSegment': '',
          'SeasonType': 'Regular Season',
          'ShotClockRange': '',
          'TeamID': '0',
          'VsConference': '',
          'VsDivision': ''
        }

        # override defaults with **kwargs
        for key, value in kwargs.iteritems():
            if params.has_key(key):
                params[key] = value

        content = self.get_json(url=base_url, payload=params)
        self.logger.debug(self.responses[:-1])

        # if not from web either, then log an error
        if not content: logging.error('could not get content: {0}'.format(base_url))

        return content

    def teams(self):
        '''
        nba.com stores team_id and team_code as a variable in a javascript file

        Arguments:
            None

        Returns:
            javascript file with js variable containing team_ids and team names

        '''

        url = 'http://stats.nba.com/scripts/custom.min.js'
        content = self.get(url)

        # if not from web either, then log an error
        if not content:
            logging.error('could not get content: {0}'.format(url))

        return content

    def teamstats(self, season, **kwargs):
        '''
          measure_type allows you to choose between Base and Advanced
          per_mode can be Totals or PerGame
          date_from and date_to allow you to select a specific day or a range of days
          last_n_games allows picking 3, 5, 10, etc. game window
        '''

        base_url = 'http://stats.nba.com/stats/leaguedashteamstats?'

        params = {
          'DateFrom': '',
          'DateTo': '',
          'GameScope': '',
          'GameSegment': '',
          'LastNGames': '0',
          'LeagueID': '00',
          'Location': '',
          'MeasureType': 'Base',
          'Month': '0',
          'OpponentTeamID': '0',
          'Outcome': '',
          'PaceAdjust': 'N',
          'PerMode': 'PerGame',
          'Period': '0',
          'PlayerExperience': '',
          'PlayerPosition': '',
          'PlusMinus': 'N',
          'Rank': 'N',
          'Season': season,
          'SeasonSegment': '',
          'SeasonType': 'Regular Season',
          'ShotClockRange': '',
          'StarterBench': '',
          'TeamID': '0',
          'VsConference': '',
          'VsDivision': ''
        }

        # override defaults with **kwargs
        for key, value in kwargs.iteritems():
            if params.has_key(key):
                params[key] = value

        content = self.get_json(url=base_url, payload=params)

        if not content: logging.error('could not get content: {0}'.format(base_url))

        return content

if __name__ == "__main__":
    pass
