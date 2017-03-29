import logging
import sys

from nba.scrapers.donbest import DonBestNBAScraper
from nba.parsers.donbest import DonBestNBAParser
from nba.pipelines.donbest import *
from nba.db.pgsql import NBAPostgres
from nba.seasons import season_gamedays

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

s = DonBestNBAScraper(cache_name='dbodds')
p = DonBestNBAParser()
db = NBAPostgres(user='nbadb', password='cft0911', database='nbadb')


for d in season_gamedays(2017, 'db'):
    try:
        odds = p.odds(s.odds(d), d)
        logging.info(odds)
        db.insert_dicts(game_odds(odds), 'odds')
        logging.info('finished {}'.format(d))

    except Exception as e:
        logging.exception(e)
