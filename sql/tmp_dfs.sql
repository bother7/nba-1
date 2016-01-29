DROP TABLE IF EXISTS tmp_dfs;

CREATE TABLE tmp_dfs AS
SELECT t1.season_id, t1.game_id, t1.player_id, t1.dk_points, t1.prior_mean_dkpoints, t1.prior_mean_min,
t1.prior_mean_tpm, t1.prior_mean_reb, t1.prior_mean_ast, t1.prior_mean_stl, t1.prior_mean_blk,
t1.prior_mean_tov, t1.prior_mean_pts,
t2.game_date_est, t2.team_id, t2.opponent_team_id, t2.opponent_team_code, t2.is_home
FROM
player_prior_means t1
INNER JOIN 
teamgames t2
ON t1.game_id = t2.game_id and t1.team_abbreviation=t2.team_code;

ALTER TABLE tmp_dfs ADD COLUMN tmp_dfs_id SERIAL;
UPDATE tmp_dfs SET tmp_dfs_id = DEFAULT;
ALTER TABLE tmp_dfs ADD PRIMARY KEY (tmp_dfs_id);

CREATE INDEX ON tmp_dfs(game_date_est, player_id, dk_points);
CREATE INDEX ON tmp_dfs(season_id, opponent_team_id, dk_points);

COPY tmp_dfs to '/home/sansbacon/pg/tmp_dfs.csv' DELIMITER ';' CSV HEADER;
