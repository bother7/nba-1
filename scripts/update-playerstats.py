#!/usr/bin/env python3
# update-teamstats.py

import logging
import sys

from nba.agents.nbacom import NBAComAgent
from nba.dates import today, datetostr
from nba.pipelines.nbacom import playerstats_table
from nba.season import season_start
from nba.utility import getdb, merge_two


def run():
    '''
    Updates nba.com statistics

    Args:
        None
        
    Returns:
        None
        
    '''
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    db = getdb()
    cn = 'nba-agent-{}'.format(today())
    a = NBAComAgent(cache_name=cn, db=db)
    a.scraper.delay = 1
    season_code = '2017-18'

    start = datetostr(d=season_start(season_code=season_code), fmt='nba')
    logging.info('teamstats: getting {}'.format(start))
    per_mode = 'PerGame'
    ps = a.playerstats(season_code, per_mode=per_mode, date_from=start, date_to=start)
    logging.info('found {} pstats for {}'.format(len(ps), start))

    q = """SELECT DISTINCT as_of from playerstats_daily
           WHERE per_mode='Totals' AND season_year=2018 ORDER BY as_of"""
    for day in a.db.select_list(q):
        logging.info('teamstats: getting {}'.format(day))
        daystr = datetostr(day, 'nba')
        ps = a.playerstats(season_code, per_mode=per_mode, date_from=start, date_to=daystr)
        logging.info('found {} pstats for {}'.format(len(ps), daystr))


if __name__ == '__main__':
    run()
