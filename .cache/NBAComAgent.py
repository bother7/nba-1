import logging

from NBAComParser import NBAComParser
from NBAComScraper import NBAComScraper
from NBADailyFantasy import NBADailyFantasy
from NBAMySQL import NBAMySQL

class NBAComAgent(object):
    '''
    Performs script-like tasks using NBA.com API
    Intended to replace standalone scripts, such as dfs-player-summary

    Examples:
        a = NBAComAgent()
    '''

    def __init__(self, db=True, safe=True):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.scraper = NBAComScraper()
        self.parser = NBAComParser()
        self.dfs = NBADailyFantasy()

        if db:
            self.db = NBAMySQL()
        else:
            self.db = None

    def dfs_player_gamelogs(self, season):
        '''
        Fetches player_gamelogs and updates mysql database

        Arguments:
             season (str): in YYYY-YY format (2015-16)

        Returns:
             players (list): player dictionary of stats + dfs points
        '''

        # step one: get player gamelogs from
        player_gamelogs = []

        gls = self.scraper.season_gamelogs(season, 'P')

        for gl in gls:
            player = gl
            player[u'dk_points'] = self.dfs.dk_points(gl)
            player[u'fd_points'] = self.dfs.fd_points(gl)
            player.pop('video_available', None)
            player_gamelogs.append(player)

        # step two: backup table
        if self.safe:
            self.db.mysql_backup_db('current_season_player_gamelogs')

        # step three: drop / create table
        sql = '''
            DROP TABLE IF EXISTS `current_season_player_gamelogs`;
            CREATE TABLE `current_season_player_gamelogs(`player_gamelogs_id` int(11) NOT NULL AUTO_INCREMENT, `season_id` varchar(255) DEFAULT NULL, `player_id` varchar(255) DEFAULT NULL, `player_name` varchar(255) DEFAULT NULL, `team_abbreviation` varchar(255) DEFAULT NULL, `team_name` varchar(255) DEFAULT NULL, `game_id` varchar(255) DEFAULT NULL, `game_date` varchar(255) DEFAULT NULL, `matchup` varchar(255) DEFAULT NULL, `wl` enum('W','L') DEFAULT NULL, `min` smallint(6) DEFAULT NULL, `fgm` smallint(6) DEFAULT NULL, `fga` smallint(6) DEFAULT NULL, `fg_pct` float DEFAULT NULL, `fg3m` smallint(6) DEFAULT NULL, `fg3a` smallint(6) DEFAULT NULL, `fg3_pct` float DEFAULT NULL, `ftm` smallint(6) DEFAULT NULL, `fta` smallint(6) DEFAULT NULL, `ft_pct` float DEFAULT NULL, `oreb` smallint(6) DEFAULT NULL, `dreb` smallint(6) DEFAULT NULL, `reb` smallint(6) DEFAULT NULL, `ast` smallint(6) DEFAULT NULL, `stl` smallint(6) DEFAULT NULL, `blk` smallint(6) DEFAULT NULL, `tov` smallint(6) DEFAULT NULL, `pf` smallint(6) DEFAULT NULL, `pts` smallint(6) DEFAULT NULL, `plus_minus` smallint(6) DEFAULT NULL, `dk_points` float DEFAULT '0', `fd_points` float DEFAULT '0', PRIMARY KEY (`player_gamelogs_id`), KEY `player_name` (`player_name`), KEY `dk_points` (`dk_points`), KEY `game_id` (`game_id`), KEY `team_abbreviation` (`team_abbreviation`), KEY `player_id_dk_points` (`player_id`,`dk_points`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        '''

        # step three: update table

        tbl = 'current_season_player_gamelogs'

        for player_gamelog in player_gamelogs:
            cursor.execute(sql, player_gamelog.values())

        db.commit()
