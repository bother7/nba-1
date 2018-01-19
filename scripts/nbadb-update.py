#!/usr/bin/env python3
# updates nbadb tables
# can run on daily or periodic basis

import logging
import sys

from nba.agents.nbacom import NBAComAgent
from nba.dates import today, yesterday, datetostr
from nba.season import season_start
from nba.scripts import nbadb_player_update
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
    season_year = 2018
    season_code = '2017-18'

    # ensures players table is up-to-date before inserting gamelogs, etc.
    # players uses 2017 as season_year if season_code is 2017-18
    # whereas nbadb calls that season_year 2018
    logging.info('starting update nba.com players')
    nbadb_player_update.update_players()
    logging.info('finished update nba.com players')

    # player_gamelogs
    logging.info('starting nba.com player gamelogs')
    a.player_gamelogs(season_code,
                      date_from=datetostr(season_start(season_code=season_code), fmt='nba'),
                      date_to=yesterday(fmt='nba'))
    logging.info('finished nba.com player gamelogs')

    # playerstats_daily
    logging.info('starting playerstats daily')
    ps = a.playerstats(season_code, all_missing=True)
    logging.info('finished playerstats daily')
    
    # player and team boxscores combined
    logging.info('starting player_boxscores_combined')
    pbs, tbs = a.combined_boxscores()
    logging.info('finished player_boxscores_combined')

    # update team_gamelogs
    logging.info('starting team gamelogs')
    a.team_gamelogs(season_code)
    logging.info('finished team gamelogs')

    # teamstats_daily
    logging.info('starting teamstats daily')
    a.teamstats(season_code, all_missing=True)
    logging.info('finished teamstats daily')

    # team_opponent_dashboards
    logging.info('start team_opponent_dashboards')
    a.team_opponent_dashboards(season_code, all_missing=True)
    logging.info('finished team_opponent_dashboards')

    # game boxscores - linescores, refs, etc.
    logging.info('start game_boxscores')
    a.game_boxscores()
    logging.info('finished game_boxscores')

    # refresh all materialized views
    logging.info('start refresh materialized queries')
    a.refresh_materialized()
    logging.info('refreshed materialized queries')

if __name__ == '__main__':
    run()