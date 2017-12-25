#!/usr/bin/env python
# updates nbadb tables
# can run on daily or periodic basis

import logging
import sys

from nba.agents.nbacom import NBAComAgent
from nba.dates import today, yesterday
from nba.pipelines.nbacom import players_v2015_table
from nba.utility import getdb


def extras():
    '''
    config = ConfigParser()
    configfn = os.path.join(os.path.expanduser('~'), '.pgcred')
    config.read(configfn)
    nbapg = NBAComPg(username=config['nbadb']['username'],
                    password=config['nbadb']['password'],
                    database=config['nbadb']['database'])
    flpg = FantasyLabsNBAPg(username=config['nbadb']['username'],
                    password=config['nbadb']['password'],
                    database=config['nbadb']['database'])
    fla = FantasyLabsNBAAgent(db=flpg, cache_name='flabs-nba', cookies=browsercookie.firefox())
    rgurua = RotoGuruNBAAgent(db=nbapg, cache_name='rg-nba')

    from nba.parsers.rotogrinders import RotoGrindersNBAParser
    from nba.scrapers.rotogrinders import RotoGrindersNBAScraper
    from nba.db.rotogrinders import RotoGrindersNBAPg

    from nba.agents.fantasylabs import FantasyLabsNBAAgent
    from nba.agents.donbest import DonBestNBAAgent
    from nba.agents.rotoguru import RotoGuruNBAAgent
    from nba.db.nbacom import NBAComPg
    from nba.db.fantasylabs import FantasyLabsNBAPg

    '''
    pass

def run():
    '''
    Updates nba.com statistics

    Args:
        None
        
    Returns:
        None
    '''
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    db = getdb('nbacom')
    cn = 'nba-agent-{}'.format(today())
    a = NBAComAgent(cache_name=cn, db=db)
    a.scraper.delay = 1
    season = '2017-18'

    # ensures players table is up-to-date before inserting gamelogs, etc.
    logging.info('starting update nba.com players')
    content = a.scraper.players_v2015(season)
    players = players_v2015_table(a.parser.players_v2015(content))
    currids = set([int(p.get('nbacom_player_id', 0)) for p in players])
    allids = set(a.db.select_list('SELECT nbacom_player_id from players'))
    missing = currids - allids
    if missing:
        np = [p for p in players if int(p['nbacom_player_id']) in missing]
        for p in players_v2015_table(np):
            a.db._insert_dict(p, 'players')

    logging.info('finished update nba.com players')


    # gets all missing (days) salaries from current seasons
    #logging.info('starting dfs salaries')
    #fla.salaries(all_missing=True)
    #rgurua.salaries(all_missing=True)
    #logging.info('finished dfs salaries')

    # ensures that player_xref table includes all players from salaries
    #logging.info('starting update player_xref')
    #fla.update_player_xref()
    #logging.info('finished update player_xref')

    # gets model from fantasylabs
    #td = today('fl')
    #mn = 'phan'
    #flpg.insert_models([{
    #    'game_date': today('fl'),
    #    'data': fla.scraper.model(model_day=td, model_name=mn),
    #    'model_name': mn}])

    # gets ownership data from fantasylabs
    #logging.info('starting dfs ownership')
    #fla.ownership(all_missing=True)
    #logging.info('finished dfs ownership')

    # gets data from rotogrinders
    #logging.info('starting rotogrinders')
    #rs = RotoGrindersNBAScraper()
    #rp = RotoGrindersNBAParser()
    #rdb = RotoGrindersNBAPg(username=config['nbadb']['username'],
    #                password=config['nbadb']['password'],
    #                database=config['nbadb']['database'])
    #jsonstr = rp.odds(rs.odds())
    #rdb.insert_odds(today(), json.loads(jsonstr))
    #logging.info('finished rotogrinders')

    '''
    # player_gamelogs
    logging.info('starting nba.com player gamelogs')
    a.player_gamelogs(season)
    logging.info('finished nba.com player gamelogs')

    # playerstats_daily
    logging.info('starting playerstats daily')
    ps = a.playerstats(season, all_missing=True)
    logging.info('finished playerstats daily')

    # player_boxscores_combined
    logging.info('starting player_boxscores_combined')
    pbs = a.player_boxscores_combined()
    logging.info('finished player_boxscores_combined')

    # update team_gamelogs
    logging.info('starting team gamelogs')
    a.team_gamelogs(season)
    logging.info('finished team gamelogs')

    # teamstats_daily
    logging.info('starting teamstats daily')
    a.teamstats(season, all_missing=True)
    logging.info('finished teamstats daily')

    # team_boxscores_combined
    logging.info('start team_boxscores_combined')
    tbs = a.team_boxscores_combined()
    logging.info('finished team_boxscores_combined')

    # team_opponent_dashboards
    logging.info('start team_opponent_dashboards')
    a.team_opponent_dashboards(season, all_missing=True)
    logging.info('finished team_opponent_dashboards')

    # v2015 boxscores - linescores, refs, etc.
    logging.info('start linescores')
    a.linescores()
    logging.info('finished linescores')


    # odds and lines
    logging.info('start odds and lines')
    dba = DonBestNBAAgent(db=nbapg)
    odds = dba.odds(all_missing=True)
    logging.debug(odds)
    logging.info('finished odds and lines')

    # refresh all materialized views
    logging.info('start refresh materialized queries')
    nbapg.refresh_materialized()
    logging.info('refreshed materialized queries')
    '''

if __name__ == '__main__':
    run()
