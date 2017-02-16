#!/usr/bin/env python
# updates nbadb tables
# can run on daily or periodic basis

import datetime
import logging
import os
import sys

from configparser import ConfigParser

from nba.agents.nbacom import NBAComAgent
from nba.db.nbacom import NBAComPg
from nba.db.fantasylabs import FantasyLabsNBAPg

def main():
    logger = logging.getLogger('nbadb-update')
    hdlr = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    
    config = ConfigParser()
    configfn = os.path.join(os.path.expanduser('~'), '.nbadb')
    config.read(configfn)
    nbapg = NBAComPg(username=config['nbadb']['username'],
                    password=config['nbadb']['password'],
                    database=config['nbadb']['database'])
    flpg = FantasyLabsNBAPg(username=config['nbadb']['username'],
                    password=config['nbadb']['password'],
                    database=config['nbadb']['database'])

    today = datetime.datetime.strftime(datetime.datetime.today(), '%-m_%-d_%Y')
    cn = 'nba-agent-{}'.format(today)
    a = NBAComAgent(cache_name=cn, cookies=None, db=nbapg)
    season = '2016-17'

    # step one: update players
    a.new_players(season)
    logger.info('finished step one')

    # step two: player_gamelogs
    a.player_gamelogs(season)
    logger.info('finished step two')

    # step three: playerstats_daily
    ps = a.playerstats(season)
    logger.info('finished step four')

    # step four: update team_gamelogs
    a.team_gamelogs(season)
    logger.info('finished step four')

    # step five: teamstats_daily
    a.teamstats(season)
    logger.info('finished step four')

    # step six: team_opponent_dashboards
    #a.teamstats(season)
    #logger.info('finished step four')

    # step seven: update salaries
    from nba.agents.fantasylabs import FantasyLabsNBAAgent
    fla = FantasyLabsNBAAgent(db=flpg, cache_name='flabs-nba')
    fla.salaries(all_missing=True)
    logger.info('finished step two')

    # step eight: ownership
    #fla.ownership(all_missing=True)
    #logger.info('finished step eight')

if __name__ == '__main__':
    main()