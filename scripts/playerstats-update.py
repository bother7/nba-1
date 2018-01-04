#!/usr/bin/env python
# playerstats-update.py
# updates nbadb tables to get correct minutes & seconds played
# can run on daily or periodic basis

import logging
import os
import pickle
import sys

from configparser import ConfigParser

from nba.agents.nbacom import NBAComAgent
from nba.db.nbapg import NBAPostgres
from nba.seasons import *
from nba.utility import merge

def main():

    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    config = ConfigParser()
    configfn = os.path.join(os.path.expanduser('~'), '.pgcred')
    config.read(configfn)
    nbapg = NBAPostgres(username=config['nbadb']['username'],
                    password=config['nbadb']['password'],
                    database=config['nbadb']['database'])
    a = NBAComAgent(cache_name='playerstats-daily', cookies=None, db=nbapg)
    a.scraper.delay = 1

    pstats = {}
    logging.info('starting playerstats_daily')
    for seas_year in range(2017, 2018):
        season = seas_year_to_season(seas_year)
        start = season_start(season)
        for daystr in season_gamedays(seas_year, 'nba'):
            logging.info('starting {}'.format(daystr))
            ps_base = a.parser.playerstats(a.scraper.playerstats(season, DateFrom=start, DateTo=daystr))
            ps_advanced = a.parser.playerstats(a.scraper.playerstats(season, DateFrom=start, DateTo=daystr, MeasureType='Advanced'))
            ps = [merge(dict(), [psadv, psb]) for psb, psadv in zip(ps_base, ps_advanced)]
            for idx, p in enumerate(ps):
                ps[idx]['AS_OF'] = daystr
                ps[idx]['MIN'] = round(ps[idx]['MIN'], 3)
                ps[idx]['SEC_PLAYED'] = round(ps[idx]['SEC_PLAYED'], 3)
            pstats[daystr] = ps
            if a.insert_db:
                with a.db.conn.cursor() as cur:
                    try:
                        cur.executemany(
                            """UPDATE playerstats_daily 
                               SET 
                                 min_played=%(MIN_PLAYED)s, 
                                 min=%(MIN)s, 
                                 sec_played=%(SEC_PLAYED)s 
                               WHERE 
                                 nbacom_player_id = %(PLAYER_ID)s AND 
                                 as_of = %(AS_OF)s;
                            """,
                            ps
                        )
                        a.db.conn.commit()
                        logging.info('completed {}'.format(daystr))
                    except Exception as e:
                        a.db.conn.rollback()
                        logging.exception(e)


    with open('/home/sansbacon/pstats.pkl', 'wb') as outfile:
        pickle.dump(pstats, outfile)


if __name__ == '__main__':
    main()
