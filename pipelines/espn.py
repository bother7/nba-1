# pipelines.py
# functions to transform fantasylabs data
# for insertion into database, use in optimizer, etc.


from __future__ import print_function
import logging

from nba.seasons import in_what_season


def optimizer_pipeline(self, models):
    '''
    Takes fantasylabs models, make ready to create Player objects for pydfs_lineup_optimizer

    Args:
        models (list): is parsed json from day's models

    Returns:
        players (list): list of players, fixed for use in pydfs_lineup_optimizer

    Examples:
        a = FantasyLabsNBAAgent()
        models = a.today_models()
        players = a.optimizer_pipeline(models)

    '''
    fl_keys = ['PlayerId', 'Player_Name', 'Position', 'Team', 'Salary', 'Score', 'AvgPts', 'Ceiling', 'Floor',
               'ProjPlusMinus']
    fl_players = [{k: v for k, v in p.items() if k in fl_keys} for p in models]

    # remove null values
    for idx, flp in enumerate(fl_players):
        if flp.get('Ceiling') is None:
            fl_players[idx]['Ceiling'] = 0
        if flp.get('Floor') is None:
            fl_players[idx]['Floor'] = 0
        if flp.get('AvgPts') is None:
            fl_players[idx]['AvgPts'] = 0

    return fl_players

def salaries_table(sals, all_players):
    '''

    Args:
        sals:

    Returns:
        List of dict to insert into db
    '''
    fixed_players = []
    for player in sals:
        '''
        Columns:
        nbacom_player_id integer,
        source_player_name character varying(50) NOT NULL,
        team_code character varying,
        game_date date NOT NULL,
        season smallint,
        source character varying(20) NOT NULL,
        source_player_id integer,
        source_position character(2) DEFAULT NULL::bpchar,
        salary smallint NOT NULL,
        dfs_position character varying,
        dfs_site character varying,

        '''


        for idx, salary in enumerate(salaries):
            fx = {'source': 'fantasylabs', 'dfs_site': site, 'game_date': day}
            fx['source_player_id'] = salary.get('PlayerId')
            fx['source_player_name'] = salary.get('Player_Name')
            fx['salary'] = salary.get('Salary')
            fx['team_code'] = salary.get('Team')
            fx['dfs_position'] = salary.get('Position')
            salaries[idx] = fx

        if player.get('PlayerId'):
            try:
                fixed_player['nbacom_player_id'] = all_players.get(int(player.get('PlayerId')))
            except:
                continue
        fixed_player['source'] = 'fl'
        fixed_player['dfs_site'] = 'dk'
        fixed_player['salary'] = player.get('Salary')
        fixed_player['source_position'] = player.get('FirstPosition')
        fixed_player['source_player_name'] = player.get('Player_Name')
        fixed_player['source_player_id'] = player.get('PlayerId')
        fixed_player['game_date'] = player.get('gamedate')
        seas = in_what_season(player.get('gamedate'))
        if seas:
            try:
                s1, s2 = seas.split('-')
                fixed_player['season'] = int(s1) + 1
            except:
                pass
        fixed_players.append(fixed_player)

        site = 'dk'
        wanted = ['Score', 'Player_Name', 'Position', 'Team', 'Ceiling', 'Floor', 'Salary', 'AvgPts', 'p_own', 'PlayerId']

