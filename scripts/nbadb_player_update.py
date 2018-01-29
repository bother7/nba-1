# nba-player-update.py

import json
import logging
import sys

from nba.agents.bbref import BBRefAgent
from nba.agents.nbacom import NBAComAgent
from nba.dates import datetostr, today
from nba.pipelines.bbref import *
from nba.pipelines.nbacom import players_v2015_table
from nba.season import season_start
from nba.utility import getdb


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
season_code = '2017-18'
a = NBAComAgent(db=getdb(), cache_name='nbacom-agent')
bbrefa = BBRefAgent(db=getdb(), cache_name='bbref-agent')


def add_gamelog_player(gamelog_player):
    '''
    Adds player to player table

    Args:
        gamelog_player (dict):

    Returns:
        None

    '''
    bbref_player = bbrefa.match_gamelog_player(gamelog_player)
    try:
        pos = bbref_to_nbacom_positions(bbref_player.get('source_player_position'), 'long')
        if pos:
            fn, ln = gamelog_player['PLAYER_NAME'].split()
            logging.info('add_gamelog_player: pos is {}'.format(pos))
            toins = {
                'nbacom_player_id': gamelog_player['PLAYER_ID'],
                'first_name': fn, 'last_name': ln,
                'display_first_last': gamelog_player['PLAYER_NAME'],
                'nbacom_position': pos[0],
                'primary_position': pos[1],
                'position_group': pos[2]}
            a.db._insert_dict(toins, 'player')
    except:
        logging.exception('add_gamelog_player: could not add player {}'.format(gamelog_player['PLAYER_NAME']))
        d = {'table_name': 'player',
             'nbacom_player_id': gamelog_player['PLAYER_ID'],
             'error_message': 'could not match player',
             'player_data': json.dumps(gamelog_player)}
        a.db._insert_dict(d, 'player_errors')


def add_nbacom_player(nbacom_player):
    '''
    Adds player to player table

    Args:
        nbacom_player (dict):

    Returns:
        status (int): 0 for success, 1 for failure

    '''
    bbref_player = bbrefa.match_nbacom_player(nbacom_player)
    try:
        pos = bbref_to_nbacom_positions(bbref_player.get('source_player_position'), 'long')
        if pos:
            logging.info('add_gamelog_player: pos is {}'.format(pos))
            toins = {
                'nbacom_player_id': nbacom_player['nbacom_player_id'],
                'first_name': nbacom_player['first_name'], 'last_name': nbacom_player['last_name'],
                'display_first_last': nbacom_player['display_first_last'],
                'nbacom_position': pos[0],
                'primary_position': pos[1],
                'position_group': pos[2]}
            a.db._insert_dict(toins, 'player')
    except:
        logging.exception('add_gamelog_player: could not add player {}'.format(nbacom_player['display_first_last']))
        d = {'table_name': 'player',
             'nbacom_player_id': nbacom_player['nbacom_player_id'],
             'error_message': 'could not match player',
             'player_data': json.dumps(nbacom_player)}
        a.db._insert_dict(d, 'player_errors')


def missing_gamelog_players(season_code):
    '''
    Gets list of players from gamelogs that are not in player table

    Args:
        a (NBAComAgent): object instance 

    Returns:
        list: of players from gamelogs that are not in player table

    '''
    start = datetostr(season_start(season_code=season_code), fmt='nba')
    content = a.scraper.season_gamelogs(
        season_code, 'P',
        date_from=start,
        date_to=today(fmt='nba'))
    gamelogs = a.parser.season_gamelogs(content, 'P')
    wanted = ["PLAYER_ID", "PLAYER_NAME", "TEAM_ID", "TEAM_ABBREVIATION",
              "GAME_ID", "GAME_DATE", "MATCHUP"]
    players = [{k: v for k, v in p.items() if k in wanted} for p in gamelogs]
    currids = set([p['PLAYER_ID'] for p in players])
    allids = set(a.db.select_list('SELECT nbacom_player_id from player'))
    missing = currids - allids
    msg = 'there are {} mising players from gamelogs'.format(len(missing))
    logging.info(msg)
    return [p for p in players if p.get('PLAYER_ID') in missing]


def missing_nbacom_players():
    '''
    Gets list of current players from nba.com that are not in player table

    Args:
        a (NBAComAgent): object instance 

    Returns:
        list: of players that are not in player table

    '''
    content = a.scraper.players_v2015(2017)
    players = players_v2015_table(a.parser.players_v2015(content))
    currids = set([p['nbacom_player_id'] for p in players if
                   p.get('nbacom_player_id')])
    allids = set(a.db.select_list('SELECT nbacom_player_id from player'))
    missing = currids - allids
    logging.debug('there are {} missing nbacom players'.format(len(missing)))
    return [p for p in players if p.get('nbacom_player_id') in missing]


def run():
    # step one: nbacom players
    # get list of missing ids (compare nba json to player table)
    # then add the players, making sure they have
    # position, position_group, and primary_position
    # if you can't find, then insert into error table for manual update
    logging.info('starting nbacom players')
    for player in missing_nbacom_players():
        nm = '{} {}'.format(player.get('firstName'), player.get('lastName'))
        msg = 'missing_nbacom_players: starting {}'.format(nm)
        logging.info(msg)
        logging.debug(player)
        add_nbacom_player(player)

    # step two: gleague players
    logging.info('starting gleague players')
    year = season_code[0:4]
    a.gleague_players(year)

    # step three: gamelog players
    # get list of missing ids (compare nba gamelogs to player table)
    # then add the players, making sure they have
    # position, position_group, and primary_position
    logging.info('starting gamelog players')
    for player in missing_gamelog_players(season_code):
        msg = 'missing_gamelog_players: {}'.format(player.get('PLAYER_NAME'))
        logging.info(msg)
        logging.debug(player)
        add_gamelog_player(player)


if __name__ == '__main__':
    run()