-- MySQL dump 10.13  Distrib 5.6.27, for Linux (x86_64)
--
-- Host: localhost    Database: nba_dot_com
-- ------------------------------------------------------
-- Server version	5.6.27
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Dumping routines for database 'nba_dot_com'
--
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `dfs_season`()
BEGIN
		DROP TABLE IF EXISTS `tmptbl_dfs_season`;
		
		CREATE TABLE `tmptbl_dfs_season` as
		
		SELECT `t1`.`player_id`, `t1`.`player_name`, `t8`.`primary_position`, `t8`.`position_group`,   `t1`.`team_abbreviation`, `t3`.`visitor_team_code`, `t3`.`home_team_code`, 
		(CASE WHEN `t1`.`team_abbreviation` = `t3`.`visitor_team_code` THEN `t3`.`home_team_code` ELSE `t3`.`visitor_team_code` END) AS `opponent`,
        (CASE WHEN `t1`.`team_abbreviation` = `t3`.`visitor_team_code` THEN 'a' ELSE 'h' END) AS `venue`,
		`t1`.`dk_points`, `t6`.`ceiling`, `t7`.`floor`, `t2`.`mean_dk_pts`, 
		round((`t6`.`ceiling`-`t2`.`mean_dk_pts`)/`t2`.`mean_dk_pts`*100 ,2) as upside,
		round((`t2`.`mean_dk_pts`-`t7`.`floor`)/`t2`.`mean_dk_pts`*100 ,2) as downside,
		round(`t1`.`dk_points` - `t2`.`mean_dk_pts`,2) as `delta`,
		`t4`.`away_dk_avg`, `t5`.`home_dk_avg`,
		`t1`.`game_id`, `t1`.`game_date`, `t1`.`wl`
		
		FROM

		(SELECT `player_id`, `player_name`, `team_abbreviation`, `game_id`, `game_date`, `dk_points`, `wl`
		FROM `nba_dot_com`.`current_season_player_gamelogs`
		) `t1`

		INNER JOIN

		(SELECT `player_id`, round(avg(`dk_points`),2) as `mean_dk_pts`
		FROM `nba_dot_com`.`current_season_player_gamelogs`
		GROUP BY `player_id`) `t2` 
		ON `t1`.`player_id` = `t2`.`player_id`

		INNER JOIN

		(SELECT `game_id`, `visitor_team_code`, `home_team_code` FROM `games`) t3
		ON `t1`.`game_id` = `t3`.`game_id`

		INNER JOIN
		(SELECT `player_id`, round(avg(`dk_points`),2) as `away_dk_avg`
		FROM `nba_dot_com`.`current_season_player_gamelogs` it1, `nba_dot_com`.`games` it2
		WHERE `it1`.`game_id` = `it2`.`game_id` and `it2`.`visitor_team_code` = `it1`.`team_abbreviation`
		GROUP BY `player_id`
		) t4

		ON `t1`.`player_id` = `t4`.`player_id`

		INNER JOIN
		(SELECT `player_id`, round(avg(`dk_points`),2) as `home_dk_avg`
		FROM `nba_dot_com`.`current_season_player_gamelogs` it1, `nba_dot_com`.`games` it2
		WHERE `it1`.`game_id` = `it2`.`game_id` and `it2`.`home_team_code` = `it1`.`team_abbreviation`
		GROUP BY `player_id`
		) t5
		ON `t1`.`player_id` = `t5`.`player_id`

		INNER JOIN

		(select player_id, avg(dk_points) as ceiling
		from `nba_dot_com`.`current_season_player_gamelogs` as f1
		where (
		   select count(*) from `nba_dot_com`.`current_season_player_gamelogs` as f2
		   where f2.player_id = f1.player_id and f2.dk_points >= f1.dk_points
		) <= 5
		GROUP BY player_id) t6
        ON `t1`.`player_id` = `t6`.`player_id`

		INNER JOIN

		(select player_id, avg(dk_points) as floor
		from `nba_dot_com`.`current_season_player_gamelogs` as f1
		where (
		   select count(*) from `nba_dot_com`.`current_season_player_gamelogs` as f2
		   where f2.player_id = f1.player_id and f2.dk_points <= f1.dk_points
		) <= 5
		GROUP BY player_id) t7
        ON `t1`.`player_id` = `t7`.`player_id`
        
        INNER JOIN
        (SELECT person_id, primary_position, position_group
        FROM players) t8
        ON `t1`.`player_id` = `t8`.`person_id`;

		ALTER TABLE `tmptbl_dfs_season` add column `tmptbl_dfs_season_id` int(10) unsigned primary KEY AUTO_INCREMENT;
		ALTER TABLE `tmptbl_dfs_season` ADD INDEX `idx_team` (`team_abbreviation`);
		ALTER TABLE `tmptbl_dfs_season` ADD INDEX `idx_ha` (`venue`, `dk_points`);
		ALTER TABLE `tmptbl_dfs_season` ADD INDEX `idx_dvp` (`opponent`, `position_group`, `dk_points`);
		
		# today's games
        DROP TEMPORARY TABLE IF EXISTS `tmp_today_games`;
        
        CREATE TEMPORARY TABLE `tmp_today_games` AS
		SELECT `visitor_team_code` as `team` from `games` where date(`game_date_est`) = CURDATE()
		UNION DISTINCT
		SELECT `home_team_code` as `team` from `games` where date(`game_date_est`) = CURDATE();

        # aggregate teamstats so have fpts allowed by position
        DROP TABLE IF EXISTS `tmptbl_dfs_teamstats`;
		
		CREATE TABLE `tmptbl_dfs_teamstats` AS
		SELECT t1.team, t1.position_group, round(avg(t1.num_players), 2) as num_players, round(avg(t1.dkpts_allowed),2) as dvp
		FROM
		(SELECT game_date, opponent as team, position_group, sum(dk_points) as dkpts_allowed, count(position_group) as num_players
		FROM tmptbl_dfs_season
		GROUP BY game_id, opponent, position_group) t1

		WHERE t1.team IN (SELECT `team` from `tmp_today_games`)
		GROUP BY t1.team, t1.position_group;

		ALTER TABLE `tmptbl_dfs_teamstats` add column `tmptbl_dfs_teamstats_id` int(10) unsigned primary KEY AUTO_INCREMENT;
		ALTER TABLE `tmptbl_dfs_teamstats` ADD INDEX `idx_team_position_group` (`team`, `position_group`);

        # aggregate playerstats so have today only
        DROP TABLE IF EXISTS `tmptbl_dfs_today`;
		
		CREATE TABLE `tmptbl_dfs_today` AS
		SELECT `game_id`, `game_date`, `player_id`, `player_name`, `primary_position`, `position_group`, 
               `team_abbreviation` as `team`, `opponent`, `venue`, `wl`, 
               `dk_points`, `ceiling`, `floor`, `upside`, `downside`, 
               `delta`, `away_dk_avg`, `home_dk_avg`
		FROM `tmptbl_dfs_season`
		WHERE `team_abbreviation` IN (SELECT `team` from `tmp_today_games`);

		ALTER TABLE `tmptbl_dfs_today` add column `tmptbl_dfs_playerstats_id` int(10) unsigned primary KEY AUTO_INCREMENT;
		ALTER TABLE `tmptbl_dfs_today` ADD INDEX `idx_team_playerids` (`team`, `player_id`);
		ALTER TABLE `tmptbl_dfs_today` ADD INDEX `idx_team_playernames` (`team`, `player_name`);
		ALTER TABLE `tmptbl_dfs_today` ADD INDEX `idx_opp_pos_dkpts` (`opponent`, `primary_position`, `position_group`, `dk_points`);

	END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `dfs_today`()
