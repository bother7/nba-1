# espn.py
# functions to transform espn data
# for insertion into database, etc.

from __future__ import print_function
import logging

from fuzzywuzzy import process




def fix_538player(playerjson):

    # fix keys
    convert = {
     'mp_2015': 'mp_last_season',
     'mp_2016': 'mp_projected',
     'opm_2015': 'opm_last_season',
     'opm_2016': 'opm_projected',
     'per_2015': 'per_last_season',
     'usage': 'usg',
     'value_2015': 'value_last_season',
     'value_2016': 'value_projected',
     'war_mean_2015': 'war_mean_last_season',
     'war_mean_2016': 'war_mean_projected',
    }

    player_stats = playerjson['player_stats']
    player = {convert.get(k, k) : v for k, v in list(player_stats.items())}

    # fix values
    if player['rookie'] == '': player['rookie'] = '0'

    columns = ['age', 'ast_pct', 'ast_pct_ptile_all', 'ast_pct_ptile_pos', 'baseyear', 'blk_pct', 'blk_pct_ptile_all', 'blk_pct_ptile_pos', 'category', 'draft', 'draft_ptile_all', 'draft_ptile_pos', 'ft_freq', 'ft_freq_ptile_all', 'ft_freq_ptile_pos', 'ft_pct', 'ft_pct_ptile_all', 'ft_pct_ptile_pos', 'height', 'height_ptile_all', 'height_ptile_pos', 'mp_last_season', 'mp_projected', 'opm_last_season', 'opm_projected', 'per_last_season', 'player', 'player_id', 'position', 'reb_pct', 'reb_pct_ptile_all', 'reb_pct_ptile_pos', 'rookie', 'stl_pct', 'stl_pct_ptile_all', 'stl_pct_ptile_pos', 'team', 'team_abbr', 'team_short', 'timestamp', 'to_pct', 'to_pct_ptile_all', 'to_pct_ptile_pos', 'tp_freq', 'tp_freq_ptile_all', 'tp_freq_ptile_pos', 'ts_pct', 'ts_pct_ptile_all', 'ts_pct_ptile_pos', 'usg', 'usage_ptile_all', 'usage_ptile_pos', 'value_last_season', 'value_projected', 'war_mean_last_season', 'war_mean_projected', 'weight', 'weight_ptile_all', 'weight_ptile_pos']

    return {col: player[col] for col in columns}


def match_players(db):
    '''
    TODO: need to refactor this
    Args:
        db:

    Returns:

    '''
    fixed = []
    '''
    nbap = {p['display_first_last']: p['nbacom_player_id'] for p in db.select_dict("""SELECT * FROM playersnodup""")}
    for p in db.select_dict("""SELECT * FROM players_espn"""):
        if nbap.get(p.get('player_name', None), None):
            p['nbacom_player_id'] = nbap[p['player_name']]
        else:
            name, perc = process.extractOne(p.get('player_name', None), list(nbap))
            if perc >= 90:
                p['nbacom_player_id'] = nbap[name]

        if 'nbacom_player_id' in p:
            fixed.append(p)
        else:
            print('could not match {}'.format(p))
    '''
    return fixed


def player_xref_table(items):
    ps = []
    for i in items:
        p = {'source': 'espn'}
        p['nbacom_player_id'] = i.get('nbacom_player_id')
        p['source_player_name'] = i.get('player_name')
        p['source_player_id'] = i.get('player_id')
        url = i.get('player_url')
        if url and '/' in url:
            p['source_player_code'] = url.split('/')[-1]
        ps.append(p)
    return ps


if __name__ == '__main__':
    pass