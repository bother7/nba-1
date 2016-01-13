'''
nba_bootstrap_scoreboards.py
gets all of the scoreboards through yesterday's date
can delete when fully integrated into NBAComAgent class
'''

import datetime
import logging
import os
import pprint
import time

try:
    import cPickle as pickle
except:
    import pickle

import MySQLdb

from NBAComParser import NBAComParser
from NBAComScraper import NBAComScraper
from NBAMySQL import NBAMySQL


def date_list(d1,d2):
  # need to first determine if date object or datestring
  if isinstance(d1, basestring):
    d1 = datetime.datetime.strptime(d1, '%Y-%m-%d')

  if isinstance(d2, basestring):
    d2 = datetime.datetime.strptime(d2, '%Y-%m-%d')

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

def get_scoreboards(scraper, date_list, save=False):
    '''
    Arguments:
        scraper(NBAComScraper):
        date_list(list): list of date_time objects from newest to oldest?
        save(bool): set as true if want to save files to disk

    Return:
        scoreboards(dict): keys are datestring, value is scoreboard HTML
    '''

    scoreboards = {}

    for day in date_list:     
        game_date = datetime.datetime.strftime(day, "%Y-%m-%d")
        scoreboard_content = scraper.scoreboard(game_date=game_date)
        scoreboards[game_date] = scoreboard_content

        if save: 
            fn = 'nba_2015-16_scoreboard_{0}.json'.format(game_date)

            with open(fn, 'w') as outfile:
                outfile.write(scoreboard_content)

        time.sleep(1)
        
    return scoreboards

def parse_scoreboards(parser, sbs=None, game_date=None):
    '''
    Arguments:
        scraper(NBAComScraper):
        date_list(list): list of date_time objects from newest to oldest?
        save(bool): set as true if want to save files to disk

    Return:
        scoreboards(dict): keys are datestring, value is scoreboard HTML
    '''

    scoreboards = []

    for day, scoreboard in scoreboards.iteritems():
        scoreboards.append(parser.scoreboard(content=scoreboard, game_date=game_date))

    return scoreboards

def save_linescores(db, table_name, linescores):
    
    cursor = db.cursor()
    placeholders = ', '.join(['%s'] * len(linescores[0]))
    columns = ', '.join(linescores[0].keys())
    sql = "INSERT INTO %s ( %s ) VALUES ( %s )" % (table_name, columns, placeholders)

    for linescore in linescores:

        try:
            cursor.execute(sql, linescore.values())

        except MySQLdb.Error, e:
            logging.error('could not insert linescore %s: %s' % (linescore.get('gamecode'), e))

    db.commit()

if __name__ == "__main__":
    scraper = NBAComScraper()
    parser = NBAComParser()
    db = db_setup()
    season_start = '2015-10-27'
    season_end = datetime.datetime.strftime(datetime.date.today() - datetime.timedelta(1), '%Y-%m-%d')
    scoreboards = []

    for day in reversed(date_list(season_end, season_start)):
        game_date = datetime.datetime.strftime(day, '%Y-%m-%d')
        scoreboard_json = scraper.scoreboard(game_date=game_date)
        scoreboard = parser.scoreboard(scoreboard_json, game_date=game_date)
        scoreboards.append(scoreboard)       

    with open('/home/sansbacon/scoreboards_20160108.pkl', 'wb') as outfile:
        pickle.dump(scoreboards, outfile)

    
