# queries.py
# ugly sql in simple functions


def current_team_dashboard():
    """
        Query to determine most recent team dashboards

        Returns:
            query string
    """
    return """
        WITH td AS (
        select * from team_opponent_dashboard where as_of = (select max(as_of) from team_opponent_dashboard t2)
        ),

        t AS (
        select nbacom_team_id as team_id, team_code from cteams
        )

        select
          as_of, t.team_code, gp, opp_fta, opp_fta_rank, opp_fg3a, opp_fg3a_rank,
          opp_reb, opp_reb_rank, opp_ast, opp_ast_rank, opp_stl, opp_stl_rank,
          opp_blk, opp_blk_rank, opp_pts, opp_pts_rank

        from td
        left join t ON td.team_id = t.team_id
        order by opp_pts DESC
    """

def dkpoints():
    """
    Query to determine percentage of points scored by category

    Returns:
        query string
    """
    return """
        WITH t1 AS (
             SELECT cs_player_gamelogs.nbacom_player_id,
                cs_player_gamelogs.player_name,
                count(cs_player_gamelogs.player_name) AS gp,
                sum(cs_player_gamelogs.min) AS mintot,
                round((sum(cs_player_gamelogs.min) / count(cs_player_gamelogs.player_name))::numeric, 1) AS mpg,
                round(sum(cs_player_gamelogs.dk_points) / count(cs_player_gamelogs.player_name)::numeric, 2) AS dkpg,
                    CASE
                        WHEN sum(cs_player_gamelogs.min)::numeric > 0::numeric THEN round(sum(cs_player_gamelogs.dk_points) / sum(cs_player_gamelogs.min)::numeric, 2)
                        ELSE NULL::numeric
                    END AS dkmin,
                    CASE
                        WHEN sum(cs_player_gamelogs.dk_points) > 0::numeric THEN round(sum(cs_player_gamelogs.pts)::numeric / sum(cs_player_gamelogs.dk_points), 3)
                        ELSE NULL::numeric
                    END AS ptspct,
                    CASE
                        WHEN sum(cs_player_gamelogs.dk_points) > 0::numeric THEN round(sum(cs_player_gamelogs.reb)::numeric * 1.25 / sum(cs_player_gamelogs.dk_points), 3)
                        ELSE NULL::numeric
                    END AS rebpct,
                    CASE
                        WHEN sum(cs_player_gamelogs.dk_points) > 0::numeric THEN round(sum(cs_player_gamelogs.ast)::numeric * 1.5 / sum(cs_player_gamelogs.dk_points), 3)
                        ELSE NULL::numeric
                    END AS astpct,
                    CASE
                        WHEN sum(cs_player_gamelogs.dk_points) > 0::numeric THEN round((sum(cs_player_gamelogs.stl) * 2)::numeric / sum(cs_player_gamelogs.dk_points), 3)
                        ELSE NULL::numeric
                    END AS stlpct,
                    CASE
                        WHEN sum(cs_player_gamelogs.dk_points) > 0::numeric THEN round((sum(cs_player_gamelogs.blk) * 2)::numeric / sum(cs_player_gamelogs.dk_points), 3)
                        ELSE NULL::numeric
                    END AS blkpct,
                    CASE
                        WHEN sum(cs_player_gamelogs.dk_points) > 0::numeric THEN round(sum(cs_player_gamelogs.tov)::numeric * '-0.5'::numeric / sum(cs_player_gamelogs.dk_points), 3)
                        ELSE NULL::numeric
                    END AS tovpct,
                    CASE
                        WHEN sum(cs_player_gamelogs.dk_points) > 0::numeric THEN round(sum(cs_player_gamelogs.fg3m)::numeric * 0.5 / sum(cs_player_gamelogs.dk_points), 3)
                        ELSE NULL::numeric
                    END AS tpmpct
               FROM cs_player_gamelogs
              GROUP BY cs_player_gamelogs.nbacom_player_id, cs_player_gamelogs.player_name
            )
        SELECT t1.nbacom_player_id,
            t1.player_name, t1.gp, t1.mintot, t1.mpg, t1.dkpg, t1.dkmin, t1.ptspct, t1.rebpct,
            t1.astpct, t1.stlpct, t1.blkpct, t1.tovpct, t1.tpmpct,
            1::numeric - (t1.ptspct + t1.rebpct + t1.astpct + t1.stlpct + t1.blkpct + t1.tovpct + t1.tpmpct) AS bonuspct
           FROM t1
        ORDER BY t1.dkmin DESC
    """

