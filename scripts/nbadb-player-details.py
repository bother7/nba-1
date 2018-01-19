#!/usr/bin/env python3
# updates nbadb player table with info from basketball reference
# can run on daily or periodic basis

import logging
from collections import defaultdict
import sys
import time

from nba.dates import today
from nba.parsers.pfr import PfrNBAParser
from nba.pipelines.bref import position_player
from nba.scrapers.pfr import PfrNBAScraper
from nba.utility import getdb


def run():
    '''
    Gets nba players and updates data if position missing
    '''
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    cn = 'nba-agent-{}'.format(today())
    nbadb = getdb()
    scraper = PfrNBAScraper(cache_name='pfr-nba-scraper')
    parser = PfrNBAParser()
    bref_players = defaultdict(list)
    upq = """
            UPDATE player SET nbacom_position = '{}', primary_position = '{}', position_group = '{}'
            WHERE nbacom_player_id = {}
        """

    for item in nbadb.select_dict("""SELECT nbacom_player_id, first_name, last_name, display_first_last, 
                                     nbacom_position, birthdate 
                                     FROM player 
                                     WHERE position_group IS NULL"""):

        try:
            letter = item['last_name'][0]
            if not bref_players.get(letter):
                content = scraper.players(letter)
                bref_players[letter] = parser.players(content)

            # test if there is a match for player in basketball reference
            # if item['display_first_last'] in players:
            # if there is a match, then put the updated information in the database
            # need to get player page from basketball-reference
            # then parse it for nbacom_position, primary_position, and position_group
            matches = [p for p in bref_players.get(letter) if p['source_player_name'] == item['display_first_last']]
            if matches:
                pid = matches[0].get('source_player_id')
                if pid:
                    content = scraper.player_page(pid)
                    player = parser.player_page(content, pid)
                    pos = position_player(player.get('source_player_position'))
                    if pos:
                        nbadb.execute(upq.format(pos[1], pos[2], item['nbacom_player_id']))
                        print('finished {} {}'.format(player, pos))
        except Exception as e:
            logging.exception(e)
        finally:
            time.sleep(.25)

if __name__ == '__main__':
    run()