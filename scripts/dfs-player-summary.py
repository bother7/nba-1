'''
dfs-player-summary.py
Fetches year-to-date player gamelogs from nba.com
Calculates dfs points
Inserts values into table `current_season_player_gamelogs`
'''

import logging
import os
import pprint

import MySQLdb

from NBAComParser import NBAComParser
from NBAComScraper import NBAComScraper


def db_setup():
    host = os.environ['MYSQL_NBA_HOST']
    user = os.environ['MYSQL_NBA_USER']
    password = os.environ['MYSQL_NBA_PASSWORD']
    database = os.environ['MYSQL_NBA_DATABASE']
    return MySQLdb.connect(host=host, user=user, passwd=password, db=database)

def dk_points(game_log):
    dk_points = 0
    dk_points += game_log['pts']
    dk_points += game_log['fg3m'] * .5
    dk_points += game_log['reb'] * 1.25
    dk_points += game_log['ast'] * 1.5
    dk_points += game_log['stl'] * 2
    dk_points += game_log['blk'] * 2
    dk_points += game_log['tov'] * -.5

    # add the bonus
    over_ten = 0
    for cat in ['pts', 'fg3m', 'reb', 'ast', 'stl', 'blk']:
        if game_log[cat] >= 10:
            over_ten += 1

    # bonus for triple double or double double
    if over_ten >= 3:
        dk_points += 3
    elif over_ten == 2:
        dk_points += 1.5

    return dk_points

def fd_points(player_log):

    fd_points = 0
    fd_points += player_log['pts']
    fd_points += player_log['reb'] * 1.2
    fd_points += player_log['ast'] * 1.5
    fd_points += player_log['stl'] * 2
    fd_points += player_log['blk'] * 2
    fd_points -= player_log['tov']

    return fd_points

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    s = NBAComScraper()
    p = NBAComParser()

    content = s.season_gamelogs('2015-16', 'P')
    player_gamelogs = p.leaguegamelog_players(content)

    for gl in player_gamelogs:
        gl[u'dk_points'] = dk_points(gl)
        gl[u'fd_points'] = fd_points(gl)
        gl.pop('video_available', None)

    pprint.pprint(player_gamelogs[0])

    # insert into database
    tbl = 'current_season_player_gamelogs'
    db = db_setup()
    cursor = db.cursor()

    placeholders = ', '.join(['%s'] * len(player_gamelogs[0]))
    columns = ', '.join(player_gamelogs[0].keys())
    sql = "INSERT INTO %s ( %s ) VALUES ( %s )" % (tbl, columns, placeholders)

    for player_gamelog in player_gamelogs:
        cursor.execute(sql, player_gamelog.values())

    db.commit()
