from __future__ import print_function, division
from collections import defaultdict
import copy
import logging
import os

try:
    import cPickle as pickle

except:
    import pickle

from NBAPlayers import NBAPlayers
from NBAComParser import NBAComParser
from NBAComScraper import NBAComScraper
from NBADailyFantasy import NBADailyFantasy
from NBAPostgres import NBAPostgres
from RotoGuruNBAParser import RotoGuruNBAParser


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
        self.nbap = NBAPlayers()
        self.safe = safe
        
        if db:
            self.nbadb = NBAPostgres()
        else:
            self.nbadb = None

    def _fix_linescores(self, linescores):
        '''
        Removes some keys, changes some keys in linescores dictionary

        Arguments:
            linescores (list): list of dictionaries, each one represents a game linescore from nba.com

        Returns:
            fixed_linescores (list): list of dictionaries, with correct keys/key names
            
        '''
        
        fixed_linescores = []
        exclude = ['game_sequence']

        for linescore in linescores:
            fixed_linescore = {k.lower():v for k,v in linescore.items()}
            fixed_linescore.pop('game_sequence', None)

            fixed_linescore['team_game_id'] = '{0}:{1}'.format(fixed_linescore['team_id'], fixed_linescore['game_id'])
            twl = fixed_linescore.get('team_wins_losses', None)

            if twl:
                wins, losses = twl.split('-')

                if wins and losses:
                    fixed_linescore['team_wins'] = wins
                    fixed_linescore['team_losses'] = losses

            fixed_linescores.append(fixed_linescore)

        return fixed_linescores

    def _players_from_csv(self, csv_fname):
        '''
        Takes csv file and returns dictionary of name: id

        Arguments:
            csv_fname (str): name of file to read/parse

        Returns:
            players (list): list of dicts, key is name, value is id

        Usage:
            csv_fname = os.path.join(os.path.dirname(__file__), 'players.csv')
            players = NBAComAgent._players_from_csv(csv_fname)

        '''
        
        players = {}

        if os.file.exists(csv_fname):
            with open(csv_fname, 'rb') as infile:
                for line in infile:
                    line = line.strip()

                    if line:
                        pname, pid = line.split(';')
                        players[pname] = pid
        else:
            raise ValueError('{0} does not exist'.format(csv_fname))
            
        return players
        
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

    def rg_salaries(self, salary_pages, players_fname, site): 
        '''
        Parses list of rotoguru pages into list of salary dictionaries

        Arguments:
            salary_pages (dict): keyed by gamedate, value is HTML
            players_fname (str): is full path of csv file with players
            site (str): name of site - dk, fd, yh . . . 
            
        Returns:
            salaries (list): list of salary dictionaries
            players (dict): keys are player name, values are player id
            unmatched (defaultdict): keys are playername, values is counter
            
        Usage:
            salaries = NBAComAgent.rotoguru_dfs_salaries(salary_pages, '~/players.csv', 'dk')
            NBAComAgent.nbadb.insert_dicts(salaries, 'salaries')
            
        '''
        
        salaries = []
        players = {}
        unmatched = defaultdict(int)

        players = self._players_from_csv(players_fname)

        for key in sorted(salary_pages.keys()):
            daypage = salary_pages.get(key)

            for sal in p.salaries(daypage, site):

                # players is key of nbacom_name and value of nbacom_id
                # need to match up rotoguru names with these
                pid = players.get(sal.get('site_player_name'), None)

                # if no match, try conversion dictionary
                if not pid:
                    nba_name = self.nbap.rg_to_nbadotcom(sal.get('site_player_name', None))
                    pid = players.get(nba_name, None)

                # if still no match, warn and don't add to database
                if not pid:
                    logging.warning('no player_id for {0}'.format(sal.get('site_player_name')))
                    unmatched[sal.get('site_player_name')] += 1
                    continue

                else:
                    sal['nbacom_player_id'] = pid

                # if no salary, warn and don't add to database    
                if not sal.get('salary', None):
                    logging.warning('no salary for {0}'.format(sal.get('site_player_name')))
                    continue

                salaries.append(sal)               

        return salaries, players, unmatched

    def scoreboards(self, season_start, season_end, pkl_fname=None):
        '''
        Downloads and parses range of scoreboards, optionally saves to pickle file
        '''
        scoreboards = []

        for day in reversed(date_list(season_end, season_start)):
            game_date = datetime.datetime.strftime(day, '%Y-%m-%d')
            scoreboard_json = scraper.scoreboard(game_date=game_date)
            scoreboard = parser.scoreboard(scoreboard_json, game_date=game_date)
            scoreboards.append(scoreboard)       

        if pkl_fname:
            try:
                with open('/home/sansbacon/scoreboards_20160108.pkl', 'wb') as outfile:
                    pickle.dump(scoreboards, outfile)

            except:
                logging.error('could not save scoreboards to {0}'.format(pkl_fname))

        return scoreboards
        
    def teamgames(self, games):
        '''
        Converts list of games into list in teamgames format, where there are2 teamgames for every game

        Arguments:
            games(list): list of games from nba.com where two teams are in 1 row (visitor, home)

        Returns:
            teamgames(list): list of games in teamgames format, 2 teamgames per game row
            
        Usage:
            # is in format {'game_id', 'visitor_team_id', 'home_team_id', . . . }
            games = NBAPostgres.select_dict('SELECT * FROM games')

            # is in format {'game_id', 'team_id', 'opponent_team_id', 'is_home' . . . }
            teamgames = NBAComAgent.teamgames(games)

        '''

        teamgames = []
        to_drop = ['home_team_code', 'home_team_id', 'visitor_team_code', 'visitor_team_id']

        for game in games:
            tg1 = copy.deepcopy(game)
            tg1['team_code'] = game['home_team_code']
            tg1['team_id'] = game['home_team_id']
            tg1['opponent_team_code'] = game['visitor_team_code']   
            tg1['opponent_team_id'] = game['visitor_team_id']
            tg1['is_home'] = True

            teamgames.append({k:v for k,v in tg1.iteritems() if not k in to_drop})

            tg2 = copy.deepcopy(game)
            tg2['team_code'] = game['visitor_team_code']
            tg2['team_id'] = game['visitor_team_id']
            tg2['opponent_team_code'] = game['home_team_code']
            tg2['opponent_team_id'] = game['home_team_id']
            tg2['is_home'] = False

            teamgames.append({k:v for k,v in tg2.iteritems() if not k in to_drop})

        return teamgames

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

        #########################################
        # generate the HTML or other files here #

if __name__ == '__main__':
    pass    
