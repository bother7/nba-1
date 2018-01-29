# queries.py


def missing_game_boxscores(tz='CST'):
    '''
    Query for missing linescores in boxv2015
    
    Args:
        None
        
    Returns:
        str: query
        
    '''
    return """
    
    SELECT nbacom_game_id as gid, to_char(game_date, 'YYYYmmdd') as gd FROM game
        WHERE game_date < (now() AT TIME ZONE '{}')::date 
        AND season_year > 2015 AND nbacom_game_id NOT IN (SELECT DISTINCT nbacom_game_id FROM game_boxscores)
        ORDER BY game_date DESC;""".format(tz)


def missing_player_boxscores(tz='CST'):
    """
    Query to determine games in current season where no data for player_boxscores table

    Returns:
        query string
    """
    return """
         SELECT games.nbacom_game_id
         FROM cs_games games
         WHERE games.game_date < (now() AT TIME ZONE '{}')::date
         AND NOT (games.nbacom_game_id IN (
           SELECT DISTINCT player_boxscores_combined.nbacom_game_id FROM player_boxscores_combined))
        ORDER BY games.nbacom_game_id;
    """.format(tz)


def missing_player_gamelogs(tz='CST'):
    """
    Query to determine games in current season where no data for player_gamelogs table

    Args:
        tz (str): default 'CST'

    Returns:
        str

    """
    return """
         SELECT games.nbacom_game_id
         FROM cs_games games
         WHERE games.game_date < (now() AT TIME ZONE '{}')::date
         AND nbacom_game_id NOT IN (SELECT DISTINCT nbacom_game_id FROM cs_player_gamelogs)
         ORDER BY games.nbacom_game_id;
    """.format(tz)


def missing_playerstats(per_mode):
    """
    Query to determine gamedays in current season where no data for playerstats table

    Args:
        per_mode (str); 'Totals', 'PerGame', etc.

    Returns:
        str
        
    """
    return """
        WITH t AS (
          SELECT day, (day + interval '1 day')::date AS as_of 
          FROM cs_season_todate
          WHERE day < (SELECT MAX(day) FROM cs_season_todate)
        )
        SELECT day FROM t
        WHERE as_of NOT IN(SELECT DISTINCT as_of FROM playerstats_daily WHERE per_mode='{}');
    """.format(per_mode)


def missing_team_gamelogs(tz='CST'):
    """
    Query to determine games in current season where no data for team_gamelogs table

    Returns:
        query string
    """
    return """
        SELECT games.nbacom_game_id
        FROM cs_games games
        WHERE games.game_date < (now() AT TIME ZONE '{}')::date
        AND games.nbacom_game_id NOT IN(SELECT DISTINCT nbacom_game_id FROM team_gamelogs) 
    """.format(tz)


def missing_teamstats(per_mode):
    """
    Query to determine gamedays in current season where no data for teamstats table

    Returns:
        query string
        
    """
    # need to address 1 day gap between game_days and as_of
    return """
        WITH t AS (
          SELECT day, (day + interval '1 day')::date AS as_of 
          FROM cs_season_todate
          WHERE day < (SELECT MAX(day) FROM cs_season_todate)
        )
        SELECT day FROM t
        WHERE as_of NOT IN(SELECT DISTINCT as_of FROM teamstats_daily WHERE per_mode='{}');
    """.format(per_mode)



def missing_team_boxscores(tz='CST'):
    """
    Query to determine games in current season where no data for team_boxscores table

    Args:
        None

    Returns:
        str
        
   """

    return """
        SELECT games.nbacom_game_id
         FROM cs_games games
         WHERE games.game_date < (now() AT TIME ZONE '{}')::date
         AND NOT (games.nbacom_game_id IN (
           SELECT DISTINCT team_boxscores_combined.nbacom_game_id FROM team_boxscores_combined))
        ORDER BY games.nbacom_game_id;
    """.format(tz)


def missing_team_opponent_dashboard(per_mode):
    """
        Query to determine gamedays in current season where no data for team_opponent_dashboard table

        Args:
            per_mode (str); 'Totals', 'PerGame', etc.

        Returns:
            str
            
    """
    return """
        WITH t AS (
          SELECT day, (day + interval '1 day')::date AS as_of 
          FROM cs_season_todate
          WHERE day < (SELECT MAX(day) FROM cs_season_todate)
        )
        SELECT day FROM t
        WHERE as_of NOT IN(SELECT DISTINCT as_of FROM team_opponent_dashboard WHERE per_mode='{}');
    """.format(per_mode)


if __name__ == '__main__':
    pass