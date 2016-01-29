DROP TABLE IF EXISTS player_prior_means;

CREATE TABLE player_prior_means AS
SELECT season_id, game_id, player_id, team_abbreviation, dk_points, 
lag(current_mean_dkpoints, 1) OVER w1 AS prior_mean_dkpoints,
lag(current_mean_min, 1) OVER w1 AS prior_mean_min,
lag(current_mean_tpm, 1) OVER w1 AS prior_mean_tpm,
lag(current_mean_reb, 1) OVER w1 AS prior_mean_reb,
lag(current_mean_ast, 1) OVER w1 AS prior_mean_ast,
lag(current_mean_stl, 1) OVER w1 AS prior_mean_stl,
lag(current_mean_blk, 1) OVER w1 AS prior_mean_blk,
lag(current_mean_tov, 1) OVER w1 AS prior_mean_tov,
lag(current_mean_pts, 1) OVER w1 AS prior_mean_pts
FROM
(SELECT season_id, game_id, player_id, team_abbreviation, 
dk_points, avg(dk_points) OVER w2 AS current_mean_dkpoints, 
min, avg(min) OVER w2 AS current_mean_min,
fg3m,  avg(fg3m) OVER w2 as current_mean_tpm,
reb,  avg(reb) OVER w2 as current_mean_reb,
ast,  avg(ast) OVER w2 as current_mean_ast,
stl,  avg(stl) OVER w2 as current_mean_stl,
blk,  avg(blk) OVER w2 as current_mean_blk,
tov,  avg(tov) OVER w2 as current_mean_tov,
pts,  avg(pts) OVER w2 as current_mean_pts
FROM current_season_player_gamelogs
WINDOW w2 AS (PARTITION BY player_id, season_id ORDER BY game_id rows unbounded preceding)
) AS t1
WINDOW w1 AS (PARTITION BY player_id, season_id  ORDER BY season_id, game_id)

UNION ALL

SELECT season_id, game_id, player_id, team_abbreviation, dk_points, 
lag(current_mean_dkpoints, 1) OVER w3 AS prior_mean_dkpoints,
lag(current_mean_min, 1) OVER w3 AS prior_mean_min,
lag(current_mean_tpm, 1) OVER w3 AS prior_mean_tpm,
lag(current_mean_reb, 1) OVER w3 AS prior_mean_reb,
lag(current_mean_ast, 1) OVER w3 AS prior_mean_ast,
lag(current_mean_stl, 1) OVER w3 AS prior_mean_stl,
lag(current_mean_blk, 1) OVER w3 AS prior_mean_blk,
lag(current_mean_tov, 1) OVER w3 AS prior_mean_tov,
lag(current_mean_pts, 1) OVER w3 AS prior_mean_pts
FROM
(SELECT season_id, game_id, player_id, team_abbreviation, 
dk_points, avg(dk_points) OVER w4 AS current_mean_dkpoints, 
min, avg(min) OVER w4 AS current_mean_min,
fg3m,  avg(fg3m) OVER w4 as current_mean_tpm,
reb,  avg(reb) OVER w4 as current_mean_reb,
ast,  avg(ast) OVER w4 as current_mean_ast,
stl,  avg(stl) OVER w4 as current_mean_stl,
blk,  avg(blk) OVER w4 as current_mean_blk,
tov,  avg(tov) OVER w4 as current_mean_tov,
pts,  avg(pts) OVER w4 as current_mean_pts
FROM player_gamelogs
WINDOW w4 AS (PARTITION BY player_id, season_id ORDER BY game_id rows unbounded preceding)
) AS t2
WINDOW w3 AS (PARTITION BY player_id, season_id  ORDER BY season_id, game_id)

CREATE INDEX ON player_prior_means(season_id, game_id, player_id, dk_points);
CREATE INDEX ON player_prior_means(season_id, team_abbreviation, dk_points, prior_mean_dkpoints);
CREATE INDEX ON player_prior_means(season_id, team_abbreviation, game_id);
