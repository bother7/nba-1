#!/usr/bin/env python
# updates nbadb tables
# can run on daily or periodic basis

import os
import sys

from configparser import ConfigParser

from nba.dates import datetostr, date_list
from nba.db.nbacom import NBAComPg
from nba.pipelines.nbacom import *
from nba.pipelines.rotoguru import *
from nba.seasons import season_dates
from pydfs_lineup_optimizer import *
from nba.optimizers.milp import LO


def fl():

    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    config = ConfigParser()
    configfn = os.path.join(os.path.expanduser('~'), '.nbadb')
    config.read(configfn)

    nbapg = NBAComPg(username=config['nbadb']['username'],
                    password=config['nbadb']['password'],
                    database=config['nbadb']['database'])

    #dq = """SELECT DISTINCT game_date FROM cs_games WHERE game_date < now()::date ORDER BY game_date"""
    dq = """SELECT DISTINCT game_date FROM games WHERE game_date = '2015-11-02'"""
    q = """SELECT * FROM past_dfs WHERE game_date = '{}' ORDER BY dk_points DESC"""

    for d in nbapg.select_list(dq):
        gd = datetostr(d, 'nba')
        logging.info('starting {}'.format(gd))
        optimizer = LineupOptimizer(settings.DraftKingsBasketballSettings)
        pls = nbapg.select_dict(q.format(gd))
        logging.info(pls[0:3])
        optimizer._players = nba_to_pydfs(pls)
        items = []
        try:
            for idx, lineup in enumerate(optimizer.optimize(n=10)):
                for p in lineup.players:
                    items.append({
                        'game_date': gd, 'lineup_rank': idx + 1, 'nbacom_player_id': p.id,
                        'positions': p.positions, 'dkpts': p.fppg, 'salary': p.salary
                    })
                print(lineup)
                logging.info('finished lineup {}'.format(idx))

        except Exception as e:
            logging.exception(e)
            continue

        #finally:
        #    nbapg.insert_dicts(items, 'optimal_lineups')


def rg():

    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    config = ConfigParser()
    configfn = os.path.join(os.path.expanduser('~'), '.nbadb')
    config.read(configfn)
    nbapg = NBAComPg(username=config['nbadb']['username'],
                    password=config['nbadb']['password'],
                    database=config['nbadb']['database'])

    with open ('/home/sansbacon/data.csv', 'r') as infile:
        data = [{k: v for k, v in row.items()} for row in csv.DictReader(infile, skipinitialspace=True, delimiter=',')]

    for d in season_dates('2015-16')[2:]:
        items = []
        players = rotoguru_to_pydfs(filter(lambda x: x['date'] == datetostr(d, 'db'), data))
        if players:
            optimizer = LineupOptimizer(settings.DraftKingsBasketballSettings)
            optimizer._players = players
            try:
                for idx, lineup in enumerate(optimizer.optimize(n=100)):
                    for p in lineup.players:
                        items.append({
                            'game_date': d, 'lineup_rank': idx + 1, 'nbacom_player_id': p.id, 'team_code': p.team,
                            'name': '{} {}'.format(p.first_name, p.last_name), 'positions': p.positions, 'dkpts': p.fppg, 'salary': p.salary
                        })

            except Exception as e:
                logging.exception(e)

            finally:
                nbapg.insert_dicts(items, 'optimal_lineups')

        logging.info('finished {}'.format(d))

def t():

    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    with open ('/home/sansbacon/data.csv', 'r') as infile:
        data = [{k: v for k, v in row.items()} for row in csv.DictReader(infile, skipinitialspace=True, delimiter=',')]

    players = rotoguru_to_pydfs(filter(lambda x: x['date'] == '20151102', data))[0:10]
    if players:
        optimizer = LO(settings.DraftKingsBasketballSettings)
        optimizer._players = players
        for lineup in optimizer.optimize():
            print(lineup)

if __name__ == '__main__':
    t()