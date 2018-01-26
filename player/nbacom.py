'''
nbacom.py
nba player data
'''

import logging

from nba.names import match_player


def nbacom_dict(db):
    '''
    Gets dict of nbacom player and id
    Args:
        db: NBAPostgres object

    Returns:
        dict: name is key, nbacom_id is value
    '''
    # recent players is a table view - has 2 columns
    q = """SELECT * FROM recent_players"""
    return {item['display_first_last']: item['id'] for item in db.select_dict(q)}


def nbacom_xref(db, players):
    '''
    Adds nbacom_player_id to list of player dict
    Args:
        db: NBAPostgres object
        players: list of dict

    Returns:
        players: list of dict
    '''
    # recent players is a table view - has 2 columns
    nbap = nbacom_dict(db)
    for idx, p in enumerate(players):
        name = match_player(p['source_player_name'], nbap.keys())
        if name:
            players[idx]['nbacom_player_id'] = nbap.get(name)
            logging.info('matched {}'.format(p))
    return players


if __name__ == '__main__':
    pass