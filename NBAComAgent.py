from __future__ import print_function, division
import logging
import os
import random

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
        gamelogs = a.dfs_player_gamelogs('2015-16')
        site = a.website(webdir='/var/www/nbadata')

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

	# need to remove video_available column AND leading zeroes from game_id
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

    def game_linescores(self, dates, table_name):
        '''
        Fetches linescores and inserts into table_name (either current_season_game_linescores or game_linescores)
        '''       

        scoreboards = []
        
        for day in dates:
            game_date = datetime.datetime.strftime(day, '%Y-%m-%d')
            scoreboard_json = scraper.scoreboard(game_date=game_date)
            scoreboard = parser.scoreboard(scoreboard_json, game_date=game_date)
            scoreboards.append(scoreboard)

        linescores = []

        for scb in scoreboards:
            linescores += scb.get('game_linescores', [])

        self.nbadb.insert_dicts(linescores, table_name)

    def website(self, webdir):
        '''
        Generates static website to upload to S3 bucket
        ''' 
        # player_gamelogs
        sql = '''SELECT * FROM current_season_player_gamelogs'''
        gamelogs = self.nbadb.select_dict(sql)

        # TODO: create table `current_season_team_gamelogs`
        # team_gamelogs
        sql = '''SELECT * FROM current_season_team_gamelogs'''
        gamelogs = self.nbadb.select_dict(sql)
        
        # daily fantasy (dfs_season procedure updates the relevant tables)
        self.nbadb.call(procedure_name='dfs_season')
        sql = '''SELECT * FROM tmptbl_dfs_season'''
        dfs_season = self.nbadb.select_dict(sql)

        sql = '''SELECT * FROM tmptbl_dfs_today'''
        dfs_today = self.nbadb.select_dict(sql)

        print(random.choice(dfs_season))
        print(random.choice(dfs_today))

        #########################################
        # generate the HTML or other files here #

if __name__ == '__main__':
    pass    
