#!/usr/bin/env python
# updates nbadb tables
# can run on daily or periodic basis

import json
import logging
import os
import sys

import browsercookie
from configparser import ConfigParser

from nba.agents.fantasylabs import FantasyLabsNBAAgent
from nba.agents.nbacom import NBAComAgent
from nba.agents.donbest import DonBestNBAAgent
from nba.agents.rotoguru import RotoGuruNBAAgent
from nba.db.nbacom import NBAComPg
from nba.db.fantasylabs import FantasyLabsNBAPg
from nba.dates import today, yesterday
from nba.parsers.rotogrinders import RotoGrindersNBAParser
from nba.scrapers.rotogrinders import RotoGrindersNBAScraper
from nba.db.rotogrinders import RotoGrindersNBAPg


def main():

    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    config = ConfigParser()
    configfn = os.path.join(os.path.expanduser('~'), '.nbadb')
    config.read(configfn)
    nbapg = NBAComPg(username=config['nbadb']['username'],
                    password=config['nbadb']['password'],
                    database=config['nbadb']['database'])
    flpg = FantasyLabsNBAPg(username=config['nbadb']['username'],
                    password=config['nbadb']['password'],
                    database=config['nbadb']['database'])
    fla = FantasyLabsNBAAgent(db=flpg, cache_name='flabs-nba', cookies=browsercookie.firefox())
    rgurua = RotoGuruNBAAgent(db=nbapg, cache_name='rg-nba')
    cn = 'nba-agent-{}'.format(today())
    a = NBAComAgent(cache_name=cn, cookies=None, db=nbapg)
    a.scraper.delay = 1
    season = '2016-17'

    '''
    # ensures players table is up-to-date before inserting gamelogs, etc.
    players = a.new_players(season[0:4])
    logging.info('finished update nba.com players')
    '''

    # gets all missing (days) salaries from current seasons
    fla.salaries(all_missing=True)
    rgurua.salaries(all_missing=True)
    logging.info('finished dfs salaries')

    '''
    # ensures that player_xref table includes all players from salaries
    fla.update_player_xref()
    logging.info('finished update player_xref')

    # gets model from fantasylabs
    td = today('fl')
    mn = 'phan'
    flpg.insert_models([{
        'game_date': today('fl'),
        'data': fla.scraper.model(model_day=td, model_name=mn),
        'model_name': mn}])

    # gets ownership data from fantasylabs
    fla.ownership(all_missing=True)
    logging.info('finished dfs ownership')

    # gets data from rotogrinders
    rs = RotoGrindersNBAScraper()
    rp = RotoGrindersNBAParser()
    rdb = RotoGrindersNBAPg(username=config['nbadb']['username'],
                    password=config['nbadb']['password'],
                    database=config['nbadb']['database'])
    jsonstr = rp.odds(rs.odds())
    rdb.insert_odds(today(), json.loads(jsonstr))
    logging.info('finished rotogrinders')

    # player_gamelogs
    a.player_gamelogs(season)
    logging.info('finished nba.com player gamelogs')

    # playerstats_daily
    ps = a.playerstats(season, all_missing=True)
    logging.info('finished playerstats daily')

    # player_boxscores_combined
    pbs = a.player_boxscores_combined()
    logging.info('finished player_boxscores_combined')

    # update team_gamelogs
    a.team_gamelogs(season)
    logging.info('finished team gamelogs')

    # teamstats_daily
    a.teamstats(season, all_missing=True)
    logging.info('finished teamstats daily')

    # team_boxscores_combined
    tbs = a.team_boxscores_combined()
    logging.info('finished team_boxscores_combined')

    # team_opponent_dashboards
    a.team_opponent_dashboards(season, all_missing=True)
    logging.info('finished team_opponent_dashboards')

    # v2015 boxscores - linescores, refs, etc.
    a.linescores()
    logging.info('finished linescores')

    # odds and lines
    dba = DonBestNBAAgent(db=nbapg)
    dba.odds(all_missing=True)
    logging.info('finished odds and lines')

    # refresh all materialized views
    nbapg.refresh_materialized()
    logging.info('refreshed materialized queries')
    '''

if __name__ == '__main__':
    main()