BEGIN
		DROP TABLE IF EXISTS `tmptbl_dfs_today`;
		
		CREATE TABLE `tmptbl_dfs_today` as
		
		SELECT `t1`.`player_id`, `t1`.`player_name`, `t8`.`primary_position`, `t8`.`position_group`,   `t1`.`team_abbreviation`, `t3`.`visitor_team_code`, `t3`.`home_team_code`, 
		(CASE WHEN `t1`.`team_abbreviation` = `t3`.`visitor_team_code` THEN `t3`.`home_team_code` ELSE `t3`.`visitor_team_code` END) AS `opponent`,
        (CASE WHEN `t1`.`team_abbreviation` = `t3`.`visitor_team_code` THEN 'a' ELSE 'h' END) AS `venue`,
		`t1`.`dk_points`, `t6`.`ceiling`, `t7`.`floor`, `t2`.`mean_dk_pts`, 
		round((`t6`.`ceiling`-`t2`.`mean_dk_pts`)/`t2`.`mean_dk_pts`*100 ,2) as upside,
		round((`t2`.`mean_dk_pts`-`t7`.`floor`)/`t2`.`mean_dk_pts`*100 ,2) as downside,
		round(`t1`.`dk_points` - `t2`.`mean_dk_pts`,2) as `delta`,
		`t4`.`away_dk_avg`, `t5`.`home_dk_avg`,
		`t1`.`game_id`, `t1`.`game_date`, `t1`.`wl`
		
		FROM

		(SELECT `player_id`, `player_name`, `a`.`team_abbreviation`, `game_id`, `game_date`, `dk_points`, `wl`
		FROM `nba_dot_com`.`current_season_player_gamelogs` AS `a`,
		(SELECT `visitor_team_code` AS `team_abbreviation` FROM `games` WHERE DATE(`game_date_est`) = CURDATE()
		UNION ALL
		SELECT `home_team_code` AS `team_abbreviation` FROM `games` WHERE DATE(`game_date_est`) = CURDATE()
		) AS `b`
        WHERE `a`.`team_abbreviation` = `b`.`team_abbreviation`) `t1`

		INNER JOIN

		(SELECT `player_id`, round(avg(`dk_points`),2) as `mean_dk_pts`
		FROM `nba_dot_com`.`current_season_player_gamelogs`
		GROUP BY `player_id`) `t2` 
		ON `t1`.`player_id` = `t2`.`player_id`

		INNER JOIN

		(SELECT `game_id`, `visitor_team_code`, `home_team_code` FROM `games`) t3
		ON `t1`.`game_id` = `t3`.`game_id`

		INNER JOIN
		(SELECT `player_id`, round(avg(`dk_points`),2) as `away_dk_avg`
		FROM `nba_dot_com`.`current_season_player_gamelogs` it1, `nba_dot_com`.`games` it2
		WHERE `it1`.`game_id` = `it2`.`game_id` and `it2`.`visitor_team_code` = `it1`.`team_abbreviation`
		GROUP BY `player_id`
		) t4

		ON `t1`.`player_id` = `t4`.`player_id`

		INNER JOIN
		(SELECT `player_id`, round(avg(`dk_points`),2) as `home_dk_avg`
		FROM `nba_dot_com`.`current_season_player_gamelogs` it1, `nba_dot_com`.`games` it2
		WHERE `it1`.`game_id` = `it2`.`game_id` and `it2`.`home_team_code` = `it1`.`team_abbreviation`
		GROUP BY `player_id`
		) t5
		ON `t1`.`player_id` = `t5`.`player_id`

		INNER JOIN

		(select player_id, avg(dk_points) as ceiling
		from `nba_dot_com`.`current_season_player_gamelogs` as f1
		where (
		   select count(*) from `nba_dot_com`.`current_season_player_gamelogs` as f2
		   where f2.player_id = f1.player_id and f2.dk_points >= f1.dk_points
		) <= 5
		GROUP BY player_id) t6
        ON `t1`.`player_id` = `t6`.`player_id`

		INNER JOIN

		(select player_id, avg(dk_points) as floor
		from `nba_dot_com`.`current_season_player_gamelogs` as f1
		where (
		   select count(*) from `nba_dot_com`.`current_season_player_gamelogs` as f2
		   where f2.player_id = f1.player_id and f2.dk_points <= f1.dk_points
		) <= 5
		GROUP BY player_id) t7
        ON `t1`.`player_id` = `t7`.`player_id`
        
        INNER JOIN
        (SELECT person_id, primary_position, position_group
        FROM players) t8
        ON `t1`.`player_id` = `t8`.`person_id`;

	END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `dfs_today_players`()
