# -*- coding: utf-8 -*-
'''
nba_list_games.py

Examples:
    dirname = '/home/sansbacon/scoreboards'
    season_scoreboards(season_start='10-28-2003',season_end='04-14-2004',dirname=dirname)
    games = parse_scoreboards(parser, dirname)
    fixed_games = fix_games(games)
    save_games(db, fixed_games)

'''

import argparse
from collections import OrderedDict
import datetime
import fnmatch
import glob
import logging
import os
from os.path import expanduser
import re
import sys
import time

try:
    import cPickle as pickle
except:
    import pickle

import MySQLdb

sys.path.append("/home/sansbacon/workspace/nbacom-python/lib")
from NBAComScraper import NBAComScraper
from NBAComParser import NBAComParser

def date_list(d1,d2):
  # need to first determine if date object or datestring
  if isinstance(d1, basestring):
    d1 = datetime.datetime.strptime(d1, '%m-%d-%Y')

  if isinstance(d2, basestring):
    d2 = datetime.datetime.strptime(d2, '%m-%d-%Y')

  # calculate difference between two dates
  # then have to add one to season.days to get the earliest date in the list
  season = d1-d2
  return [d1 - datetime.timedelta(days=x) for x in range(0, season.days+1)]

def db_setup():
    host = os.environ['MYSQL_NBA_HOST']
    user = os.environ['MYSQL_NBA_USER']
    password = os.environ['MYSQL_NBA_PASSWORD']
    database = os.environ['MYSQL_NBA_DATABASE']
    return MySQLdb.connect(host=host, user=user, passwd=password, db=database)

def fix_games(games):

    fixed_games = []
    include = ['game_date_est', 'game_id', 'gamecode', 'home_team_id', 'season', 'visitor_team_id']

    for game in games:
        fixed_game = {k.lower():v for k,v in game.items() if k.lower() in include}

        if fixed_game.has_key('season'):
            season = int(fixed_game['season']) + 1
            fixed_game['season'] = season
            gamecode_teams = fixed_game['gamecode'].split('/')[-1]
            fixed_game['visitor_team_code'] = gamecode_teams[0:3]
            fixed_game['home_team_code'] = gamecode_teams[3:6]
            fixed_games.append(fixed_game)

    return fixed_games

def game_linescores(parser, dirname, pattern):
    linescores = []

    # get all of the filenames
    for root, dirnames, filenames in os.walk(dirname):
        for filename in fnmatch.filter(filenames, pattern):
            try:
                fn = os.path.join(root, filename)
                with open(fn, 'r') as infile:
                    content = infile.read()
                scoreboard = parser.scoreboard(content=content)
                linescores += scoreboard['game_linescores']

            except:
                logging.error('could not open {0}'.format(fn))

    return linescores

def get_options():
  opt_parser = argparse.ArgumentParser(description='This is the parser for nba-scraper script')
  opt_parser.add_argument('--start_date', dest="start_date")
  opt_parser.add_argument('--end_date', dest="end_date")
  return opt_parser.parse_args()

def get_scoreboards(scraper, date_list):

  scoreboards = {}

  for day in date_list:
    # convert date object to YYYY-MM-DD format
    game_date = datetime.datetime.strftime(day, "%Y-%m-%d")
    scoreboard_content = scraper.scoreboard(game_date=game_date)
    fn = 'nba_2014_scoreboard_{0}.json'.format(game_date)

    scoreboards[game_date] = scoreboard_content

    with open(fn, 'w') as outfile:
        outfile.write(scoreboard_content)

    time.sleep(.5)

  return scoreboards

def parse_scoreboards(parser, dirname):

    games = []

    for fullpath in glob.glob('{0}/*.json'.format(dirname)):
        pattern = re.compile(r'(\d+[-]+\d+[-]+\d+)_scoreboard\.json')
        match = re.search(pattern, fullpath)

        if match:
            game_date = match.group(1)

            with open(fullpath, 'r') as infile:
                scoreboard = parser.scoreboard(content=infile.read(), game_date=game_date)
                games += scoreboard['game_headers']

    return games


def save_games(db, all_games):
    cursor = db.cursor()

    placeholders = ', '.join(['%s'] * len(all_games[0]))
    columns = ', '.join(all_games[0].keys())
    sql = "INSERT INTO %s ( %s ) VALUES ( %s )" % ('games', columns, placeholders)

    for game in all_games:
        cursor.execute(sql, game.values())

    db.commit()

def save_linescores(db, linescores):

    cursor = db.cursor()

    for linescore in linescores:

        try:
            placeholders = ', '.join(['%s'] * len(linescore))
            columns = ', '.join(linescore.keys())
            sql = "INSERT INTO %s ( %s ) VALUES ( %s )" % ('game_linescores', columns, placeholders)
            cursor.execute(sql, linescore.values())

        except MySQLdb.Error, e:
            logging.error('could not insert linescore %s: %s' % (linescore.get('gamecode'), e))

    db.commit()

def setup_log():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler()])
    return logging.getLogger(__name__)

def season_scoreboards(season_start, season_end, dirname):
    for date in date_list(season_end, season_start):
        game_date = datetime.datetime.strftime(date, '%m-%d-%Y')
        scoreboard = scraper.scoreboard(game_date=game_date)
        fn = '{0}/{1}_scoreboard.json'.format(dirname, game_date)
        with open(fn, 'w') as outfile:
            outfile.write(scoreboard)

