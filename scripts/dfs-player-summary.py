'''
dfs-player-summary.py
Fetches year-to-date player gamelogs from nba.com
Calculates dfs points
Inserts values into table `current_season_player_gamelogs`
'''

import logging
import os

import MySQLdb
import MySQLdb.cursors

from NBAComParser import NBAComParser
from NBAComScraper import NBAComScraper


def db_setup():
    host = os.environ['MYSQL_NBA_HOST']
    user = os.environ['MYSQL_NBA_USER']
    password = os.environ['MYSQL_NBA_PASSWORD']
    database = os.environ['MYSQL_NBA_DATABASE']
    db = MySQLdb.connect(host=host, user=user, passwd=password, db=database)

    cursor = db.cursor()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    s = NBAComScraper()
    p = NBAComParser()
    safe = True

    content = s.season_gamelogs('2015-16', 'P')
    player_gamelogs = p.leaguegamelog_players(content)

    for gl in player_gamelogs:
        gl[u'dk_points'] = dk_points(gl)
        gl[u'fd_points'] = fd_points(gl)
        gl.pop('video_available', None)

    # insert into database
    tbl = 'current_season_player_gamelogs'
    cursor = db_setup()

    placeholders = ', '.join(['%s'] * len(player_gamelogs[0]))
    columns = ', '.join(player_gamelogs[0].keys())
    sql = "INSERT INTO %s ( %s ) VALUES ( %s )" % (tbl, columns, placeholders)

    for player_gamelog in player_gamelogs:
        cursor.execute(sql, player_gamelog.values())

    db.commit()
