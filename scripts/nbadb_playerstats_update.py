#!/usr/bin/env python3
# nbadb_playerstats_update.py
# updates nbadb tables
# can run on daily or periodic basis

import logging
import sys

from nba.agents.nbacom import NBAComAgent
from nba.dates import today, datetostr
from nba.utility import getdb


def run2():
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

    # playerstats_daily
    logging.info('starting teamstats daily')

    # Totals
    q = """
        SELECT (as_of - interval '1 day')::date AS day
        FROM audit_teamstats_daily
        WHERE missing_totals > 0
    """

    for day in a.db.select_list(q):
        datestr = datetostr(day, fmt='nba')
        logging.info('starting {} Totals'.format(datestr))
        a.teamstats(season_code, date_from='2017-10-17', date_to=datestr, per_mode='Totals')

    # PerGame
    q = """
        SELECT (as_of - interval '1 day')::date AS day
        FROM audit_teamstats_daily
        WHERE missing_pergame > 0
    """

    for day in a.db.select_list(q):
        datestr = datetostr(day, fmt='nba')
        logging.info('starting {} PerGame'.format(datestr))
        a.teamstats(season_code, date_from='2017-10-17', date_to=datestr, per_mode='PerGame')


    logging.info('finished teamstats daily')


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

    # playerstats_daily
    logging.info('starting teamstats daily')

    q = """
        SELECT (as_of - interval '1 day')::date AS day
        FROM audit_teamstats_daily
        WHERE missing_pergame > 0
    """

    for datestr in ['2017-11-23', '2017-12-24', '2018-01-24', '2018-01-25']:
        logging.info('starting {} PerGame'.format(datestr))
        a.teamstats(season_code, date_from='2017-10-17', date_to=datestr, per_mode='PerGame')

    logging.info('finished teamstats daily')


if __name__ == '__main__':
    run()