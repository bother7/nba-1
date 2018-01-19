# pipelines.py
# functions to transform nbacom list of dict
# for insertion into database, use in optimizer, etc.
from __future__ import print_function
from future.utils import iteritems
import logging

from nba.dates import convert_format, datetostr, strtodate, today
from nba.dfs import dk_points, fd_points
from pydfs_lineup_optimizer import Player

logging.getLogger(__name__).addHandler(logging.NullHandler())


def gamedetail(gds):
    '''

    Args:
        gds:

    Returns:

    '''
    wanted = ['q1', 'q2', 'q3', 'q4', 'ot1', 'ot2', 'ot3', 'ot4', 's', 'ta', 'tid']

    linescores = []
    for gd in gds.values():
        g = gd['g']

        # get visiting team
        v = {k: v for k, v in g.items() if k in ['gid', 'gdte', 'gcode']}
        for k in wanted:
            v[k] = g['vls'][k]
        linescores.append(v)

        # get home team
        h = {k: v for k, v in g.items() if k in ['gid', 'gdte', 'gcode']}
        for k in wanted:
            h[k] = g['hls'][k]
        linescores.append(h)

    return linescores


def nba_to_pydfs(players):
    '''
    Takes results, make ready to create Player objects for pydfs_lineup_optimizer

    Args:
        players (list): day's worth of stats

    Returns:
        players (list): list of players, fixed for use in pydfs_lineup_optimizer
    '''
    return [Player(p['nbacom_player_id'], p['first_name'], p['last_name'],
            p.get('dfs_position').split('/'),
            p.get('team_code'),
            float(p.get('salary', 100000)),
            float(p.get('dk_points',0))) for p in players]


def players_v2015_table(players):
    '''
    Converts data from v2015 API players for insertion into database

    Arguments:
        players: python list of parsed JSON

    Returns:
        list of player dict
    '''
    fixed = []
    for p in players:
        f = {}
        try:
            f['nbacom_player_id'] = int(p['personId'])
            f['first_name'] = p['firstName']
            f['last_name'] = p['lastName']
            f['display_first_last'] = '{} {}'.format(f['first_name'], f['last_name'])
            f['nbacom_position'] = p['pos']
        except:
            logging.exception('could not add {}'.format(p))
            continue
        try:
            f['birthdate'] = strtodate(p['dateOfBirthUTC'])
        except (KeyError, TypeError):
            f['birthdate'] = None

        f['school'] = p.get('collegeName', None)
        f['country'] = p.get('country', None)
        f['last_affiliation'] = p.get('lastAffiliation', None)
        try:
            f['height'] = int(p['heightFeet']) * 6 + int(p['heightInches'])
        except:
            f['height'] = None
        try:
            f['weight'] = int(p['weightPounds'])
        except:
            f['weight'] = None
        try:
            f['jersey'] = int(p['jersey'])
        except:
            f['jersey'] = None
        try:
            f['from_year'] = int(p['nbaDebutYear'])
        except:
            f['from_year'] = None
        try:
            f['draft_number'] = int(p['draft']['pickNum'])
            f['draft_round'] = int(p['draft']['roundNum'])
            f['draft_year'] = int(p['draft']['seasonYear'])
        except:
            f['draft_number'] = None
            f['draft_round'] = None
            f['draft_year'] = None
        fixed.append(f)
    return fixed


def players_table(players):
    '''
    Prepares players for insertion into nbadb players table

    Args:
        players: list of dict

    Returns:
        List of dict formatted for insertion into database
    '''
    fixed = []

    # get rid of extraneous columns, use different names for person_id and position
    omit = ['display_fi_last', 'display_last_comma_first', 'dleague_flag', 'games_played_flag', 'nbacom_team_id',
            'playercode', 'rosterstatus', 'season_exp', 'team_abbreviation', 'team_city', 'team_code', 'team_id', 'team_name']
    convert = {'person_id': 'nbacom_player_id', 'position': 'nbacom_position'}

    # loop through players
    # use lowercase key names, fix values for various columns
    # height (in inches) needs to be calculated from 6-10
    # replace 'Undrafted' or non-integer draft positions with None
    # if player is C, can add primary_position and position_group
    for p in players:
        fp = {}
        for k,v in p.items():
            nk = k.lower()
            if nk in omit:
                continue
            elif nk in convert:
                nk = convert[nk]
            elif nk == 'height':
                try:
                    f,i = v.split('-')
                    v = int(f) * 12 + int(i)
                except:
                    v = None
            elif 'draft' in nk:
                try:
                    v = int(v)
                except:
                    v = None
            elif nk == 'nbacom_position':
                if v == 'C':
                    fp['position_group'] = 'Big'
                    fp['primary_position'] = 'C'
            if v == '':
                v = None
            fp[nk] = v
        fixed.append(fp)
    return fixed


