'''
realgmxref.py
cross-reference realgm players with nba.players table ids
'''

import logging

from nba.player.nbacom import nbacom_xref


def update_realgm_xref(db, players):
    '''
    
    Args:
        db: NBAPostgres instance 
        players: list of players to add to player_xref table

    Returns:
        None
    '''
    pass


if __name__ == '__main__':
    pass