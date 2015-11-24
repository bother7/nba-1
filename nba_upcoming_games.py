'''
nba_upcoming_games.py

lines/implied totals
team-level stats for each game
player reports for each game
include advanced stats like rebound rate, usage, etc.
'''

import logging
import pprint
import time

from Emailer import Emailer
from NBAComParser import NBAComParser
from NBAComScraper import NBAComScraper
from NBATeamNames import NBATeamNames
from PinnacleNBAParser import PinnacleNBAParser
from PinnacleNBAScraper import PinnacleNBAScraper


def headers_data(games):
    headers = ['display_date', 'game_total', 'home_team', 'home_total', 'away_team', 'away_total']
    data = [[game.get(k, 'N/A') for k in headers] for game in games]
    return headers, data

def get_dashboards(games, scoreboard, nbap, nbat):
    '''
        Games is a list of game dictionaries (from pinnacle XML feed)
        Scoreboard is a dictionary of information about daily games (from nba.com)
        nbap is a NBAComParser instance
        nbat is a NBATeamNames instance

        Dashboards is a dictionary, keys are 3-letter team codes (ATL)
        Value is a dashboard (dictionary) with keys: parameters, overall, location, days_rest, wins_losses
        The value of each key is a list of dictionaries
        parameters: 1 item in list
        overall: 1 item in list
        location: 2 items - home and away
        days_rest: multiple items that vary - 0 days, 1 day, 2 days, 3 days, 4 days
        wins_losses: 2 items - wins and losses
    '''

    dashboards = {}

    # gamecode used to match games in the games dictionary from pinnacle and the nba.com scoreboard
    # in format YYYYMMDD/AWAY_CODEHOME_CODE (20151101/CHADET)

    gamecodes = [h.get('GAMECODE', None) for h in scoreboard['game_headers']]

    for gc in gamecodes:
        for game in games:

            # if match, then we get the teamdashboard for the away and home teams
            # add the dashboard by 3-letter key (ATL) to the dashboards dictionary
            if game.get('nbacom_gamecode', None) == gc:
                away = game.get('away_team', None)
                home = game.get('home_team', None)
                away_code = nbat.nbacom_short_to_code(away)
                home_code = nbat.nbacom_short_to_code(away)
                dashboards[away] =  nbap.team_dashboard(nbas.team_dashboard(team_id=away_code, season=season))
                dashboards[home] =  nbap.team_dashboard(nbas.team_dashboard(team_id=home_code, season=season))

    return dashboards

def get_games(s, p, today):
    xml = s.odds()
    return p.odds(xml, today)

def get_scoreboard(s, p):
    '''
    Uses NBAScraper and NBAParser to get scoreboard dictionary
    '''
    content = s.scoreboard(game_date=today)

    if content:
        return p.scoreboard(content, today)

    else:
        return None

if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR, handler=logging.StreamHandler())
    today = time.strftime("%Y-%m-%d")
    season = '2015-16'

    s = PinnacleNBAScraper() # use_cache=False
    p = PinnacleNBAParser()
    e = Emailer()

    # step one: list of games and odds
    games = get_games(s, p, today)
    print p.to_csv(games)

    # step two: matchup information
    nbas = NBAComScraper()
    nbap = NBAComParser()
    nbat = NBATeamNames()
    #scoreboard = get_scoreboard(nbap, nbas)
    #dashboards = get_dashboards(games, scoreboard, nbap, nbat)

    # now assemble the report
    #e.send(['eric.truett@gmail.com'], 'NBA Daily Report', e.html_table(headers, data))