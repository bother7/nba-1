'''
realgmxref.py
cross-reference realgm players with nba.players table ids
'''

import logging

from nba.names import match_player


def nbacom_ids(db, players):
    '''
    Gets nbacom_player_id for list of player dict
    Args:
        db: NBAPostgres object
        players: list of dict

    Returns:
        players: list of dict
    '''
    # recent players is a table view - has 2 columns
    q = """SELECT * FROM recent_players"""
    nba = {item['display_first_last']: item['id'] for item in db.select_dict(q)}
    for idx, p in enumerate(players):
        name = match_player(p['source_player_name'], nba.keys())
        if name:
            players[idx]['nbacom_player_id'] = nba.get(name)
            logging.debug('matched {}'.format(p))
    return players


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