BEGIN

	DROP TABLE IF EXISTS `tmp_today`;
	CREATE TABLE `tmp_today` AS

	SELECT a.game_date, a.player_name, a.primary_position, a.team, a.opponent, a.venue, a.wl, a.dk_points, a.floor, a.ceiling
	FROM tmptbl_dfs_today AS a 
	WHERE 
		(SELECT COUNT(*) 
		FROM tmptbl_dfs_today AS b 
		WHERE a.player_name = b.player_name AND b.game_date >= a.game_date
		) <= 5 

	ORDER BY a.player_name ASC, a.game_date DESC;

	ALTER TABLE `tmp_today` ADD `tmp_today_id` INT AUTO_INCREMENT PRIMARY KEY;
	ALTER TABLE `tmp_today` ADD INDEX `idx_team_player_pts` (`team`, `player_name`, `dk_points`);

    SELECT c.game_date, c.player_name, c.primary_position, c.dk_points, d.last5, c.team, c.opponent, c.venue, c.wl, c.floor, c.ceiling
	FROM `tmp_today` AS `c`
	INNER JOIN
	(select player_name, avg(dk_points) as last5 from `tmp_today` GROUP BY player_name) AS d
	ON c.player_name = d.player_name
    ORDER BY c.team, c.player_name, c.game_date DESC;

	END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `dfs_tomorrow`()
