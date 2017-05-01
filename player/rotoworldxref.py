'''
rotoworldxref.py
cross-reference rotoworld players with nba.players table ids
'''

import logging

from nba.db.queries import rotoworld_players
from nba.player.nbacom import nbacom_xref


def rotoworld_player_ids(db):
    '''
    Returns list of dict of rotoworld players
    Args:
        db: 

    Returns:
        list of dict: rotoworld players
    '''
    rwp = {p['source_player_id']: p['source_player_name'] for p in db.select_dict(rotoworld_players())}
    return [{'source': 'rotoworld', 'source_player_name': v, 'source_player_id': k} for k,v in rwp.items()]


def update_rotoworld_xref(db, players=None):
    '''
    
    Args:
        db: NBAPostgres instance 
        players: list of players to add to player_xref table

    Returns:
        None
    '''
    if not players:
        players = rotoworld_player_ids(db)
    return nbacom_xref(db, players)


if __name__ == '__main__':
    pass