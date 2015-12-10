#!/usr/bin/python
# nbacom_fetch_boxscores.py
import argparse
import datetime
import pprint
import logging
import sys
sys.path.append("/home/sansbacon/workspace/nbacom-python/lib")
from NBAComScraper import NBAComScraper
from NBAComParser import NBAComParser
from NBADailyFantasy import NBADailyFantasy

def setup_log(verbose=False):
    if verbose:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler()])
    else:
        logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler()])

    return logging.getLogger(__name__)

# this is goofy, all should be a flag rather than a value
def script_arguments():
    parser = argparse.ArgumentParser(description='This is the parser for nba-scraper script')
    parser.add_argument('--later_date', dest="later_date", help='date in mm-dd-yyyy format')
    parser.add_argument('--earlier_date', dest="earlier_date", help='date in mm-dd-yyyy format')
    parser.add_argument('--later_season', dest="later_season", help='season in yyyy-yy format')
    parser.add_argument('--earlier_season', dest="earlier_season", help='season in yyyy-yy format')
    parser.add_argument('--all', action='store_true', help='all seasons (bootstrap)')
    parser.add_argument('--verbose', action='store_true', help='verbose flag' )
    return parser.parse_args()

def date_list(d1,d2):
    # need to first determine if date object or datestring
    if isinstance(d1, basestring):
        d1 = datetime.datetime.strptime(d1, '%m-%d-%Y')

    if isinstance(d2, basestring):
        d2 = datetime.datetime.strptime(d2, '%m-%d-%Y')

    # calculate difference between two dates
    # then have to add one to season.days to get the earliest date in the list
    season = d1-d2
    dates = [d1 - datetime.timedelta(days=x) for x in range(0, season.days+1)]
    return dates

def find(lst, key, value):
    for i, dic in enumerate(lst):
        if dic[key] == value:
            return i
    return -1

def get_content(date_list):

    scoreboards = []
    player_boxscores = []
    team_boxscores = []

    for day in date_list:
        # convert date object to YYYY-MM-DD format
        game_date = datetime.datetime.strftime(day, "%Y-%m-%d")
        scoreboard_content, scoreboard_url = scraper.scoreboard(game_date=game_date)
        scoreboard = parser.scoreboard(scoreboard_content, game_date=game_date)
        scoreboards.append(scoreboard)

        for game in scoreboard['game_headers']:
            box_score, dbg = scraper.boxscore(game['GAME_ID'],game_date=game_date)
            players, teams = parser.boxscore(box_score,game_date=game_date)
            player_boxscores.extend(players)
            team_boxscores.extend(teams)
                
    return player_boxscores, team_boxscores, scoreboards

if __name__ == "__main__":
    # setup variables
    opts = script_arguments()
    log = setup_log(opts.verbose)
    scraper = NBAComScraper(logger=log)
    parser = NBAComParser(logger=log)

    # this is the giant loop
    nba_seasons = [
        {"season": "2014-15", "start": "10-28-2014", "end": "04-15-2015"},
        {"season": "2013-14", "start": "10-29-2013", "end": "04-16-2014"},
        {"season": "2012-13", "start": "10-30-2012", "end": "04-17-2013"},
        {"season": "2011-12", "start": "11-25-2011", "end": "04-26-2012"},
        {"season": "2010-11", "start": "10-26-2010", "end": "04-13-2011"},
        {"season": "2009-10", "start": "10-27-2009", "end": "04-14-2010"},
        {"season": "2008-09", "start": "10-28-2008", "end": "04-15-2009"},
        {"season": "2007-08", "start": "10-30-2007", "end": "04-16-2008"},
        {"season": "2006-07", "start": "10-31-2006", "end": "04-18-2007"},
        {"season": "2005-06", "start": "11-1-2005", "end": "04-19-2006"},
        {"season": "2004-05", "start": "11-2-2004", "end": "04-20-2005"},
        {"season": "2003-04", "start": "10-28-2003", "end": "04-14-2004"},
        {"season": "2002-03", "start": "10-29-2002", "end": "04-16-2003"},
        {"season": "2001-02", "start": "10-30-2001", "end": "04-17-2002"},
        {"season": "2000-01", "start": "10-31-2000", "end": "04-18-2001"},
        {"season": "1999-00", "start": "11-2-1999", "end": "4-19-2000"},
        {"season": "1998-99", "start": "2-5-1999", "end": "5-5-1999"},
        {"season": "1997-98", "start": "10-31-1997", "end": "4-19-1998"},
        {"season": "1996-97", "start": "11-1-1996", "end": "4-20-1997"}
    ]
    
    # do the whole thing
    if opts.all:
        for s in nba_seasons:
            log.debug(s)
            dates = date_list(s['end'], s['start'])
    
    elif opts.later_season and opts.earlier_season:
        start_index = find(nba_seasons, 'season', opts.later_season)
        end_index = find(nba_seasons, 'season', opts.earlier_season)
        log.debug("%s %s" % (start_index, end_index))
        for idx in range(start_index, end_index + 1):
            log.debug(nba_seasons[idx])

    else:
        dates = date_list(opts.later_date,opts.earlier_date)
        if dates:
            log.debug(dates)
            #player_boxscores, team_boxscores, scoreboards = get_content(dates)
            #logging.debug(pprint.pprint(player_boxscores))
            #logging.debug(pprint.pprint(team_boxscores))
            #pprint.pprint(scoreboards)