def player_boxscores_table(pbs):
    '''
    Cleans merged list of player boxscores

    Arguments:
        pbs: list of playerboxscore dictionaries

    Returns:
        cleaned_players: list of playerboxscore dictionaries
    '''
    omit = ['FG3_PCT', 'FG_PCT', 'FT_PCT', 'TEAM_CITY', 'TEAM_NAME']
    cls = []
    for player in pbs:
        cl = {k.lower(): v for k, v in player.items() if k not in omit}
        # change to nbacom_player_id
        if 'game_id' in cl:
            cl['nbacom_game_id'] = cl['game_id']
            cl.pop('game_id', None)
        if 'player_id' in cl:
            cl['nbacom_player_id'] = cl['player_id']
            cl.pop('player_id', None)
        if 'team_id' in cl:
            cl['nbacom_team_id'] = cl['team_id']
            cl.pop('team_id', None)
        if 'team_abbreviation' in cl:
            cl['team_code'] = cl['team_abbreviation']
            cl.pop('team_abbreviation', None)
        if 'to' in cl:
            cl['tov'] = cl.get('to')
            cl.pop('to', None)
        cls.append(cl)
    logging.info(cls)
    return cls


def player_gamelogs_table(gl):
    '''
    Prepares players for insertion into nbadb players table

    Args:
        gl: list of dict

    Returns:
        List of dict formatted for insertion into database
    '''
    fixed = []
    omit = ['VIDEO_AVAILABLE', 'TEAM_NAME', 'MATCHUP', 'WL', 'SEASON_ID']

    # skip today - no reliable way of testing if game is over
    for l in gl:
        if l.get('GAME_DATE') == today():
            continue
        cl = {k.lower().strip(): v for k, v in l.items() if k.upper() not in omit}
        cl['dk_points'] = dk_points(cl)
        cl['fd_points'] = fd_points(cl)

        # change to nbacom_player_id
        if 'game_id' in cl:
            cl['nbacom_game_id'] = cl['game_id']
            cl.pop('game_id', None)
        if 'player_id' in cl:
            cl['nbacom_player_id'] = cl['player_id']
            cl.pop('player_id', None)
        if 'team_id' in cl:
            cl['nbacom_team_id'] = cl['team_id']
            cl.pop('team_id', None)
        if 'team_abbreviation' in cl:
            cl['team_code'] = cl['team_abbreviation']
            cl.pop('team_abbreviation', None)
        fixed.append(cl)
    return fixed


def playerstats_table(ps, as_of):
    '''
    Cleans merged list of player base + advanced stats

    Arguments:
        ps: list of player dictionaries

    Returns:
        cleaned_players: list of player dictionaries
    '''
    omit = ['CFID', 'CFPARAMS', 'COMMENT', 'TEAM_NAME']
    cleaned_players = []
    for player in ps:
        clean_player = {k.lower(): v for k, v in iteritems(player) if k not in omit}
        if 'to' in clean_player:
            clean_player['tov'] = clean_player['to']
            clean_player.pop('to', None)
        if 'team_abbreviation' in clean_player:
            clean_player['team_code'] = clean_player['team_abbreviation']
            clean_player.pop('team_abbreviation', None)
        if 'player_id' in clean_player:
            clean_player['nbacom_player_id'] = clean_player['player_id']
            clean_player.pop('player_id', None)
        if 'team_id' in clean_player:
            clean_player['nbacom_team_id'] = clean_player['team_id']
            clean_player.pop('team_id', None)
        clean_player['as_of'] = as_of
        cleaned_players.append(clean_player)
    return cleaned_players


