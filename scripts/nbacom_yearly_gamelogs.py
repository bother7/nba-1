'''
nbacom_yearly_gamelogs.py
gets yearly gamelogs from nba.com or file
returns list of player dictionaries
'''

import json
import os
import pprint
import sys

import MySQLdb

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

def main():
    player_logs = []

    for year in ['2000', '2001', '2002', '2003', '2004', '2005']:
    
        base_fn = '/home/sansbacon/'

        try:
            with open('{0}{1}_gamelog.json'.format(base_fn, year), 'r') as infile:
                parsed = json.load(infile)

            results = parsed['resultSets'][0]
            headers = [h.lower() for h in results['headers']]
            exclude = ['matchup', 'team_name', 'video_available', 'game_date']

            for result in results['rowSet']:
                player_log = dict(zip(headers, result))
                player_log['season'] = year
                player_log['dk_points'] = dk_points(player_log)
                player_log['fd_points'] = fd_points(player_log)
                player_logs.append({k:player_log[k] for k in player_log if k not in exclude})

        except:
            pass

    # now insert into database
    db = db_setup()
    cursor = db.cursor()

    placeholders = ', '.join(['%s'] * len(player_logs[0]))
    columns = ', '.join(player_logs[0].keys())
    sql = "INSERT INTO %s ( %s ) VALUES ( %s )" % ('player_gamelogs', columns, placeholders)

    for player_log in player_logs:
        cursor.execute(sql, player_log.values())

    db.commit()

if __name__ == '__main__':
    main()
