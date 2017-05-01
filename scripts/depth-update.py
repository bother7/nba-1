#!/usr/bin/env python
# depth-update.py
# updates depth_chart table to get accurate depth charts for NBA players
# can run on daily or periodic basis


import logging
import os
import pickle
import sys

from configparser import ConfigParser

from nba.dates import date_list, datetostr
from nba.db.nbacom import NBAComPg
from nba.parsers.realgm import RealgmNBAParser
from nba.parsers.rotoworld import RotoworldNBAParser
from nba.scrapers.wayback import WaybackScraper
from nba.seasons import season_start, season_end


def realgm(scraper, season, db):
    results = []
    p = RealgmNBAParser()

    url = 'http://basketball.realgm.com/nba/depth-charts'

    for d in date_list(d2=season_start(season), d1=season_end(season), delta=7):
        dstr = datetostr(d, 'db')
        try:
            content, content_date = scraper.get_wayback(url, d=dstr, max_delta=6)
            if content and content_date:
                for r in p.depth_charts(content, dstr):
                    r.pop('pf', None)
                    db._insert_dict(r, 'depth_charts')
                    results.append(r)
                logging.info('completed {}'.format(dstr))
            else:
                logging.error('could not get {}'.format(dstr))
        except Exception as e:
            logging.exception('could not get {}: {}'.format(dstr, e))


def rotoworld(scraper, season, db):
    results = []
    p = RotoworldNBAParser()

    url = 'http://www.rotoworld.com/teams/depth-charts/nba.aspx'

    for d in date_list(d2=season_start(season), d1=season_end(season), delta=7):
        dstr = datetostr(d, 'db')
        try:
            content, content_date = scraper.get_wayback(url, d=dstr, max_delta=10)
            if content and content_date:
                for r in p.depth_charts(content, dstr):
                    r.pop('pf', None)
                    db._insert_dict(r, 'depth_charts')
                    results.append(r)
                logging.info('completed {}'.format(dstr))
            else:
                logging.error('could not get {}'.format(dstr))
        except Exception as e:
            logging.exception('could not get {}: {}'.format(dstr, e))

def main():

    config = ConfigParser()
    configfn = os.path.join(os.path.expanduser('~'), '.pgcred')
    config.read(configfn)
    db = NBAComPg(username=config['nbadb']['username'],
                    password=config['nbadb']['password'],
                    database=config['nbadb']['database'])

    s = WaybackScraper(cache_name='realgm-wayback')
    rotoworld(s, '2014-15', db)
    rotoworld(s, '2016-17', db)

    #results = realgm(s, '2016-17', db)
    #results += rotoworld(s, '2016-17', db)
    #with open('/home/sansbacon/rotoworld-depth-2017.pkl', 'wb') as outfile:
    #    pickle.dump(results, outfile)


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    main()
