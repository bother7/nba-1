'''
nbacom_update_players.py
gets players that are in the gamelogs that are not in the players table

'''

import logging
from time import sleep

from NBAComParser import NBAComParser
from NBAComScraper import NBAComScraper
from NBAMySQL import NBAMySQL


def main():
    # 1626166
    # setup
    logging.basicConfig(level=logging.DEBUG,
                        format='%(message)s',
                        handlers=[logging.StreamHandler()])
    p = NBAComParser()
    s = NBAComScraper()
    n = NBAMySQL()

    ## note - need to find existing script that does all of this
    for player in n.players_to_add():
        player_info = {k.lower(): v for k,v in p.player_info(s.player_info(player_id=player['player_id'], season='2015-16')).iteritems()}

        # fix keynames
        player_info.pop('games_played_flag', None)
        player_info['nbacom_team_id'] = player_info.get('team_id', None)
        player_info.pop('team_id', None)
        player_info['primary_position'] = player_info.get('position', None)
        player_info.pop('position', None)

        try:
            n._insert_dict(player_info, 'players')

        except Exception as e:
            logging.exception('could not insert row: {0}'.format(e.message))

        sleep(.5)

if __name__ == '__main__':
    main()
