#!/usr/bin/python

'''
nba_team_stats.py
Downloads and saves daily team stats
'''

from collections import OrderedDict
import datetime
import logging
import pickle
import time

from NBAComParser import NBAComParser
from NBAComScraper import NBAComScraper

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

def get_teamstats_day(s, season):
    '''
    Season is main parameter
    :param s (NBAComScraper): scraper object
    :param season (dict): has code, start, end, and day
    :return content (dict): has base, advanced, opponent
    '''

    content = {'base': {}, 'advanced': {}, 'opponent': {}}
    content['base'] = s.team_stats(season['code'], DateFrom=season['start'], DateTo=season['day'], Measure='Base')
    content['advanced'] = s.team_stats(season['code'], DateFrom=season['start'], DateTo=season['day'], Measure='Advanced')
    content['opponent'] = s.team_opponent_dashboard(season['code'], DateFrom=season['start'], DateTo=season['day'])

    return content

def nba_seasons():
    return [
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

if __name__ == '__main__':
    '''
    Describe how script works here
    I think I want to use ordereddict to keep seasons in order
    '''

    logging.basicConfig(level=logging.DEBUG, handler=logging.StreamHandler())

    # dictionary of season and then days: {'2015-16': {'2015-10-30': parsed_content}, . . . }
    results = OrderedDict()

    s = NBAComScraper()
    p = NBAComParser()

    seasons = nba_seasons()

    for seas in seasons:
        season_code = seas.get('season', None)

        if season_code:
            season_end = seas.get('end', None)
            season_start = seas.get('start', None)

            if season_start and season_end:

                # date_list returns order of newest to oldest, reverse list so oldest to newest
                #season_dates = reversed(date_list(season_end, season_start))
                season_dates = date_list(season_end, season_start)

                # probably want ordered dict for values so in date order from 1st day of season to last???
                for datestr in [datetime.datetime.strftime(d, '%Y-%m-%d') for d in season_dates]:
                    content = get_teamstats_day(s, season={'code': season_code, 'start': season_start, 'end': season_end, 'day': datestr})
                    results.setdefault(season_code, {})
                    results[season_code][datestr] = content
		    time.sleep(1)

with open('nba_team_stats.pkl', 'wb') as outfile:
    pickle.dump(results, outfile)