def fix_linescores(linescores):

    fixed_linescores = []
    exclude = ['game_sequence']

    for linescore in linescores:
        fixed_linescore = {k.lower():v for k,v in linescore.items()}
        fixed_linescore.pop('game_sequence', None)

        fixed_linescore['team_game_id'] = '{0}:{1}'.format(fixed_linescore['team_id'], fixed_linescore['game_id'])
        twl = fixed_linescore.get('team_wins_losses', None)

        if twl:
            wins, losses = twl.split('-')

            if wins and losses:
                fixed_linescore['team_wins'] = wins
                fixed_linescore['team_losses'] = losses

        fixed_linescores.append(fixed_linescore)

    return fixed_linescores

def save_season_gamelogs(db, gamelogs):

    cursor = db.cursor()

    for gl in gamelogs:

        exclude = ['team_name', 'video_available']
        gl = {k:v for k,v in gl.items() if k not in exclude}

        try:
            placeholders = ', '.join(['%s'] * len(gl))
            columns = ', '.join(gl.keys())
            sql = "INSERT INTO %s ( %s ) VALUES ( %s )" % ('team_gamelogs', columns, placeholders)
            cursor.execute(sql, gl.values())

        except MySQLdb.Error, e:
            logging.error('could not insert gamelog: %s' % e)

    db.commit()

def season_gamelogs(scraper, parser, season, player_or_team):
    '''
    '''

    content = scraper.season_gamelogs(season=season, player_or_team=player_or_team)
    gamelogs = parser.season_gamelogs(content=content, season=int(season[:4]) + 1, player_or_team=player_or_team)
    logging.debug('found {0} gamelogs for {1}'.format(len(gamelogs), season))
    team_gamelogs = []

    seasons = ['2014-15', '2013-14', '2012-13', '2011-12', '2010-11', '2009-10', '2008-09', '2007-08', '2006-07', '2005-06', '2004-05', '2003-04', '2002-03', '2001-02', '2000-01', '1999-00']
    for season in seasons:
        team_gamelogs += season_gamelogs(scraper, parser, season, 'T')

    try:
        with open(os.path.join(expanduser("~"),'gamelogs.pkl'), 'w') as outfile:
            pickle.dump(team_gamelogs, outfile)

    except TypeError, e:
        logging.error(e.message())

    save_season_gamelogs(db, team_gamelogs)

def team_stats_game(scraper, parser):
    pass

def save_teamstats_game(db, teamstats):

    cursor = db.cursor()

    for team in teamstats:

        try:
            placeholders = ', '.join(['%s'] * len(team))
            columns = ', '.join(team.keys())
            sql = "INSERT INTO %s ( %s ) VALUES ( %s )" % ('team_stats_game', columns, placeholders)
            cursor.execute(sql, team.values())

        except MySQLdb.Error, e:
            logging.error('could not insert linescore: %s' % e)

    db.commit()

if __name__ == "__main__":
    scraper = NBAComScraper(dldir='/home/sansbacon/teamstats')
    parser = NBAComParser()
    log = setup_log()
    db = db_setup()

    seasons = ['2014-15', '2013-14', '2012-13', '2011-12', '2010-11', '2009-10', '2008-09', '2007-08', '2006-07', '2005-06', '2004-05', '2003-04', '2002-03', '2001-02', '2000-01', '1999-00']

    season_start_end = {
        '1999-00': ['11-02-1999', '04-19-2000'],
        '2000-01': ['10-31-2000', '04-18-2001'],
        '2001-02': ['10-30-2001', '04-17-2002'],
        '2002-03': ['10-29-2002', '04-16-2003'],
        '2003-04': ['10-28-2003', '04-14-2004'],
        '2004-05': ['11-02-2004', '04-20-2005'],
        '2005-06': ['11-01-2005', '04-19-2006'],
        '2006-07': ['10-31-2006', '04-18-2007'],
        '2007-08': ['10-30-2007', '04-16-2008'],
        '2008-09': ['10-28-2008', '04-16-2009'],
        '2009-10': ['10-27-2009', '04-14-2010'],
        '2010-11': ['10-26-2010', '04-13-2011'],
        '2011-12': ['12-25-2011', '04-26-2012'],
        '2012-13': ['10-30-2012', '04-17-2013'],
        '2013-14': ['10-29-2013', '04-16-2014'],
        '2014-15': ['10-28-2014', '04-15-2015'],
        '2015-16': None
    }

    all_teamstats = []

    for season in seasons:

        dates = season_start_end.get(season, None)

        if dates:
            season_start = dates[0]
            season_end = dates[1]

            for day in reversed(date_list(season_end, season_start)):
                date_to = datetime.datetime.strftime(day, '%m-%d-%Y')
                content = scraper.team_stats(season, date_from=season_start, date_to=date_to, measure_type='Advanced')
                teamstats = parser.team_stats(content, stat_date=date_to)

                for teamstat in teamstats:
                    all_teamstats.append(teamstat)

    with open('/home/sansbacon/all_teamstats_advanced.pkl', 'w') as outfile:
        pickle.dump(all_teamstats, outfile)
