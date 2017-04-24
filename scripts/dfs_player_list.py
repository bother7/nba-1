#!/usr/bin/env python
# generates list of players from today's games
# TODO: this script is incomplete

import logging
import os
import sys

from configparser import ConfigParser

from nba.agents.nbacom import NBAComAgent
from nba.db.nbacom import NBAComPg
from nba.db.fantasylabs import FantasyLabsNBAPg
from nba.dates import today
from nba.db.queries import today_team_url_codes


def main():

    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    config = ConfigParser()
    configfn = os.path.join(os.path.expanduser('~'), '.pgcred')
    config.read(configfn)
    nbapg = NBAComPg(username=config['nbadb']['username'],
                    password=config['nbadb']['password'],
                    database=config['nbadb']['database'])
    flpg = FantasyLabsNBAPg(username=config['nbadb']['username'],
                    password=config['nbadb']['password'],
                    database=config['nbadb']['database'])

    cn = 'nba-agent-{}'.format(today())
    a = NBAComAgent(cache_name=cn, cookies=None, db=nbapg)
    a.scraper.delay = 1
    season = '2016-17'

    # get the rosters
    q = """SELECT is_starter FROM starters WHERE nbacom_player_id = {}
            ORDER BY game_date DESC LIMIT 1"""
    incomplete = []
    roster_url = 'http://data.nba.com/data/10s/prod/v1/2016/teams/{}/roster.json'
    for urlcode in nbapg.select_list(today_team_url_codes()):
        print(urlcode)
        try:
            roster = a.scraper.get_json(roster_url.format(urlcode))
            for p in roster["league"]["standard"]["players"]:
                pid = p.get('personId')
                starter = a.db.select_scalar(q.format(pid))
                print('{}, {}'.format(pid, starter))
        except:
            incomplete.append(roster_url.format(urlcode))
    for i in incomplete:
        try:
            roster = a.scraper.get_json(roster_url.format(urlcode))
            for p in roster["league"]["standard"]["players"]:
                starter = a.db.select_scalar(q.format(p))
                print('{}, {}'.format(p, starter))
        except:
            logging.error('could not get {}'.format(i))


if __name__ == '__main__':
    main()