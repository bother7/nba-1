#!/usr/bin/env python3

# nbadb_player_update.py
# updates nbadb player tables
# can run on daily or periodic basis

import logging
from collections import defaultdict
import sys
import time

from nba.agents.nbacom import NBAComAgent
from nba.dates import today
from nba.parsers.pfr import PfrNBAParser
from nba.pipelines.bref import position_player
from nba.pipelines.nbacom import players_v2015_table
from nba.scrapers.pfr import PfrNBAScraper
from nba.utility import getdb


def update_players():
    '''
    Gets nba players and updates data if position missing
    '''
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    cn = 'nba-agent-{}'.format(today())
    a = NBAComAgent(db=getdb(), cache_name=cn)
    scraper = PfrNBAScraper(cache_name='pfr-nba-scraper')
    parser = PfrNBAParser()
    bref_players = defaultdict(list)
    upq = """
            UPDATE player SET nbacom_position = '{}', primary_position = '{}', position_group = '{}'
            WHERE nbacom_player_id = {}
        """

    # get list of nba players
    content = a.scraper.players_v2015(2017)
    players = players_v2015_table(a.parser.players_v2015(content))

    # use set difference to identify missing ids
    # then list comprehension to filter players
    currids = set([p['nbacom_player_id'] for p in players if p.get('nbacom_player_id')])
    allids = set(a.db.select_list('SELECT nbacom_player_id from player'))
    missing = currids - allids
    for player in [p for p in players if p.get('nbacom_player_id') in missing]:
        if (not player.get('nbacom_position') or not player.get('primary_position') or
            not player.get('position_group')):
            logging.info('updating positional info for {}'.format(player.get('display_first_last')))
            nm = player.get('display_first_last')
            letter = player['last_name'][0].lower()
            if not bref_players.get(letter):
                bref_players[letter] = parser.players(scraper.players(letter))
            # test if there is a match for player in basketball reference
            # if item['display_first_last'] in players:
            # if there is a match, then put the updated information in the player dict
            matches = [p for p in bref_players.get(letter) if
                       p['source_player_name'] == player['display_first_last']]

            if matches:
                logging.info('found b-ref match for {}'.format(player.get('display_first_last')))
                pid = matches[0].get('source_player_id')
                if pid:
                    logging.info('getting b-ref info for {}'.format(player.get('display_first_last')))
                    brplayer = parser.player_page(scraper.player_page(pid), pid)
                    pos = position_player(brplayer.get('source_player_position'))
                    if pos:
                        player['nbacom_position'] = pos[0]
                        player['primary_position'] = pos[1]
                        player['position_group'] = pos[2]
                
                    a.db._insert_dict(player, 'player')
                    logging.info('finished {}'.format(player))
            else:
                logging.info('could not add player\n{}'.format(player))
    logging.info('finished')

if __name__ == '__main__':
    pass