def team_boxscores_table(tbs):
    '''
    Cleans merged list of team boxscores

    Arguments:
        tbs: list of team boxscore dictionaries

    Returns:
        list of team boxscore dictionaries
    '''
    omit = ['COMMENT', 'FG3_PCT', 'FG_PCT', 'FT_PCT', 'TEAM_CITY', 'TEAM_NAME']
    cls = []
    for box in tbs:
        cl = {k.lower(): v for k, v in box.items() if k not in omit}
        if 'min' in cl:
            cl.pop('min', None)
        if 'game_id' in cl:
            cl['nbacom_game_id'] = cl['game_id']
            cl.pop('game_id', None)
        if 'team_id' in cl:
            cl['nbacom_team_id'] = cl['team_id']
            cl.pop('team_id', None)
        if 'team_abbreviation' in cl:
            cl['team_code'] = cl['team_abbreviation']
            cl.pop('team_abbreviation', None)
        if 'to' in cl:
            cl['tov'] = cl.get('to')
            cl.pop('to', None)
        cls.append(cl)
    logging.info(cls)
    return cls


def team_gamelogs_table(tgl):
    '''
    Cleans merged list of team gamelogs base + advanced

    Arguments:
        tgl: list of dictionaries

    Returns:
        cleaned_items(list)
    '''
    omit = ['matchup', 'season_id', 'team_name', 'video_available', 'wl']
    cleaned_items = []

    # skip today - no reliable way of testing if game is over
    for gl in tgl:
        if gl.get('GAME_DATE') == today():
            logging.info('did not add {}'.format(gl))
            continue
        cleaned_item = {k.lower(): v for k,v in gl.items() if k.lower() not in omit}
        if 'game_id' in cleaned_item:
            cleaned_item['nbacom_game_id'] = cleaned_item['game_id']
            cleaned_item.pop('game_id', None)
        if 'team_id' in cleaned_item:
            cleaned_item['nbacom_team_id'] = cleaned_item['team_id']
            cleaned_item.pop('team_id', None)
        if cleaned_item.get('team_abbreviation'):
            cleaned_item['team_code'] = cleaned_item['team_abbreviation']
            cleaned_item.pop('team_abbreviation', None)
        if cleaned_item.get('min'):
            cleaned_item['minutes'] = cleaned_item['min']
            cleaned_item.pop('min', None)
        cleaned_items.append(cleaned_item)
    return cleaned_items


def team_opponent_dashboards_table(dash, as_of):
    '''
    Args:
        dash:
        as_of:

    Returns:

    '''
    topp = []
    omit = ['CFID', 'CFPARAMS', 'COMMENT', 'TEAM_NAME']
    for team in dash:
        cleaned_item = {k.lower(): v for k,v in team.items() if k.upper() not in omit}
        if 'game_id' in cleaned_item:
            cleaned_item['nbacom_game_id'] = cleaned_item['game_id']
            cleaned_item.pop('game_id', None)
        if 'team_id' in cleaned_item:
            cleaned_item['nbacom_team_id'] = cleaned_item['team_id']
            cleaned_item.pop('team_id', None)
        if cleaned_item.get('team_abbreviation'):
            cleaned_item['team_code'] = cleaned_item['team_abbreviation']
            cleaned_item.pop('team_abbreviation', None)
        cleaned_item['as_of'] = convert_format(as_of, 'nba')
        topp.append(cleaned_item)
    return topp


def teamstats_table(ts, as_of):
    '''
    Cleans merged list of team base + advanced stats

    Arguments:
        ts: list of dictionaries
        as_of(str): in YYYY-MM-DD format

    Returns:
        cleaned_items(list): list of cleaned team dictionaries
    '''
    cls = []
    omit = ['CFID', 'CFPARAMS', 'COMMENT', 'TEAM_CITY', 'TEAM_NAME']
    for t in ts:
        cl = {k.lower(): v for k, v in t.items() if k.upper() not in omit}
        cl['as_of'] = as_of
        if 'game_id' in cl:
            cl['nbacom_game_id'] = cl['game_id']
            cl.pop('game_id', None)
        if 'team_id' in cl:
            cl['nbacom_team_id'] = cl['team_id']
            cl.pop('team_id', None)
        if cl.get('team_abbreviation'):
            cl['team_code'] = cl['team_abbreviation']
            cl.pop('team_abbreviation', None)
        cls.append(cl)
    return cls

if __name__ == '__main__':
    pass