'''
nbacom.py
nba player data
'''

from collections import defaultdict

import logging
import sys

from nba.utility import getdb

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def nbacom_xref(db=None, with_pos=False):
    '''
    Adds nbacom_player_id to list of player dict

    Args:
        db (NBAPostgres): instance
        with_pos (bool): default false, set True to get key with position + name

    Returns:
        dict: key is str, val is list
        
    '''
    if not db:
        db = getdb()
    q = """SELECT * FROM player"""
    nbacom_players = defaultdict(list)
    if with_pos:
        for p in db.select_dict(q):
            key = '{}_{}'.format(p['display_first_last'], p['nbacom_position']).lower()
            nbacom_players[key].append(p)
    else:
        for p in db.select_dict(q):
            key = p['display_first_last'].lower()
            nbacom_players[key].append(p)
    return nbacom_players


if __name__ == '__main__':
    pass