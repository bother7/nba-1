#!/usr/env python
'''
#rotoguru-nba.py

'''

import datetime
import logging
import cPickle as pickle
import pprint
import time

from EWTFantasyTools import EWTFantasyTools
from NBASeasons import NBASeasons
from RotoGuruNBAScraper import RotoGuruNBAScraper

def current_season_data(s, site, polite=True):
    n = NBASeasons()
    ft = EWTFantasyTools()
    season = n.season('2015-16')

    contents = {}
    d1 = datetime.datetime.strftime(datetime.datetime.today()- datetime.timedelta(1), '%Y%m%d')
    d2 = season['start']
    dformat = '%Y%m%d'
    
    for d in ft.date_list(d1, d2, dformat):
        content = s.salaries_day(d, site)

        if content:
            contents[d] = content

        if polite:
            time.sleep(1)
        
    return contents

def get_season_data(s, site, seasonstr, polite=True):
    n = NBASeasons()
    ft = EWTFantasyTools()
    season = n.season(seasonstr)

    contents = {}
    
    for d in ft.date_list(season['end'], season['start'], '%Y%m%d'):
        content = s.salaries_day(d, site)

        if content:
            contents[d] = content

        if polite:
            time.sleep(1)
        
    return contents

def get_season_salaries(s, season, polite=True):
    n = NBASeasons()
    ft = EWTFantasyTools()
    season = n.season(seasonstr)

    contents = {}
    
    for d in ft.date_list(season['end'], season['start'], '%Y%m%d'):
        content = s.salaries_day(d, 'dk')

        if content:
            contents[d] = content

        time.sleep(4)
        
    return contents
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    from RotoGuruNBAScraper import RotoGuruNBAScraper
    scraper = RotoGuruNBAScraper()

    '''
    seasonstr = '2015-16'
    site = 'fd'
    season = current_season_data(scraper, site)
    fn = '{0}_nba_rg_fd.pkl'.format(seasonstr)

    with open(fn, 'wb') as outfile:
        pickle.dump(season, outfile)

    '''
    seasonstr = '2013-14'
    site = 'fd'
    season = get_season_data(scraper, site, seasonstr)
    fn = '{0}_nba_rg_fd.pkl'.format(seasonstr)

    with open(fn, 'wb') as outfile:
        pickle.dump(season, outfile)
    
