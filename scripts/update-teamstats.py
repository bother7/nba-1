#!/usr/bin/env python3
# update-teamstats.py

import logging
import sys

from nba.agents.nbacom import NBAComAgent
from nba.dates import today, yesterday, datetostr
from nba.pipelines.nbacom import teamstats_table
from nba.season import season_start
from nba.scripts import nbadb_player_update
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
    season_year = 2018
    season_code = '2017-18'

    # teamstats_daily
    start = datetostr(d=season_start(season_code=season_code), fmt='nba')
    logging.info('teamstats: getting {}'.format(start))
    ts_base = a.parser.teamstats(a.scraper.teamstats(season_code, DateFrom=start, DateTo=start))
    ts_advanced = a.parser.teamstats(a.scraper.teamstats(season_code, DateFrom=start, DateTo=start, MeasureType='Advanced'))
    ts = [merge_two(tsb, tsadv) for tsb, tsadv in zip(ts_base, ts_advanced)]
    logging.info('found {} teamstats for {}'.format(len(ts), start))
    a.db.insert_dicts(teamstats_table(ts, start), a.table_names['ts'])

    q = """SELECT DISTINCT as_of from teamstats_daily 
           WHERE per_mode='PerGame' AND season_year=2018 ORDER BY as_of"""
    for day in a.db.select_list(q):
        logging.info('teamstats: getting {}'.format(day))
        daystr = datetostr(day, 'nba')
        ts_base = a.parser.teamstats(a.scraper.teamstats(season_code, DateFrom=start, DateTo=daystr))
        ts_advanced = a.parser.teamstats(a.scraper.teamstats(season_code, DateFrom=start, DateTo=daystr, MeasureType='Advanced'))
        ts = [merge_two(tsb, tsadv) for tsb, tsadv in zip(ts_base, ts_advanced)]
        logging.info('found {} teamstats for {}'.format(len(ts), daystr))
        a.db.insert_dicts(teamstats_table(ts, daystr), a.table_names['ts'])

if __name__ == '__main__':
    run()
