from __future__ import print_function, division
import logging
import random

import MySQLdb  

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
        self.safe = safe
        
        if db:
            self.nbadb = NBAMySQL()
        else:
            self.nbadb = None

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

        gls = self.parser.player_game_logs(content=self.scraper.season_gamelogs(season, 'P'))

        for gl in gls:
            player = gl
            player['dk_points'] = self.dfs.dk_points(player)
            player['fd_points'] = self.dfs.fd_points(player)
            player.pop('video_available'.upper(), None)
            player_gamelogs.append(player)

        # step two: backup table
        if self.safe:
            self.nbadb.mysql_backup_table(self.nbadb.database, 'current_season_player_gamelogs')
    
        # step three: drop / create table
        self.nbadb.create_current_season_player_gamelogs()

        # step four: update table
        table_name = 'current_season_player_gamelogs'
        self.nbadb.insert_dicts(player_gamelogs, table_name)

        return player_gamelogs
        
if __name__ == '__main__':
    a = NBAComAgent()
    gl = a.dfs_player_gamelogs('2015-16')
    print(random.choice(gl))
    #pass
