#!/usr/env python
# nbacom_fetch_yearly_playerstats.py
# this script downloads year-by-year stats of players
# can download basic or advanced
# does not use my existing classes to scrape / parse
# TODO: keep logic, but use the scraper class to handle save & download

import httplib2
import logging
import os.path
from time import sleep

def get_from_web(url):   
    return h.request(url, "GET")

def save_content(content, fn):
    try:
        with open(fn, 'w') as outfile:
            outfile.write(content)
            logging.debug('saved player ' + str(id) + ' to ' + fn)  
    except:
        logging.exception('could not save file ' + fn)

if __name__ == '__main__':
    # setup
    logging.basicConfig(level=logging.DEBUG,
                    format='%(message)s',
                    handlers=[logging.StreamHandler()])
    savedir = 'nbaplayerstats_json_files'
    h = httplib2.Http(".cache")

    base_url = 'http://stats.nba.com/stats/leaguedashplayerstats?'

    unchanged_params = 'DateFrom=&DateTo=&GameScope=&GameSegment=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PaceAdjust=N&PerMode=Totals&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&SeasonSegment=&SeasonType=Regular+Season&StarterBench=&VsConference=&VsDivision=&Rank=N'

    for year in range(1995, 2015):
        year_param = str(year) + '-' + str(year+1)[-2:]

        # get regular stats
        bs_fn = os.path.join(os.path.dirname(os.path.realpath(__file__)), savedir, year_param + '_basic.json')
        if not os.path.isfile(bs_fn):
            url_base_stats = base_url + unchanged_params + '&MeasureType=Base&Season=' + year_param
            logging.debug(url_base_stats)
            bs_resp, bs_content = get_from_web(url_base_stats)
            logging.debug(bs_content) 
            save_content(bs_content, bs_fn)
      
        # get advanced stats
        adv_fn = os.path.join(os.path.dirname(os.path.realpath(__file__)), savedir, year_param + '_advanced.json')
        if not os.path.isfile(adv_fn):
            url_adv_stats = base_url + unchanged_params + '&MeasureType=Advanced&Season=' + year_param
            logging.debug(url_adv_stats)
            adv_resp, adv_content = get_from_web(url_adv_stats)
            logging.debug(adv_content)
            save_content(adv_content, adv_fn)
