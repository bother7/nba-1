import datetime as dt
import json
import logging
import os

from nba.parsers.fantasylabs import FantasyLabsNBAParser
from nba.scrapers.fantasylabs import FantasyLabsNBAScraper
from nba.dates import date_list


class FantasyLabsNBAAgent(object):
    '''
    Performs script-like tasks using fantasylabs scraper, parser, and db module
    Intended to replace standalone scripts so can use common API and tools

    Examples:
        a = FantasyLabsNBAAgent()
        players = a.today_models()
        players, pp_players = a.today_models()
    '''

    def __init__(self, cookies=None, cache_name=None, db=None, safe=False):
        '''

        Args:
            cookies:
            cache_name:
            db:
            safe:
        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        if db:
            self.db = db
        self.scraper = FantasyLabsNBAScraper(cookies=cookies, cache_name=cache_name)
        self.parser = FantasyLabsNBAParser()

    def optimizer_pipeline(self, models):
        '''
        Takes fantasylabs models, make ready to create Player objects for pydfs_lineup_optimizer

        Args:
            models (list): is parsed json from day's models

        Returns:
            players (list): list of players, fixed for use in pydfs_lineup_optimizer

        Examples:
            a = FantasyLabsNBAAgent()
            models = a.today_models()
            players = a.optimizer_pipeline(models)

        '''

        fl_keys = ['PlayerId', 'Player_Name', 'Position', 'Team', 'Salary', 'Score', 'AvgPts', 'Ceiling', 'Floor', 'ProjPlusMinus']
        fl_players = [{k: v for k,v in p.items() if k in fl_keys} for p in models]

        # remove null values
        for idx, flp in enumerate(fl_players):
            if flp.get('Ceiling') is None:
                fl_players[idx]['Ceiling'] = 0
            if flp.get('Floor') is None:
                fl_players[idx]['Floor'] = 0
            if flp.get('AvgPts') is None:
                fl_players[idx]['AvgPts'] = 0

        return fl_players

    def past_day_models(self, model_day, model_name='default', fn=None, insert_db=False):
        '''
        Gets list of player models for day

        Args:
            model_day (str): in %Y-%m-%d format
            model_name (str): default, cash, etc.
            fn (str): name of model json file to load from disk
            insert_db (bool): true if want to insert models into database

        Returns:
            players (list): parsed model
            pp_players (list): parsed model, prepared for insert into database

        Examples:
            a = FantasyLabsNBAAgent()
            models = a.past_day_models(model_day='2016-03-01')
            models = a.past_day_models(model_day='2016-03-01', model_name='phan')
            models = a.past_day_models(model_day='2016-03-01', model_name='phan', insert_db=True)

        '''

        if fn:
            with open(fn, 'r') as infile:
                model = json.load(infile)

        else:
            model = self.scraper.model(model_day=model_day, model_name=model_name)

        players = self.parser.model(content=model, site='dk', gamedate=model_day)
        pp_players = self.db.preprocess_salaries(players)

        if self.db and insert_db:
            self.db.insert_salaries(pp_players)

        return players, pp_players

    def range_models(self, range_start, range_end, model_name='default', insert_db=False):
        '''
        Gets list of player models for day

        Args:
            range_start (str): in %Y-%m-%d format
            range_end (str): in %Y-%m-%d format
            model_name (str): default, cash, etc.
            fn (str): name of model json file to load from disk
            insert_db (bool): true if want to insert models into database

        Returns:
            players (list): parsed model
            pp_players (list): parsed model, prepared for insert into database

        Examples:
            a = FantasyLabsNBAAgent()
            models = a.range_models(range_start='2016-03-01', range_end='2016-03-07')
            models = a.range_models(range_start='2016-03-01', range_end='2016-03-07', model_name='phan')
            models = a.range_models(range_start='2016-03-01', range_end='2016-03-07', model_name='phan', insert_db=True)
        '''

        players = []
        pp_players = []

        for d in date_list(range_end, range_start):
            d_players, d_pp_players = self.past_day_models(model_day=dt.datetime.strftime(d, '%Y-%m-%d'), model_name=model_name)
            players += d_players
            pp_players += d_pp_players

        if self.db and insert_db:
            self.db.insert_salaries(pp_players)

        return players, pp_players

    def salaries(self, day):
        '''
        Args:
            day(str): in mm_dd_YYYY format
        Returns:
            players(list): of player dict
        '''
        return self.parser.dk_salaries(self.scraper.model(day), day)

    def today_games(self):
        '''
        Gets list of today's games

        Args:
            None

        Returns:
            list: parsed game json

        Examples:
            a = FantasyLabsNBAAgent()
            games = a.today_games()
        '''

        return self.parser.games(self.scraper.games_today())

    def today_model(self, model_name='phan'):
        '''
        Gets list of player models for today's games

        Args:
            model_name (str): default, cash, etc.
            fn (str): name of model json file to load from disk
            insert_db (bool): true if want to insert models into database

        Returns:
            players (list): parsed model
            pp_players (list): parsed model, prepared for insert into database

        Examples:
            a = FantasyLabsNBAAgent()
            models = a.today_models()
            models = a.today_models(model_name='phan')
            models = a.range_models(model_name='phan', insert_db=True)
        '''
        today = dt.datetime.strftime(dt.datetime.today(), '%Y-%m-%d')
        model = self.scraper.model(model_day=today, model_name=model_name)
        return self.parser.model(content=model, site='dk', gamedate=today)

    def update_models(self, season, model_name='default', insert_db=False):
        '''
        Fills in all missing models
        Query database for dates
        Then fetches missing dates

        Args:
            season (str): in YYYY-YY format
            model_name (str): default, cash, etc.
            insert_db (bool): true if want to insert models into database

        Returns:
            players (list): parsed model
            pp_players (list): parsed model, prepared for insert into database

        Examples:
            a = FantasyLabsNBAAgent()
            models = a.update_models(season='2015-16')
            models = a.update_models(season='2015-16', model_name='phan')
            models = a.update_models(season='2015-16', model_name='phan', insert_db=True)

        '''

        sql = "SELECT DISTINCT game_date FROM dfs.salaries WHERE source='fl' and dfs_site='dk'"

        # now execute it
        
        '''
        model = self.scraper.model(model_day=model_day, model_name=model_name)

        players = self.parser.model(content=model, site='dk', gamedate=model_day)
        pp_players = self.db.preprocess_salaries(players)

        if self.db and insert_db:
            self.db.insert_salaries(pp_players)

        return players, pp_players
        '''

if __name__ == '__main__':
    pass
