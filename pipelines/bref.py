"""
# pipelines/bref.py
# functions to transform basketball-reference data
"""

import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())


def position_player(pos):
    '''
    Converts basketball-reference position to position fields in player table
    (nbacom_position, primary_position, and position_group)

    Args:
        pos (str): Center, Power Forward, etc.

    Returns:
        tuple: default None, elements are nbacom_position, primary_position, and position_group

    '''
    # TODO: need to test this more but have most common positional designations
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


if __name__ == '__main__':
    pass