#!/usr/bin/env python3
# update-teamdash.py

import logging
import sys

from nba.agents.nbacom import NBAComAgent
from nba.dates import today, datetostr
from nba.pipelines.nbacom import team_opponent_dashboards_table
from nba.season import season_start
from nba.utility import getdb


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
    content = a.scraper.team_opponent_dashboard(season_code, DateFrom=start, DateTo=start)
    topp = a.parser.team_opponent_dashboard(content)
    logging.info('found {} teamdash for {}'.format(len(topp), start))
    a.db.insert_dicts(team_opponent_dashboards_table(topp, start), a.table_names['tod'])

    q = """SELECT DISTINCT as_of from team_opponent_dashboard 
           WHERE per_mode='PerGame' AND season_year=2018 ORDER BY as_of"""
    for day in a.db.select_list(q):
        daystr = datetostr(day, 'nba')
        logging.info('starting dashboards for {}'.format(daystr))
        content = a.scraper.team_opponent_dashboard(season_code, DateFrom=start, DateTo=daystr)
        topp = a.parser.team_opponent_dashboard(content)
        logging.info('found {} teamdash for {}'.format(len(topp), daystr))
        a.db.insert_dicts(team_opponent_dashboards_table(topp, daystr), a.table_names.get('tod'))


if __name__ == '__main__':
    run()