BEGIN
    DROP TABLE IF EXISTS `tmptbl_dfs_tomorrow`;
    CREATE TABLE `tmptbl_dfs_tomorrow` as

    SELECT `t1`.`game_id`, `t1`.`game_date`, `t1`.`player_id`, `t1`.`player_name`, `t1`.`team_abbreviation`, 
	(CASE WHEN `t1`.`team_abbreviation` = `t3`.`visitor_team_code` THEN `t3`.`home_team_code` ELSE `t3`.`visitor_team_code` END) AS `opponent`,
    (CASE WHEN `t1`.`team_abbreviation` = `t3`.`visitor_team_code` THEN 'a' ELSE 'h' END) AS `venue`,
    `t1`.`dk_points`, `t2`.`mean_dk_pts`, 
    `t7`.`floor`, `t6`.`ceiling`, 
    round((`t6`.`ceiling`-`t2`.`mean_dk_pts`)/`t2`.`mean_dk_pts`*100 ,2) as upside,
    round((`t2`.`mean_dk_pts`-`t7`.`floor`)/`t2`.`mean_dk_pts`*100 ,2) as downside,
    round(`t1`.`dk_points` - `t2`.`mean_dk_pts`,2) as `delta`,
    `t4`.`away_dk_avg`, `t5`.`home_dk_avg`, `t1`.`wl`

    FROM

    (SELECT `player_id`, `player_name`, `a`.`team_abbreviation`, `game_id`, `game_date`, `dk_points`, `wl`
	FROM `current_season_player_gamelogs` AS `a`, 
	(SELECT `visitor_team_code` as `team_abbreviation` from `games` where date(`game_date_est`) = CURDATE() + INTERVAL 1 DAY
	UNION ALL
	select `home_team_code` as `team_abbreviation` from `games` where date(`game_date_est`) = CURDATE() + INTERVAL 1 DAY
	) AS `b`
	WHERE `a`.`team_abbreviation` = `b`.`team_abbreviation`   	
    ) `t1`

    INNER JOIN

    (SELECT `player_id`, round(avg(`dk_points`),2) as `mean_dk_pts`
    FROM `nba_dot_com`.`current_season_player_gamelogs`
    GROUP BY `player_id`) `t2` 
    ON `t1`.`player_id` = `t2`.`player_id`

    INNER JOIN

    (SELECT `game_id`, `visitor_team_code`, `home_team_code` FROM `games`) t3
    ON `t1`.`game_id` = `t3`.`game_id`

    INNER JOIN
    (SELECT `it1`.`player_id`, round(avg(`it1`.`dk_points`),2) as `away_dk_avg`
    FROM `nba_dot_com`.`current_season_player_gamelogs` it1, `nba_dot_com`.`games` it2
    WHERE `it1`.`game_id` = `it2`.`game_id` and `it2`.`visitor_team_code` = `it1`.`team_abbreviation`
    GROUP BY `player_id`
    ) t4

    ON `t1`.`player_id` = `t4`.`player_id`

    INNER JOIN
    (SELECT `player_id`, round(avg(`dk_points`),2) as `home_dk_avg`
    FROM `nba_dot_com`.`current_season_player_gamelogs` it1, `nba_dot_com`.`games` it2
    WHERE `it1`.`game_id` = `it2`.`game_id` and `it2`.`home_team_code` = `it1`.`team_abbreviation`
    GROUP BY `player_id`
    ) t5
    ON `t1`.`player_id` = `t5`.`player_id`

    INNER JOIN
    (select player_id, avg(dk_points) as ceiling
    from `nba_dot_com`.`current_season_player_gamelogs` as f1
    where (
       select count(*) from `nba_dot_com`.`current_season_player_gamelogs` as f2
       where f2.player_id = f1.player_id and f2.dk_points >= f1.dk_points
    ) <= 5
    GROUP BY player_id) t6
    ON `t1`.`player_id` = `t6`.`player_id`

    INNER JOIN
    (select player_id, avg(dk_points) as floor
    from `nba_dot_com`.`current_season_player_gamelogs` as f1
    where (
       select count(*) from `nba_dot_com`.`current_season_player_gamelogs` as f2
       where f2.player_id = f1.player_id and f2.dk_points <= f1.dk_points
    ) <= 5
    GROUP BY player_id) t7
    ON `t1`.`player_id` = `t7`.`player_id`

	INNER JOIN
	(SELECT person_id, primary_position, position_group
	FROM players) t8
	ON `t1`.`player_id` = `t8`.`person_id`;

    ALTER TABLE `tmptbl_dfs_tomorrow` ADD INDEX `player_id_dk_points` (`player_id`, `dk_points`);
    ALTER TABLE `tmptbl_dfs_tomorrow` ADD INDEX `player_name_dk_points` (`player_name`, `dk_points`);
    ALTER TABLE `tmptbl_dfs_tomorrow` ADD INDEX `team_player_name_dk_points` (`team_abbreviation`, `player_name`, `dk_points`);
    ALTER TABLE `tmptbl_dfs_tomorrow` ADD INDEX `opponent_player_name_dk_points` (`opponent`, `player_name`, `dk_points`);
    ALTER TABLE `tmptbl_dfs_tomorrow` ADD INDEX `venue_player_name_dk_points` (`venue`, `player_name`, `dk_points`);

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `players_avg_last_n`(IN n tinyint)
BEGIN

	DROP TEMPORARY TABLE IF EXISTS `tmptable_players_last_n`;

    CREATE TEMPORARY TABLE `tmptable_players_last_n`
    (INDEX (player_name, dk_points), INDEX (opponent, primary_position, dk_points))
    SELECT a.game_date, a.player_name, c.min, a.primary_position, a.team, 
		   a.opponent, a.venue, a.wl, a.dk_points, a.floor, a.ceiling
		FROM tmptbl_dfs_today AS a 
		INNER JOIN current_season_player_gamelogs AS c
		ON a.game_id = c.game_id AND a.player_name = c.player_name
		WHERE 
			(SELECT COUNT(*) 
			FROM tmptbl_dfs_today AS b 
			WHERE a.player_name = b.player_name AND b.game_date >= a.game_date
			) <= n;

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `players_best_n`(IN n tinyint)
BEGIN
	SELECT a.game_date, a.player_name, c.min, a.primary_position, a.team, a.opponent, a.venue, a.wl, a.dk_points, a.floor, a.ceiling
		FROM tmptbl_dfs_today AS a 
		INNER JOIN current_season_player_gamelogs AS c
		ON a.game_id = c.game_id AND a.player_name = c.player_name
		WHERE 
			(SELECT COUNT(*) 
			FROM tmptbl_dfs_today AS b 
			WHERE a.player_name = b.player_name AND b.dk_points >= a.dk_points
			) <= n
		ORDER BY a.ceiling DESC, a.dk_points DESC;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `players_last_n`(IN n tinyint)
