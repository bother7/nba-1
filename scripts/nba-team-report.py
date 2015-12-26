'''
nba-team-report.py

Gets basic stats about teams for upcoming games

Usage:
    python nba-team-report.py


'''

import collections
from datetime import date, timedelta
import datetime
import logging
from operator import itemgetter
import pprint

from NBAComParser import NBAComParser
from NBAComScraper import NBAComScraper
from PinnacleNBAParser import PinnacleNBAParser
from PinnacleNBAScraper import PinnacleNBAScraper

def combine_games(nbagames, pinnacleodds):
    '''
    Merges pinnacleodds dictionary with nbagames list of lists

    Args:
        nbagames (list): list of 3-element lists (gamecode, away_team_code, home_team_code)
        pinnacleodds (list): list of dictionaries of game info and spread / total

    Returns:
        list: of dictionaries representing games
    '''

    combinedgames = []
    for nbagame in nbagames:
        for pinnacleodd in pinnacleodds:
            if nbagame[0] and nbagame[0] == pinnacleodd.get('nbacom_gamecode', None):
                combinedgame = pinnacleodd
                if nbagame[1]: combinedgame['nbacom_visitor_team_id'] = nbagame[1]
                if nbagame[2]: combinedgame['nbacom_home_team_id'] = nbagame[2]
                combinedgames.append(combinedgame)
                break

    return combinedgames

def nba_games(scraper, parser, game_date):
    content = scraper.scoreboard(game_date=game_date)
    results = parser.scoreboard(content)
    return [[g.get('GAMECODE'), g.get('VISITOR_TEAM_ID'), g.get('HOME_TEAM_ID')] for g in results.get('game_headers')]

def team_dashboard(scraper, parser, team_id):
    '''
    Team dashboard is nba.com container for team stats, can request 'base' or 'advanced' stats. We want some of both.
    '''
     
    dashboard_base = parser.team_dashboard(scraper.team_dashboard(team_id, '2015-16'))
    dashboard_advanced = parser.team_dashboard(scraper.team_dashboard(team_id, '2015-16', MeasureType='Advanced'))
    
    return {
        'base': dashboard_base.get('overall', None),
        'advanced': dashboard_advanced.get('overall', None),
    }

def main():
    '''

    Step 1: get list of games from nba.com
    Step 2: get spreads / odds from pinnacle.com
    Step 3: reconcile game list and odds
    '''
    
    nbaparser = NBAComParser()
    nbascraper = NBAComScraper()
    pinnacleparser = PinnacleNBAParser()
    pinnaclescraper = PinnacleNBAScraper(use_cache=False)

    # step one: get list of list of games: GAMECODE, VISITOR_TEAM_ID, HOME_TEAM_ID
    #today = datetime.datetime.strftime(datetime.datetime.today(), '%Y-%m-%d')
    today = datetime.datetime.strftime(date.today() - timedelta(1), '%Y-%m-%d')
    nbagames = nba_games(nbascraper, nbaparser, today)
    pprint.pprint(nbagames)
    
    # step two: reconcile game list with game totals / spreads
    pinnaclexml = pinnaclescraper.odds()
    pinnacleodds = pinnacleparser.odds(pinnaclexml, today)
    pprint.pprint(pinnacleodds)
    #print [g.get('nbacom_gamecode', None) for g in pinnacleodds]

    # step three: reconcile game list with game totals / spreads
    # if need sorted results, use combinedgames.sort(key=itemgetter('start'))
    #combinedgames = combine_games(nbagames, pinnacleodds)

    #

    '''    # step four: get team dashboards from nba.com
    dashboards = {}
    for game in combinedgames:
        gamecode = game.get('nbacom_gamecode', None)

        if gamecode:
            away_dashboard = team_dashboard(nbascraper, nbaparser, game.get('nbacom_visitor_team_id', None))
            home_dashboard = team_dashboard(nbascraper, nbaparser, game.get('nbacom_home_team_id', None))
            dashboards[gamecode] = [away_dashboard, home_dashboard]

    pprint.pprint(dashboards)


    # step XX: print report

    # gets unique game times and number of games, can sort earliest to latest
    c = collections.Counter([g.get('display_date', None) for g in combinedgames])
    for k,v in sorted(c.items()):
        header = '{0} - {1} games'.format(k, v)
        print '*' * len(header), '\n', header, '\n', '*' * len(header), '\n\n'

        for game in combinedgames:
            if game.get('display_date', None) == k:
                firstline = '{0} ({1}) vs. {2} ({3}) : Total {4}'.format(game.get('away_team', None), game.get('away_total', None), game.get('home_team', None), game.get('home_total', None), game.get('game_total', None))
                print '-' * len(firstline)
                print firstline
                print '-' * len(firstline), '\n'
                
            # still need to add spread_away and spread_home to the report
    '''
    '''
    # go through away and home teams in each game
    # dashboard = {'parameters': [], 'overall': [], 'location': [], 'days_rest': [], 'wins_losses': []}
    # overall_base: typical counting stats, plus_minus
    # overall_advanced: ast_pct, ast_ratio, def_rating, dreb_pct, efg_pct, net_rating, off_rating, oreb_pct, pace, reb_pct, tm_tov_pct

    # TODO: format team report
    # set TeamID parameter to get all players from a team: TeamID=1610612737
    player_stats = {}

    for game in games:
	gamecode, away_team_id, home_team_id = game 
	
	player_stats[gamecode] = []

	# TODO: get player stats

	away_players = parser.
	for , teams in team_stats.items():
	away_team = 
    '''
    
if __name__ == '__main__':
    main()
