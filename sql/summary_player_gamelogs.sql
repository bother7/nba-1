# main query
DROP TABLE IF EXISTS tt1;

CREATE TABLE tt1 as
SELECT 
  t1.game_id, t1.player_id as pid, t1.player_name as player, t1.team_abbreviation as team, 
  t1.season, t1.min as minutes, t1.pts as points, fg3m, ftm, reb, ast, tov, stl, blk, plus_minus,
  t1.dk_points, t2.m_dk_points, round(dk_points - m_dk_points, 2) as d_dk_points, 
  round(t1.pts/t1.dk_points, 2) as dk_pts_ratio, t2.m_dk_points_ratio, round(t1.pts/t1.dk_points - t2.m_dk_points_ratio, 2) as d_dk_points_ratio,
  t2.m_dk_points_permin, round(dk_points/min, 2) as dk_pts_permin, round(dk_points/min - m_dk_points_permin, 2) as d_dk_pts_permin,
  t1.wl
FROM nba_dot_com.player_gamelogs t1
INNER JOIN
  (SELECT player_id, season, 
  round(avg(dk_points),2) as m_dk_points,
  round(sum(dk_points)/sum(min),2) as m_dk_points_permin,
  round(sum(pts)/sum(dk_points),2) as m_dk_points_ratio
  FROM player_gamelogs
  GROUP BY player_id, season
) t2
ON t1.player_id = t2.player_id and t1.season = t2.season;

ALTER TABLE tt1 ADD INDEX (game_id);
ALTER TABLE tt1 ADD INDEX (pid, season, wl);

# lookup table for player averages
DROP TABLE IF EXISTS tt2;

CREATE TABLE tt2 as
select pid, player, season, wl, round(avg(dk_points), 2) as wl_dk_pts from tt1
GROUP BY pid, season, wl WITH ROLLUP;

ALTER TABLE tt2 ADD INDEX (pid, season, wl);

DROP TABLE IF EXISTS summary_player_gamelogs;

CREATE TABLE summary_player_gamelogs AS
SELECT date(t3.game_date_est) as game_date, tt1.*, tt2.wl_dk_pts, round(tt1.dk_points - tt2.wl_dk_pts, 2) as d_wl_dk_pts
FROM tt1
INNER JOIN tt2
on tt1.pid = tt2.pid AND tt1.season = tt2.season AND tt1.wl = tt2.wl
INNER JOIN games t3
ON tt1.game_id = t3.game_id;

ALTER TABLE summary_player_gamelogs add column `summary_player_gamelogs_id` int unsigned PRIMARY KEY AUTO_INCREMENT;
ALTER TABLE summary_player_gamelogs ADD INDEX (game_id);
ALTER TABLE summary_player_gamelogs ADD INDEX (pid, season, wl);

DROP TABLE IF EXISTS tt1;
DROP TABLE IF EXISTS tt2;