BEGIN
	DROP TEMPORARY TABLE IF EXISTS `tmptable_players_last_n`;
    
    CREATE TEMPORARY TABLE `tmptable_players_last_n`
    (INDEX (`player_name`, `dk_points`))
	SELECT a.game_date, a.player_name, c.min, a.primary_position, a.team, a.opponent, a.venue, a.wl, a.dk_points, a.floor, a.ceiling
	FROM tmptbl_dfs_today AS a 
	INNER JOIN current_season_player_gamelogs AS c
	ON a.game_id = c.game_id AND a.player_name = c.player_name
	WHERE 
	(SELECT COUNT(*) 
	FROM tmptbl_dfs_today AS b 
	WHERE a.player_name = b.player_name AND b.game_date >= a.game_date
	) <= n;

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `player_best_n`(IN plyr varchar(50), IN n tinyint)
BEGIN
	SELECT a.game_date, a.player_name, c.min, a.primary_position, a.team, a.opponent, a.venue, a.wl, a.dk_points, a.floor, a.ceiling
		FROM tmptbl_dfs_today AS a 
		INNER JOIN current_season_player_gamelogs AS c
		ON a.game_id = c.game_id AND a.player_name = c.player_name
		WHERE 
			(SELECT COUNT(*) 
			FROM current_season_player_gamelogs AS b 
			WHERE a.player_name = b.player_name AND b.dk_points >= a.dk_points
			) <= n AND a.player_name = plyr
		ORDER BY a.dk_points DESC;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `player_last_n`(IN plyr varchar(50), IN n tinyint)
BEGIN
	SELECT a.game_date, a.player_name, c.min, a.primary_position, a.team, a.opponent, a.venue, a.wl, a.dk_points, a.floor, a.ceiling
		FROM tmptbl_dfs_today AS a 
		INNER JOIN current_season_player_gamelogs AS c
		ON a.game_id = c.game_id AND a.player_name = c.player_name
		WHERE 
			(SELECT COUNT(*) 
			FROM current_season_player_gamelogs AS b 
			WHERE a.player_name = b.player_name AND b.game_date >= a.game_date
			) <= n AND a.player_name = plyr
		ORDER BY a.game_date DESC;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2016-01-10 10:00:39
