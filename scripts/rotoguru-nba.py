#!/usr/env python
'''
#rotoguru-nba.py

'''

import datetime
import logging
import pickle
import pprint
import time

from EWTFantasyTools import EWTFantasyTools
from NBASeasons import NBASeasons
from RotoGuruNBAScraper import RotoGuruNBAScraper

def current_season_data(s, polite=True):
    n = NBASeasons()
    ft = EWTFantasyTools()
    season = n.season('2015-16')

    contents = {}
    
    for d in ft.date_list(datetime.datetime.strftime(datetime.datetime.today(), '%Y%m%d'), season['start'], '%Y%m%d'):
        content = s.data_day(d)

        if content:
            contents[d] = content

        time.sleep(4)
        
    return contents

def get_season_data(s, seasonstr, polite=True):
    n = NBASeasons()
    ft = EWTFantasyTools()
    season = n.season(seasonstr)

    contents = {}
    
    for d in ft.date_list(season['end'], season['start'], '%Y%m%d'):
        content = s.data_day(d)

        if content:
            contents[d] = content

        time.sleep(4)
        
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

    seasonstr = '2015-16'
    season = current_season_data(scraper)
    fn = '{0}_nba_rg_data.pkl'.format(seasonstr)

    with open(fn, 'wb') as outfile:
        pickle.dump(season, outfile)
        
