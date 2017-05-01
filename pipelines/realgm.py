"""
# pipelines/realgm.py
# functions to transform realgm data
# for insertion into database
"""

from __future__ import print_function
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())


def depth_charts_table(dc):
    '''
    Prepares depth charts for insertion into database
    Args:
        dc:

    Returns:
        dc
    '''
    # {u'20161229': [{'c': u'Paul Millsap', 'pf': u'T. Sefolosha', 'pg': u'D. Schroder',
    # 'team': 'ATL', 'role': u'Starters', 'sg': u'Kent Bazemore', 'sf': u'Kyle Korver'},
    # season, as_of, nbacom_player_id, team_code, source, source_player_id,
    # source_player_name, source_position, source_role
    pass

if __name__ == '__main__':
    pass