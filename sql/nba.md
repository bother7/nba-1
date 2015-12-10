## Table nba.dfs

Combines fields from player_gamelogs with dfs data (fantasy points, salary, etc.)

    CREATE TABLE `dfs` (
      `dfs_id` int(11) NOT NULL AUTO_INCREMENT,
      `game_id` int(11) NOT NULL,
      `players_id` int(11) NOT NULL,
      `site` char(2) NOT NULL,
      `position` char(2) NOT NULL,
      `site_position` char(2) NOT NULL,
      `position_group` enum('Point', 'Wing', 'Big') DEFAULT NULL,
      `points` decimal(5,2) DEFAULT NULL,
      `salary` smallint(5) unsigned NOT NULL,
      PRIMARY KEY (`dfs_id`),
      CONSTRAINT `fk_game_id` FOREIGN KEY (`game_id`) REFERENCES `games` (`game_id`) ON DELETE CASCADE ON UPDATE CASCADE,
      CONSTRAINT `fk_players_id` FOREIGN KEY (`players_id`) REFERENCES `players` (`players_id`) ON DELETE CASCADE ON UPDATE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

## Table nba.game_linescores

Game-by-game results along with breakdowns by quarter. Can see team's record at time of game, opponent, etc.

    CREATE TABLE `game_linescores` (
      `game_linescores_id` int(11) NOT NULL AUTO_INCREMENT,
      `team_game_id` varchar(45) DEFAULT NULL,
      `game_id` int(11) NOT NULL,
      `game_date_est` datetime NOT NULL,
      `team_id` int(11) NOT NULL,
      `team_abbreviation` varchar(3) NOT NULL,
      `team_city_name` varchar(30) NOT NULL,
      `team_wins_losses` varchar(6) DEFAULT NULL,
      `team_wins` tinyint(4) DEFAULT NULL,
      `team_losses` tinyint(4) DEFAULT NULL,
      `pts` tinyint(3) unsigned DEFAULT NULL,
      `pts_qtr1` tinyint(3) unsigned DEFAULT NULL,
      `pts_qtr2` tinyint(3) unsigned DEFAULT NULL,
      `pts_qtr3` tinyint(3) unsigned DEFAULT NULL,
      `pts_qtr4` tinyint(3) unsigned DEFAULT NULL,
      `pts_ot1` tinyint(3) unsigned DEFAULT NULL,
      `pts_ot2` tinyint(3) unsigned DEFAULT NULL,
      `pts_ot3` tinyint(3) unsigned DEFAULT NULL,
      `pts_ot4` tinyint(3) unsigned DEFAULT NULL,
      `pts_ot5` tinyint(3) unsigned DEFAULT NULL,
      `pts_ot6` tinyint(3) unsigned DEFAULT NULL,
      `pts_ot7` tinyint(3) unsigned DEFAULT NULL,
      `pts_ot8` tinyint(3) unsigned DEFAULT NULL,
      `pts_ot9` tinyint(3) unsigned DEFAULT NULL,
      `pts_ot10` tinyint(3) unsigned DEFAULT NULL,
      `fg_pct` decimal(4,3) DEFAULT NULL,
      `ft_pct` decimal(4,3) DEFAULT NULL,
      `fg3_pct` decimal(4,3) DEFAULT NULL,
      `ast` tinyint(3) unsigned DEFAULT NULL,
      `reb` tinyint(3) unsigned DEFAULT NULL,
      `tov` tinyint(3) unsigned DEFAULT NULL,
      PRIMARY KEY (`game_linescores_id`),
      CONSTRAINT `fk_game_id` FOREIGN KEY (`game_id`) REFERENCES `games` (`game_id`) ON DELETE CASCADE ON UPDATE CASCADE,
      UNIQUE KEY `team_game_id_UNIQUE` (`team_game_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

## Table nba.games

List of games from 2000-2016 seasons

    CREATE TABLE `games` (
      `game_id` int(11) NOT NULL,
      `game_date_est` datetime NOT NULL,
      `gamecode` varchar(30) NOT NULL,
      `visitor_team_id` varchar(12) NOT NULL,
      `visitor_team_code` varchar(3) NOT NULL,
      `home_team_id` varchar(12) NOT NULL,
      `home_team_code` varchar(3) NOT NULL,
      `season` smallint(6) NOT NULL,
      PRIMARY KEY (`game_id`),
      UNIQUE KEY `gamecode` (`gamecode`),
      KEY `idx_season` (`season`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

## Table nba.player_gamelogs

Individual player games (boxscores) from 2000-2016 seasons, basic statistics

    CREATE TABLE `player_gamelogs` (
      `player_gamelogs_id` int(11) NOT NULL AUTO_INCREMENT,
      `game_id` varchar(255) DEFAULT NULL,
      `player_id` varchar(255) DEFAULT NULL,
      `player_name` varchar(255) DEFAULT NULL,
      `team_id` varchar(255) DEFAULT NULL,
      `team_abbreviation` varchar(255) DEFAULT NULL,
      `team_city` smallint(6) DEFAULT NULL,
      `start_position` varchar(3) DEFAULT NULL,
      `comment` varchar(255) DEFAULT NULL,
      `season` smallint(6) DEFAULT NULL,
      `season_id` smallint(6) NOT NULL,
      `min` smallint(6) DEFAULT NULL,
      `fgm` smallint(6) DEFAULT NULL,
      `fga` smallint(6) DEFAULT NULL,
      `fg_pct` float DEFAULT NULL,
      `fg3m` smallint(6) DEFAULT NULL,
      `fg3a` smallint(6) DEFAULT NULL,
      `fg3_pct` float DEFAULT NULL,
      `ftm` smallint(6) DEFAULT NULL,
      `fta` smallint(6) DEFAULT NULL,
      `ft_pct` float DEFAULT NULL,
      `oreb` smallint(6) DEFAULT NULL,
      `dreb` smallint(6) DEFAULT NULL,
      `reb` smallint(6) DEFAULT NULL,
      `ast` smallint(6) DEFAULT NULL,
      `tov` smallint(6) DEFAULT NULL,
      `stl` smallint(6) DEFAULT NULL,
      `blk` smallint(6) DEFAULT NULL,
      `pf` smallint(6) DEFAULT NULL,
      `pts` smallint(6) DEFAULT NULL,
      `plus_minus` smallint(6) DEFAULT NULL,
      `dk_points` float DEFAULT '0',
      `fd_points` float DEFAULT '0',
      `wl` enum('W','L') DEFAULT NULL,
      PRIMARY KEY (`player_gamelogs_id`),
      CONSTRAINT `fk_game_id` FOREIGN KEY (`game_id`) REFERENCES `games` (`game_id`) ON DELETE CASCADE ON UPDATE CASCADE,
      KEY `player_name` (`player_name`),
      KEY `dk_points` (`dk_points`),
      KEY `season` (`season`),
      KEY `team_abbreviation` (`team_abbreviation`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

## Table nba.player_gamelogs_advanced

Daily advanced stats from 2000-2016 seasons. Can obtain from leaguedashplayerstats

    CREATE TABLE `player_gamelogs_advanced` (
      `player_gamelogs_advanced_id` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
      `date_of` date NOT NULL,
      `season` smallint(6) DEFAULT NULL,
      `player_id` int(11) DEFAULT NULL,
      `player_name` varchar(50) DEFAULT NULL,
      `team_id` varchar(50) DEFAULT NULL,
      `team_abbreviation` varchar(3) DEFAULT NULL,
      `age` smallint(6) DEFAULT NULL,
      `gp` smallint(6) DEFAULT NULL,
      `w` smallint(6) DEFAULT NULL,
      `l` smallint(6) DEFAULT NULL,
      `w_pct` float DEFAULT NULL,
      `min` smallint(6) DEFAULT NULL,
      `off_rating` float DEFAULT NULL,
      `def_rating` float DEFAULT NULL,
      `net_rating` float DEFAULT NULL,
      `ast_pct` float DEFAULT NULL,
      `ast_to` float DEFAULT NULL,
      `ast_ratio` float DEFAULT NULL,
      `oreb_pct` float DEFAULT NULL,
      `dreb_pct` float DEFAULT NULL,
      `reb_pct` float DEFAULT NULL,
      `tm_tov_pct` float DEFAULT NULL,
      `efg_pct` float DEFAULT NULL,
      `ts_pct` float DEFAULT NULL,
      `usg_pct` float DEFAULT NULL,
      `pace` float DEFAULT NULL,
      `pie` float DEFAULT NULL,
      `cfid` smallint(6) DEFAULT NULL,
      `cfparams` varchar(255) DEFAULT NULL,
      `fgm` tinyint DEFAULT NULL,
      `fga` tinyint DEFAULT NULL,
      `fgm_pg` float default NULL,
      `fga_pg` float default NULL,
      `fg_pct` float default NULL,
      CONSTRAINT `fk_game_id` FOREIGN KEY (`game_id`) REFERENCES `games` (`game_id`) ON DELETE CASCADE ON UPDATE CASCADE,
      KEY `season` (`season`),
      KEY `team_abbreviation` (`team_abbreviation`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

## Table nba.players

Historical list of players

    CREATE TABLE `players` (
      `players_id` int(11) NOT NULL AUTO_INCREMENT,
      `person_id` int(11) DEFAULT NULL,
      `first_name` varchar(50) DEFAULT NULL,
      `last_name` varchar(50) DEFAULT NULL,
      `display_first_last` varchar(50) DEFAULT NULL,
      `display_last_comma_first` varchar(50) DEFAULT NULL,
      `display_fi_last` varchar(50) DEFAULT NULL,
      `birthdate` date DEFAULT NULL,
      `school` varchar(50) DEFAULT NULL,
      `country` varchar(50) DEFAULT NULL,
      `last_affiliation` varchar(50) DEFAULT NULL,
      `height` tinyint(4) DEFAULT NULL,
      `weight` smallint(6) DEFAULT NULL,
      `season_exp` tinyint(4) DEFAULT NULL,
      `jersey` varchar(3) DEFAULT NULL,
      `position` varchar(20) DEFAULT NULL,
      `rosterstatus` varchar(20) DEFAULT NULL,
      `team_id` varchar(30) DEFAULT NULL,
      `team_name` varchar(30) DEFAULT NULL,
      `team_abbreviation` varchar(3) DEFAULT NULL,
      `team_code` varchar(30) DEFAULT NULL,
      `team_city` varchar(30) DEFAULT NULL,
      `playercode` varchar(50) DEFAULT NULL,
      `from_year` smallint(6) DEFAULT NULL,
      `to_year` smallint(6) DEFAULT NULL,
      `dleague_flag` varchar(100) DEFAULT NULL,
      PRIMARY KEY (`players_id`),
      UNIQUE KEY `person_id` (`person_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

## Table nba.projections

Player projections

    CREATE TABLE `projections` (
      `projections_id` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
      `espn_code` varchar(50) DEFAULT NULL,
      `site` varchar(50) NOT NULL,
      `season` smallint NOT NULL,
      `mp_projected` smallint NOT NULL,
      `fgm` decimal(6,2) NOT NULL,
      `fga` decimal(6,2) NOT NULL,
      `tpm` decimal(6,2) NOT NULL,
      `tpa` decimal(6,2) NOT NULL,
      `ftm` decimal(6,2) NOT NULL,
      `fta` decimal(6,2) NOT NULL,
      `tr` decimal(6,2) NOT NULL,
      `as` decimal(6,2) NOT NULL,
      `st` decimal(6,2) NOT NULL,
      `bk` decimal(6,2) NOT NULL,
      `to` decimal(6,2) NOT NULL,
      `pts` decimal(6,2) NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

## Table nba.projections538

scraped CARMELO projections

    CREATE TABLE `projections538` (
      `projections538_id` int(11) NOT NULL AUTO_INCREMENT,
      `espn_id` smallint(6) DEFAULT NULL,
      `espn_code` varchar(50) DEFAULT NULL,
      `age` float NOT NULL,
      `ast_pct` float NOT NULL,
      `ast_pct_ptile_all` float NOT NULL,
      `ast_pct_ptile_pos` float NOT NULL,
      `baseyear` smallint(6) NOT NULL,
      `blk_pct` float NOT NULL,
      `blk_pct_ptile_all` float NOT NULL,
      `blk_pct_ptile_pos` float NOT NULL,
      `category` varchar(50) NOT NULL,
      `draft` smallint(6) DEFAULT NULL,
      `draft_ptile_all` float NOT NULL,
      `draft_ptile_pos` float NOT NULL,
      `ft_freq` float NOT NULL,
      `ft_freq_ptile_all` float NOT NULL,
      `ft_freq_ptile_pos` float NOT NULL,
      `ft_pct` float NOT NULL,
      `ft_pct_ptile_all` float NOT NULL,
      `ft_pct_ptile_pos` float NOT NULL,
      `height` tinyint(4) NOT NULL,
      `height_ptile_all` float NOT NULL,
      `height_ptile_pos` float NOT NULL,
      `mp_last_season` smallint(6) NOT NULL,
      `mp_projected` smallint(6) NOT NULL,
      `opm_last_season` smallint(6) NOT NULL,
      `opm_projected` smallint(6) NOT NULL,
      `per_last_season` smallint(6) NOT NULL,
      `player` varchar(50) NOT NULL,
      `player_id` varchar(10) NOT NULL,
      `position` varchar(5) NOT NULL,
      `reb_pct` float NOT NULL,
      `reb_pct_ptile_all` float NOT NULL,
      `reb_pct_ptile_pos` float NOT NULL,
      `rookie` tinyint(4) DEFAULT '0',
      `stl_pct` float NOT NULL,
      `stl_pct_ptile_all` float NOT NULL,
      `stl_pct_ptile_pos` float NOT NULL,
      `team` varchar(40) DEFAULT NULL,
      `team_abbr` varchar(3) DEFAULT NULL,
      `team_short` varchar(20) DEFAULT NULL,
      `timestamp` float NOT NULL,
      `to_pct` float NOT NULL,
      `to_pct_ptile_all` float NOT NULL,
      `to_pct_ptile_pos` float NOT NULL,
      `tp_freq` float NOT NULL,
      `tp_freq_ptile_all` float NOT NULL,
      `tp_freq_ptile_pos` float NOT NULL,
      `ts_pct` float NOT NULL,
      `ts_pct_ptile_all` float NOT NULL,
      `ts_pct_ptile_pos` float NOT NULL,
      `usg` float NOT NULL,
      `usage_ptile_all` float NOT NULL,
      `usage_ptile_pos` float NOT NULL,
      `value_last_season` float NOT NULL,
      `value_projected` float NOT NULL,
      `war_mean_last_season` float NOT NULL,
      `war_mean_projected` float NOT NULL,
      `weight` smallint(6) NOT NULL,
      `weight_ptile_all` float NOT NULL,
      `weight_ptile_pos` float NOT NULL,
      PRIMARY KEY (`projections538_id`),
      KEY `idx_projections538_player` (`player`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

## Table nba.summary_player_gamelogs

Adds season average to player gamelogs
TODO: add other columns, such as moving average, opponent data, etc.

    CREATE TABLE `summary_player_gamelogs` (
      `game_id` varchar(255) CHARACTER SET utf8 DEFAULT NULL,
      `player_id` varchar(255) CHARACTER SET utf8 DEFAULT NULL,
      `player_name` varchar(255) CHARACTER SET utf8 DEFAULT NULL,
      `position` varchar(20) DEFAULT NULL,
      `player_team_code` varchar(255) CHARACTER SET utf8 DEFAULT NULL,
      `season` smallint(6) DEFAULT NULL,
      `min` smallint(6) DEFAULT NULL,
      `dk_points` float DEFAULT '0',
      `fd_points` float DEFAULT '0',
      `wl` enum('W','L') CHARACTER SET utf8 DEFAULT NULL,
      `game_date_est` datetime NOT NULL,
      `visitor_team_code` varchar(3) NOT NULL,
      `home_team_code` varchar(3) NOT NULL,
      `season_avg` double DEFAULT NULL,
      KEY `game_id` (`game_id`),
      KEY `game_date_est` (`game_date_est`),
      KEY `player_id` (`player_id`),
      KEY `game_date_player` (`game_id`,`player_id`,`game_date_est`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

## Table nba.team_gamelogs

Team-level boxscores, 

    CREATE TABLE `team_gamelogs` (
      `team_gamelogs_id` int(11) NOT NULL AUTO_INCREMENT,
      `team_id` varchar(255) NOT NULL,
      `team_abbreviation` varchar(3) NOT NULL,
      `game_id` int(11) NOT NULL,
      `game_date` datetime NOT NULL,
      `season` smallint(6) NOT NULL,
      `season_id` int(11) NOT NULL,
      `matchup` varchar(30) NOT NULL,
      `away_team_abbreviation` varchar(3) NOT NULL,
      `home_away` enum('A','H') DEFAULT NULL,
      `home_team_abbreviation` varchar(3) NOT NULL,
      `wl` enum('W','L') DEFAULT NULL,
      `min` smallint(5) unsigned DEFAULT NULL,
      `fgm` tinyint(3) unsigned DEFAULT NULL,
      `fga` tinyint(3) unsigned DEFAULT NULL,
      `fg_pct` decimal(4,3) DEFAULT NULL,
      `fg3m` tinyint(3) unsigned DEFAULT NULL,
      `fg3a` tinyint(3) unsigned DEFAULT NULL,
      `fg3_pct` decimal(4,3) DEFAULT NULL,
      `ftm` tinyint(3) unsigned DEFAULT NULL,
      `fta` tinyint(3) unsigned DEFAULT NULL,
      `ft_pct` decimal(4,3) DEFAULT NULL,
      `oreb` tinyint(3) unsigned DEFAULT NULL,
      `dreb` tinyint(3) unsigned DEFAULT NULL,
      `reb` tinyint(3) unsigned DEFAULT NULL,
      `ast` tinyint(3) unsigned DEFAULT NULL,
      `tov` tinyint(3) unsigned DEFAULT NULL,
      `stl` tinyint(3) unsigned DEFAULT NULL,
      `blk` tinyint(3) unsigned DEFAULT NULL,
      `pf` tinyint(3) unsigned DEFAULT NULL,
      `pts` tinyint(3) unsigned DEFAULT NULL,
      `plus_minus` tinyint(4) DEFAULT NULL,
      `opponent_pts` tinyint(3) unsigned DEFAULT NULL,
      PRIMARY KEY (`team_gamelogs_id`)
      CONSTRAINT `fk_game_id` FOREIGN KEY (`game_id`) REFERENCES `games` (`game_id`) ON DELETE CASCADE ON UPDATE CASCADE,
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

## Table nba.team_gamelogs_advanced

Team day-by-day advanced stats

    CREATE TABLE `team_gamelogs_advanced` (
      `team_stats_game_id` int(11) NOT NULL AUTO_INCREMENT,
      `statdate` date NOT NULL,
      `season` smallint(6) DEFAULT NULL,
      `team_id` int(11) NOT NULL,
      `gp` tinyint(3) unsigned NOT NULL,
      `w` tinyint(3) unsigned NOT NULL,
      `l` tinyint(3) unsigned NOT NULL,
      `min` smallint(6) NOT NULL,
      `off_rating` decimal(5,2) NOT NULL,
      `def_rating` decimal(5,2) NOT NULL,
      `net_rating` decimal(5,2) NOT NULL,
      `ast_pct` decimal(5,3) NOT NULL,
      `ast_to` decimal(5,3) NOT NULL,
      `ast_ratio` decimal(5,3) NOT NULL,
      `oreb_pct` decimal(5,3) NOT NULL,
      `dreb_pct` decimal(5,3) NOT NULL,
      `reb_pct` decimal(5,3) NOT NULL,
      `tm_tov_pct` decimal(5,3) NOT NULL,
      `efg_pct` decimal(5,3) NOT NULL,
      `ts_pct` decimal(5,3) NOT NULL,
      `pace` decimal(5,2) NOT NULL,
      `pie` decimal(5,3) NOT NULL,
      PRIMARY KEY (`team_stats_game_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

## Table nba.yearly_playerstats_advanced

Yearlong advanced player stats

    CREATE TABLE `yearly_playerstats_advanced` (
      `player_id` varchar(255) DEFAULT NULL,
      `player_name` varchar(255) DEFAULT NULL,
      `team_id` varchar(255) DEFAULT NULL,
      `team_abbreviation` varchar(255) DEFAULT NULL,
      `season` smallint(6) DEFAULT NULL,
      `age` smallint(6) DEFAULT NULL,
      `gp` smallint(6) DEFAULT NULL,
      `w` smallint(6) DEFAULT NULL,
      `l` smallint(6) DEFAULT NULL,
      `w_pct` float DEFAULT NULL,
      `min` smallint(6) DEFAULT NULL,
      `off_rating` float DEFAULT NULL,
      `def_rating` float DEFAULT NULL,
      `net_rating` float DEFAULT NULL,
      `ast_pct` float DEFAULT NULL,
      `ast_to` float DEFAULT NULL,
      `ast_ratio` float DEFAULT NULL,
      `oreb_pct` float DEFAULT NULL,
      `dreb_pct` float DEFAULT NULL,
      `reb_pct` float DEFAULT NULL,
      `tm_tov_pct` float DEFAULT NULL,
      `efg_pct` float DEFAULT NULL,
      `ts_pct` float DEFAULT NULL,
      `usg_pct` float DEFAULT NULL,
      `pace` float DEFAULT NULL,
      `pie` float DEFAULT NULL,
      `cfid` smallint(6) DEFAULT NULL,
      `cfparams` varchar(255) DEFAULT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;        

## Table nba.yearly_playerstats_advanced

Yearlong basic player stats

    CREATE TABLE `yearly_playerstats_basic` (
      `yearly_playerstats_basic_id` int(11) NOT NULL AUTO_INCREMENT,
      `player_id` varchar(255) DEFAULT NULL,
      `player_name` varchar(255) DEFAULT NULL,
      `team_id` varchar(255) DEFAULT NULL,
      `team_abbreviation` varchar(255) DEFAULT NULL,
      `season` smallint(6) DEFAULT NULL,
      `age` smallint(6) DEFAULT NULL,
      `gp` smallint(6) DEFAULT NULL,
      `w` smallint(6) DEFAULT NULL,
      `l` smallint(6) DEFAULT NULL,
      `w_pct` float DEFAULT NULL,
      `min` smallint(6) DEFAULT NULL,
      `fgm` smallint(6) DEFAULT NULL,
      `fga` smallint(6) DEFAULT NULL,
      `fg_pct` float DEFAULT NULL,
      `fg3m` smallint(6) DEFAULT NULL,
      `fg3a` smallint(6) DEFAULT NULL,
      `fg3_pct` float DEFAULT NULL,
      `ftm` smallint(6) DEFAULT NULL,
      `fta` smallint(6) DEFAULT NULL,
      `ft_pct` float DEFAULT NULL,
      `oreb` smallint(6) DEFAULT NULL,
      `dreb` smallint(6) DEFAULT NULL,
      `reb` smallint(6) DEFAULT NULL,
      `ast` smallint(6) DEFAULT NULL,
      `tov` smallint(6) DEFAULT NULL,
      `stl` smallint(6) DEFAULT NULL,
      `blk` smallint(6) DEFAULT NULL,
      `blka` smallint(6) DEFAULT NULL,
      `pf` smallint(6) DEFAULT NULL,
      `pfd` smallint(6) DEFAULT NULL,
      `pts` smallint(6) DEFAULT NULL,
      `plus_minus` smallint(6) DEFAULT NULL,
      `dd2` smallint(6) DEFAULT NULL,
      `td3` smallint(6) DEFAULT NULL,
      `cfid` smallint(6) DEFAULT NULL,
      `cfparams` varchar(255) DEFAULT NULL,
      PRIMARY KEY (`yearly_playerstats_basic_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
