# nba-sql-examples.md

## Game numbers by season

select game_id, gamecode, season, game_date_est, 
@visitor_team_code:=visitor_team_code AS visitor_team_code, 
@rownum := CASE WHEN @visitor_team_code=visitor_team_code THEN @rownum+1 ELSE 1 END AS game_number

FROM games p, (SELECT @rownum:=0, @visitor_team_code:='') r
WHERE season = 2015
ORDER BY visitor_team_code, game_date_est

SELECT t1.game_id, t1.gamecode, t1.season, t1.game_date_est, @team_id:=team_id AS team_id, t2.team_abbreviation, 
@rownum := CASE WHEN @team_id=team_id THEN @rownum+1 ELSE 1 END AS game_number
FROM games AS t1, game_linescores AS t2, (SELECT @rownum:=0, @team_id:='') AS t3
WHERE t1.game_id = t2.game_id
ORDER BY t2.team_id, t1.game_date_est

## Create temporary table

CREATE TEMPORARY TABLE tmp2015 AS
SELECT * from player_gamelogs
WHERE season = 2015;

## Combining multiple tables

SELECT t1.game_id, t1.player_id, t1.player_name, 
       t3.position, t1.team_abbreviation as player_team, t1.dk_points,
       t1.wl, t2.game_date_est, t2.visitor_team_code, t2.home_team_code, t2.season

FROM player_gamelogs as t1, games as t2, players as t3

WHERE t1.game_id = t2.game_id AND t1.player_id = t3.person_id


## Self-join to calculate mean

select t1.game_id, t2.player_id, t1.player_name, t1.position, t1.game_date_est, t1.dk_points, t2.mean_dk_pts
FROM tmp2015 t1, 

(
SELECT player_gamelogs_id as id, player_id, avg(dk_points) as mean_dk_pts
FROM player_gamelogs
WHERE season = 2015
GROUP BY player_id
) t2

WHERE t1.id = t2.id and season = 2015
ORDER BY t2.player_id