def missing_games_meta():
    """
    Query to determine games in current season where no data for games_meta table

    Returns:
        query string
    """
    return """
         SELECT '00' || games.game_id::text as game_id, TO_CHAR(game_date, 'YYYYmmdd') as game_date
         FROM cs_games games
         WHERE games.game_date < now()::date
         AND NOT (game_id IN (
           SELECT DISTINCT game_id FROM games_meta))
        ORDER BY games.game_id;
    """


def missing_models():
    """
    Query to determine gamedays in current season where no data for models table

    Returns:
        query string
    """
    return """
        SELECT DISTINCT games.game_date
        FROM
            cs_games games
        WHERE
            games.game_date < now()::date
            AND(NOT(games.game_date IN(SELECT DISTINCT game_date FROM models)))
        ORDER BY
            games.game_date DESC;
    """


def missing_odds():
    """
    Query to determine gamedays in current season where no data for odds table

    Returns:
        query string
    """
    return """
        SELECT DISTINCT to_char(game_date, 'YYYYmmdd') as game_date
        FROM cs_games games
        WHERE games.game_date < localdate()
            AND(NOT(games.game_date IN(SELECT DISTINCT game_date FROM odds)))
        ORDER BY game_date DESC;
    """


def missing_ownership():
    """
    Query to determine gamedays in current season where no data for ownership table

    Returns:
        query string
    """
    return """
        SELECT DISTINCT games.game_date
        FROM
            cs_games games
        WHERE
            games.game_date < now()::date
            AND(NOT(games.game_date IN(SELECT DISTINCT ownership.game_date FROM ownership)))
        ORDER BY
            games.game_date DESC;
    """


def missing_player_boxscores():
    """
    Query to determine games in current season where no data for player_boxscores table

    Returns:
        query string
    """
    return """
         SELECT '00' || games.game_id::text
         FROM cs_games games
         WHERE games.game_date < now()::date
         AND NOT (games.game_id IN (
           SELECT DISTINCT player_boxscores_combined.game_id FROM player_boxscores_combined))
        ORDER BY games.game_id;
    """


def missing_player_gamelogs():
    """
    Query to determine games in current season where no data for player_gamelogs table

    Returns:
        query string
    """
    return """
         SELECT '00' || games.game_id::text
         FROM cs_games games
         WHERE games.game_date < now()::date
         AND NOT (game_id IN (
           SELECT DISTINCT game_id FROM cs_player_gamelogs))
        ORDER BY games.game_id;
    """

def missing_playerstats():
    """
    Query to determine gamedays in current season where no data for playerstats table

    Returns:
        query string
    """
    return """
         SELECT DISTINCT games.game_date
         FROM cs_games games
         WHERE games.game_date < now()::date
         AND NOT (games.game_date IN ( SELECT DISTINCT playerstats_daily.as_of FROM playerstats_daily))
         ORDER BY games.game_date DESC;
    """

def missing_salaries():
    """
    Query to determine gamedays in current season where no data for dfs_salaries table

    Returns:
        query string
    """
    return """
        SELECT DISTINCT games.game_date
        FROM
            cs_games games
        WHERE
            games.game_date <= now()::date
                       AND NOT(games.game_date IN
                (SELECT DISTINCT dfs_salaries.game_date
                 FROM dfs_salaries))
        ORDER BY games.game_date DESC
    """


def missing_salaries_ids(source=None):
    """
    Query to identify rows in dfs_salaries table where there is no nbacom_player_id

    Returns:
        query string
    """
    if source:
        return """
            SELECT DISTINCT source_player_name AS n, source_player_id AS id
            FROM
                dfs_salaries
            WHERE
                source = '{}' AND nbacom_player_id IS NULL;
        """.format(source)

    else:
        return """
            SELECT DISTINCT dfs_salaries.source_player_name AS n,
                dfs_salaries.source_player_id AS id
            FROM
                dfs_salaries
            WHERE
                (dfs_salaries.nbacom_player_id IS NULL);
        """


