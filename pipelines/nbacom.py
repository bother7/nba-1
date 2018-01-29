# pipelines.py
# functions to transform nbacom list of dict
# for insertion into database, use in optimizer, etc.
from future.utils import iteritems
import logging

from nba.dates import add_days_to_datestr, convert_format, strtodate, today
from nba.dfs import dk_points, fd_points

logging.getLogger(__name__).addHandler(logging.NullHandler())


def games_table(games):
    '''
    
    Args:
        games: 

    Returns:

    TODO:
        implement this function
    '''
    pass
    '''
    for item in data['lscd']:
        mscd = item['mscd']
        for game in mscd['g']:
            g = {'season': 2018}
            g['game_id'] = game['gid']
            g['gamecode'] = game['gcode']
            g['game_date'] = game['gdte']
            if 'AS1' in game['gcode'] or 'WLDUSA' in game['gcode']:
                continue   
            elif (subtract_datestr(g['game_date'], '2017-10-17') >= 0):
                g['game_type'] = 'regular'
            else:
                continue
            v = game['v']
            g['visitor_team_id'] = v['tid']
            g['visitor_team_code'] = v['ta']
            h = game['h']
            g['home_team_id'] = h['tid']
            g['home_team_code'] = h['ta']
            nbadb._insert_dict(g, 'games')
            games.append(g)
    '''


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


def gleague_player_table(players):
    '''
    Formats gleague players to insert in player table

    Args:
        players (list): of dict

    Returns:
        list: of dict

    '''
    results = []

    xref = {'sn': 'school', 'ln': 'last_name', 'wt': 'weight',
            'dy': 'draft_year', 'fn': 'first_name', 'pid': 'nbacom_player_id',
            'num': 'jersey', 'dob': 'birthdate', 'ht': 'height',
            'pos': 'nbacom_position', 'la': 'last_affiliation'}

    for player in players:

        # convert field names to columns in player table
        p = {xref.get(k): v for k, v in player.items() if v and xref.get(k)}
        p['display_first_last'] = '{} {}'.format(p['first_name'], p['last_name'])
        # need to convert height to int
        height = None
        try:
            f, i = [int(val) for val in player['height'].split('-')]
            p['height'] = f * 12 + i
        except:
            p['height'] = None

        # need to get primary_position and position_group
        if p.get('nbacom_position') == 'G':
            if player.get('height', 0) > 75:
                p['primary_position'] = 'SG'
                p['position_group'] = 'Wing'
                results.append(p)
            else:
                p['primary_position'] = 'PG'
                p['position_group'] = 'Point'
                results.append(p)
        elif p.get('nbacom_position') == 'F':
            if player.get('height', 0) > 79:
                p['primary_position'] = 'PF'
                p['position_group'] = 'Big'
                results.append(p)
            else:
                p['primary_position'] = 'SF'
                p['position_group'] = 'Wing'
                results.append(p)
        elif p.get('nbacom_position') == 'C':
            p['primary_position'] = 'C'
            p['position_group'] = 'Big'
            results.append(p)
        elif p.get('height'):
            if player.get('height', 0) > 83:
                p['primary_position'] = 'C'
                p['position_group'] = 'Big'
                results.append(p)
            elif player.get('height', 0) > 80:
                p['primary_position'] = 'PF'
                p['position_group'] = 'Big'
                results.append(p)
            elif player.get('height', 0) > 77:
                p['primary_position'] = 'SF'
                p['position_group'] = 'Wing'
                results.append(p)
            elif player.get('height', 0) > 74:
                p['primary_position'] = 'SG'
                p['position_group'] = 'Wing'
                results.append(p)
            else:
                p['primary_position'] = 'PG'
                p['position_group'] = 'Point'
                results.append(p)
        else:
            logging.error('could not guess position {}'.format(player))
    return results


def nba_to_pydfs(players):
    '''
    Takes results, make ready to create Player objects for pydfs_lineup_optimizer

    Args:
        players (list): day's worth of stats

    Returns:
        players (list): list of players, fixed for use in pydfs_lineup_optimizer
    '''
    try:
        from pydfs_lineup_optimizer import Player
        return [Player(p['nbacom_player_id'], p['first_name'], p['last_name'],
                p.get('dfs_position').split('/'),
                p.get('team_code'),
                float(p.get('salary', 100000)),
                float(p.get('dk_points',0))) for p in players]

    except ImportError:
        logging.exception('could not import pydfs_lineup_optimizer')


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
            f['height'] = int(p['heightFeet']) * 12 + int(p['heightInches'])
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


def playerstats_table(ps, datestr, per_mode):
    '''
    Cleans merged list of player base + advanced stats

    Arguments:
        ps (list): of dict
        datestr (str): in YYYY-MM-DD format
        per_mode (str): 'Totals', 'PerGame', etc.

    Returns:
        list: of dict
        
    '''
    omit = ['CFID', 'CFPARAMS', 'COMMENT', 'TEAM_NAME']
    cleaned_players = []
    for player in ps:
        clean_player = {k.lower(): v for k, v in iteritems(player) if k not in omit}
        clean_player['per_mode'] = per_mode
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
        clean_player['as_of'] = add_days_to_datestr(datestr, 1)
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
    for gl in [l for l in tgl if l['GAME_DATE'] != today()]:
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


def team_opponent_dashboards_table(dash, as_of, per_mode='Totals'):
    '''
    Args:
        dash (list): of dict
        as_of (str): in YYYY-MM-DD format
        per_mode (str): 'Totals', 'PerGame', etc.

    Returns:

    '''
    topp = []
    omit = ['CFID', 'CFPARAMS', 'COMMENT', 'TEAM_NAME']
    for team in dash:
        cleaned_item = {k.lower(): v for k,v in team.items() if k.upper() not in omit}
        cleaned_item['per_mode'] = per_mode
        if 'game_id' in cleaned_item:
            cleaned_item['nbacom_game_id'] = cleaned_item['game_id']
            cleaned_item.pop('game_id', None)
        if 'team_id' in cleaned_item:
            cleaned_item['nbacom_team_id'] = cleaned_item['team_id']
            cleaned_item.pop('team_id', None)
        if cleaned_item.get('team_abbreviation'):
            cleaned_item['team_code'] = cleaned_item['team_abbreviation']
            cleaned_item.pop('team_abbreviation', None)
        cleaned_item['as_of'] = add_days_to_datestr(as_of, 1)
        topp.append(cleaned_item)
    return topp


def teamstats_table(ts, as_of, per_mode):
    '''
    Cleans merged list of team base + advanced stats

    Arguments:
        ts (list): of dict
        as_of (str): in YYYY-MM-DD format
        per_mode (str): 'Totals', 'PerGame', etc.

    Returns:
        list: of dict
        
    '''
    cls = []
    omit = ['CFID', 'CFPARAMS', 'COMMENT', 'TEAM_CITY', 'TEAM_NAME']
    for t in ts:
        cl = {k.lower(): v for k, v in t.items() if k.upper() not in omit}
        cl['per_mode'] = per_mode
        cl['as_of'] = add_days_to_datestr(as_of, 1)
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