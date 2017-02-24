import datetime as dt
import logging
import time

from nba.parsers.fantasylabs import FantasyLabsNBAParser
from nba.scrapers.fantasylabs import FantasyLabsNBAScraper
from nba.dates import convert_format


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
                self.db.insert_salaries(sals, game_date=convert_format(day, 'std'))
            return sals
        elif all_missing:
            salaries = {}
            for day in self.db.select_list('SELECT game_date FROM missing_salaries'):
                daystr = datetostr(day, 'fl')
                sals = self.parser.dk_salaries(self.scraper.model(daystr), daystr)
                salaries[datetostr(day, 'nba')] = sals
                logging.debug('got salaries for {}'.format(daystr))
                time.sleep(1)
            if self.insert_db:
                self.db.insert_salaries_dict(salaries)
            return salaries
        else:
            raise ValueError('must provide day or set all_missing to True')

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
    #pass

    # update-salaries.py
    # fetches and inserts dfs salaries

    import datetime
    import logging
    import os
    import sys

    import browsercookie
    from configparser import ConfigParser

    from nba.agents.fantasylabs import FantasyLabsNBAAgent
    from nba.db.fantasylabs import FantasyLabsNBAPg
    from nba.dates import *
    from nba.seasons import *

    logger = logging.getLogger('nbadb-update')
    hdlr = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    config = ConfigParser()
    configfn = os.path.join(os.path.expanduser('~'), '.nbadb')
    config.read(configfn)

    flpg = FantasyLabsNBAPg(username=config['nbadb']['username'],
                            password=config['nbadb']['password'],
                            database=config['nbadb']['database'])
    fla = FantasyLabsNBAAgent(db=flpg, cache_name='flabs-nba', cookies=browsercookie.firefox())

   # q = """select distinct game_date from games where season = 2015 order by game_date DESC"""
   # for d in flpg.select_list(q):
   #     try:
   #         fla.salaries(day=datetostr(d, site='fl'))
   #         logger.info('completed {}'.format(d))
   #     except Exception as e:
   #         logger.exception('{} failed: {}'.format(d, e))
   #     finally:
   #         time.sleep(1.5)

    # salaries to get
    # 4-3-2015, 2-4-2015, 2-2-2015, 1-31-2015, 1-30-2015, 1-29-2015, 1-17-2015, 10-29-2015
    # 10-28-2015,

    q = """select distinct game_date from games where season = 2016 order by game_date DESC"""
    for d in flpg.select_list(q):
        try:
            fla.scraper.as_string = True
            model = fla.scraper.model(model_day=datetostr(d, site='fl'), model_name='phan')
            flpg._insert_dict({'game_date': d, 'data': model, 'model_name': 'phan'}, 'models')
            logger.info('completed {}'.format(d))
        except Exception as e:
            logger.exception('{} failed: {}'.format(d, e))
        finally:
            time.sleep(1.5)
