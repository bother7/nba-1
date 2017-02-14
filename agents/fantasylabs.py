import datetime as dt
import logging

from nba.parsers.fantasylabs import FantasyLabsNBAParser
from nba.scrapers.fantasylabs import FantasyLabsNBAScraper
from nba.dates import date_list
from nba.seasons import season_start, season_end


class FantasyLabsNBAAgent(object):
    '''
    Performs script-like tasks using fantasylabs scraper, parser, and db module
    Intended to replace standalone scripts so can use common API and tools

    Examples:
        a = FantasyLabsNBAAgent()
        players = a.today_models()
        players, pp_players = a.today_models()
    '''

    def __init__(self, db, cookies=None, cache_name=None):
        '''
        Args:
            db:
            cookies:
            cache_name:
        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.scraper = FantasyLabsNBAScraper(cookies=cookies, cache_name=cache_name)
        self.parser = FantasyLabsNBAParser()
        if db:
            self.db = db
            self.insert_db = True
        else:
            self.insert_db=False

    def one_model(self, model_day, model_name='default'):
        '''
        Gets list of player models for day

        Args:
            model_day (str): in %Y-%m-%d format
            model_name (str): default, cash, etc.
            insert_db (bool): true if want to insert models into database

        Returns:
            players (list): parsed model

        Examples:
            a = FantasyLabsNBAAgent()
            model = a.one_model(model_day='03_01_2016')
        '''
        model = self.scraper.model(model_day=model_day, model_name=model_name)
        players = self.parser.model(content=model, site='dk', gamedate=model_day)

        # need to run through pipeline
        if self.insert_db:
            self.db.insert_salaries(players)
        return players

    def many_models(self, model_name='default', range_start=None, range_end=None, all_missing=False):
        '''
        Gets list of player models for day

        Args:
            range_start (str): in %Y-%m-%d format
            range_end (str): in %Y-%m-%d format
            model_name (str): default, cash, etc.

        Returns:
            players (list): parsed model

        Examples:
            a = FantasyLabsNBAAgent()
            models = a.many_models(range_start='2016-03-01', range_end='2016-03-07')
            models = a.many_models(all_missing=True)
        '''
        players = []
        if all_missing:
            # THIS NEEDS TO BE ADAPTED
            salaries = []
            for day in self.db.select_list('SELECT game_date FROM missing_salaries'):
                daystr = dt.datetime.strftime(day, '%m_%d_%Y')
                sals = self.parser.dk_salaries(self.scraper.model(daystr), daystr)
                salaries.append(sals)
                if self.insert_db:
                    self.db.insert_salaries(sals)
            return [item for sublist in salaries for item in sublist]
        else:
            for d in date_list(range_end, range_start):
                p = self.one_model(model_day=dt.datetime.strftime(d, '%m_%d_%Y'), model_name=model_name)
                if self.insert_db:
                    self.db.insert_models(p)
                players.append(p)
        return [item for sublist in players for item in sublist]

    def salaries(self, day=None, all_missing=False):
        '''
        Args:
            day(str): in mm_dd_YYYY format
        Returns:
            players(list): of player dict
        '''
        if day:
            sals = self.parser.dk_salaries(self.scraper.model(day), day)
            if self.insert_db:
                self.db.insert_salaries(sals)
            return sals
        elif all_missing:
            salaries = []
            for day in self.db.select_list('SELECT game_date FROM missing_salaries'):
                daystr = dt.datetime.strftime(day, '%m_%d_%Y')
                sals = self.parser.dk_salaries(self.scraper.model(daystr), daystr)
                salaries.append(sals)
                if self.insert_db:
                    self.db.insert_salaries(sals)
            return [item for sublist in salaries for item in sublist]
        else:
            return None

    def today_model(self, model_name='default'):
        '''
        Gets list of player models for today's games

        Args:
            model_name (str): default, cash, etc.

        Returns:
            players (list): parsed model

        Examples:
            a = FantasyLabsNBAAgent()
            models = a.today_model()
        '''
        today = dt.datetime.strftime(dt.datetime.today(), '%m_%d_%Y')
        model = self.scraper.model(model_day=today, model_name=model_name)
        return self.parser.model(content=model, gamedate=today)

if __name__ == '__main__':
    pass
