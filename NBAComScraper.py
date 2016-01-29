'''
NBAComScraper

'''

import logging

from EWTScraper import EWTScraper


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
        logging.getLogger(__name__).addHandler(logging.NullHandler())

    def boxscore(self, game_id, season):
        '''

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

        if not content: logging.error('could not get content from url: {0}'.format(url))

        return content

    def player_stats(self, season, **kwargs):
        '''
          measure_type allows you to choose between Base and Advanced
          per_mode can be Totals or PerGame
          date_from and date_to allow you to select a specific day or a range of days
          last_n_games allows picking 3, 5, 10, etc. game window='2014-15',per_mode='Totals',season_type='Regular Season',date_from='',date_to='',measure_type='Base',
        last_n_games=0,month=0,opponent_team_id=0
        '''

        base_url = 'http://stats.nba.com/stats/leaguedashplayerstats?'

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
            logging.error('could not get content: {0}'.format(url))

        return content

    def player_game_logs(self, player_id, season, **kwargs):

        # NOTE: need 2nd URL to match up player info to PlayerID
        # http://stats.nba.com/stats/commonplayerinfo?LeagueID=00&PlayerID=203112&SeasonType=Regular+Season
        # then call URL for the gamelogs
        # http://stats.nba.com/stats/playergamelog?LeagueID=00&PlayerID=203112&Season=2014-15&SeasonType=Regular+Season

        # step one: get commonplayerinfo
        player_info = self.player_info(player_id)

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

        return content, player_info

    def players (self, season, **kwargs):

        base_url = 'http://stats.nba.com/stats/commonallplayers?'

        params = {
          'IsOnlyCurrentSeason': '0',
          'LeagueID': '00',
          'Season': season,
        }

        # override defaults with **kwargs
        for key, value in kwargs.iteritems():
            if params.has_key(key):
                params[key] = value

        content = self.get_json(url=base_url, payload=params)

        if not content: logging.error('could not get content: {0}'.format(base_url))

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

    def team_game_logs(self, team_id, season):

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

        # if not from web either, then log an error
        if not content: logging.error('could not get content: {0}'.format(base_url))

        return content

    def team_stats(self, season, **kwargs):
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

    def teams(self):
        '''
        Returns javascript file with js variable containing team_ids and team names
        :return: content(str)
        '''

        url = 'http://stats.nba.com/scripts/custom.min.js'
        content = self.get(url)

        # if not from web either, then log an error
        if not content:
            logging.error('could not get content: {0}'.format(url))

        return content

if __name__ == "__main__":
    pass