def missing_team_gamelogs():
    """
    Query to determine games in current season where no data for team_gamelogs table

    Returns:
        query string
    """
    return """
        SELECT '00' || games.game_id::text
        FROM cs_games games
        WHERE NOT(games.game_id IN(SELECT DISTINCT game_id FROM team_gamelogs))
        AND games.game_date < now()::date
    """


def missing_teamstats():
    """
    Query to determine gamedays in current season where no data for teamstats table

    Returns:
        query string
    """
    return """
        SELECT DISTINCT games.game_date
        FROM cs_games games
        WHERE NOT(games.game_date IN(SELECT DISTINCT as_of FROM teamstats_daily))
        AND games.game_date < now()::date
        ORDER BY games.game_date DESC;
    """


def missing_team_boxscores():
    """
    Query to determine games in current season where no data for team_boxscores table

    Returns:
        query string
    """
    return """
        SELECT '00' || games.game_id::text
         FROM cs_games games
         WHERE games.game_date < now()::date
         AND NOT (games.game_id IN (
           SELECT DISTINCT team_boxscores_combined.game_id FROM team_boxscores_combined))
        ORDER BY games.game_id;
    """


def missing_team_opponent_dashboard():
    """
        Query to determine gamedays in current season where no data for team_opponent_dashboard table

        Returns:
            query string
    """
    return """
        SELECT DISTINCT games.game_date
        FROM cs_games games
        WHERE games.game_date < now()::date
        AND NOT (games.game_date IN (
            SELECT DISTINCT team_opponent_dashboard.as_of
            FROM team_opponent_dashboard))
        ORDER BY games.game_date DESC;
    """

def optimal_lineups():
    """
    Query for optimal lineups table

    Returns:
        query string
    """
    return """
        WITH ol AS (
          SELECT game_date, nbacom_player_id, "name", dkpts, count(nbacom_player_id) as n
          FROM optimal_lineups
          GROUP BY game_date, nbacom_player_id, "name", dkpts
        ),

        ol2 AS (
          SELECT ol.*,
          ROW_NUMBER() OVER (PARTITION BY game_date ORDER BY n DESC) as rnk
          FROM ol
        )

        SELECT rnk, round(avg(n), 1) as navg
        FROM ol2
        GROUP BY rnk
        ORDER BY rnk
    """

def rotoworld_players():
    '''
    Query to get rotoworld players from depth_charts
    Returns:
        query string
    '''
    return """select source_player_id, source_player_name
           from depth_charts 
           where source='rotoworld'
           """


def today_team_url_codes():
    """
        Query to determine team_url_codes for all teams playing today

        Returns:
            query string
    """
    return """
        SELECT cteams.team_url_code
        FROM cteams
        WHERE (cteams.nbacom_team_id IN ( SELECT teamgames.team_id
               FROM teamgames
              WHERE teamgames.game_date = now()::date));
    """


def update_dfs_salaries_ids():
    """
        Query to update nbacom_player_ids in dfs_salaries table

        Returns:
            query string
    """
    return """
        UPDATE dfs_salaries SET nbacom_player_id = sq.nbacom_player_id
        FROM (SELECT nbacom_player_id, source, source_player_id from player_xref) AS sq
        WHERE dfs_salaries.nbacom_player_id IS NULL
        AND dfs_salaries.source_player_id = sq.source_player_id
        AND dfs_salaries.source = sq.source;
    """


def update_odds():
    """
        Query to update season and game_id in odds table

        Returns:
            query string
    """
    return """
        update odds
        set season = sq.season, game_id = sq.game_id
        from (
            select season, game_id, game_date, visitor_team_code from games
        ) sq
        where odds.game_date = sq.game_date AND odds.away = sq.visitor_team_code AND odds.season IS NULL
    """


if __name__ == '__main__':
    pass