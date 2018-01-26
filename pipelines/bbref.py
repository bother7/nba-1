"""
# pipelines/bbref.py
# functions to transform basketball-reference data
"""

import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())



def bbref_player_id(fn, ln, offset='01'):
    '''
    Creates bbref player id from player name

    Args:
        fn (str): 
        ln (str): 

    Returns:
        str

    '''
    if len(ln) > 4:
        p1 = ln[0:5]
    else:
        p1 = ln
    if len(fn) > 2:
        p2 = fn[0:2]
    else:
        p2 = fn
    return '{}{}{}'.format(p1, p2, offset).lower()


def bbref_to_nbacom_positions(pos, short_or_long):
    '''
    Converts basketball-reference position to position fields in player table
    (nbacom_position, primary_position, and position_group)

    Args:
        pos (str): Center, Power Forward, etc.
        short_or_long (str): short position form or long form

    Returns:
        tuple: elements are nbacom_position, primary_position, and position_group

    '''
    if short_or_long in ['s', 'short']:
        posxref = {'Center': ('C', 'C', 'Big'),
                   'Center and Power Forward': ('C-F', 'C', 'Big'),
                   'Point Guard': ('G', 'PG', 'Point'),
                   'Point Guard and Shooting Guard': ('G', 'PG', 'Point'),
                   'Power Forward': ('F', 'PF', 'Big'),
                   'Power Forward and Center': ('PF-C', 'PF', 'Big'),
                   'Power Forward and Small Forward': ('F', 'PF', 'Big'),
                   'Shooting Guard': ('G', 'SG', 'Wing'),
                   'Shooting Guard and Small Forward': ('G-F', 'SG', 'Wing'),
                   'Small Forward': ('F', 'SF', 'Wing'),
                   'Small Forward and Shooting Guard': ('F-G', 'SF', 'Wing')}
        return posxref.get(pos)
    elif short_or_long in ['l', 'long']:
        posxref = {'F-C': ('PF-C', 'PF', 'Big'),
                   'G-F': ('G-F', 'SG', 'Wing'),
                   'F-G': ('F-G', 'SF', 'Wing'),
                   'C': ('C', 'C', 'Big')}
        return posxref.get(pos)
    else:
        return None


def guess_bbref_position(bbref_player):
    '''
    Guesses position based on heuristics

    Args:
        bbref_player (dict): 

    Returns:
        str: position such as 'Power Forward'

    '''
    bbref_pos = bbref_player.get('source_player_position')
    if bbref_pos in ['Forward', 'F']:
        try:
            if bbref_player.get('height'):
                f, i = [int(val) for val in bbref_player['height'].split('-')]
                if (f * 12 + i > 79):
                    bbref_pos = 'Power Forward'
                else:
                    bbref_pos = 'Small Forward'
        except:
            logging.error('could not guess bbref position')
    elif bbref_pos in ['Guard', 'G']:
        if bbref_player.get('height'):
            try:
                f, i = [int(val) for val in bbref_player['height'].split('-')]
                if (f * 12 + i > 75):
                    bbref_pos = 'Shooting Guard'
                else:
                    bbref_pos = 'Point Guard'
            except:
                logging.error('could not guess bbref position')
    return bbref_pos


if __name__ == '__main__':
    pass