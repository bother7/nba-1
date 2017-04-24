import logging

from nba.db.queries import *
from nba.parsers.donbest import DonBestNBAParser
from nba.scrapers.donbest import DonBestNBAScraper
from nba.pipelines.donbest import game_odds
from nba.dates import convert_format


class DonBestNBAAgent(object):
    '''
    Performs script-like tasks using donbest scraper, parser, and db module
    '''

    def __init__(self, db, cookies=None, cache_name=None):
        '''
        Args:
            db:
            cookies:
            cache_name:
        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.scraper = DonBestNBAScraper(cookies=cookies, cache_name=cache_name)
        self.parser = DonBestNBAParser()
        if db:
            self.db = db
            self.insert_db = True
        else:
            self.insert_db=False


    def odds(self, day=None, all_missing=False):
        '''
        Args:
            day(str): in mm_dd_YYYY format
            all_missing(bool): single day or all missing days in season?
        Returns:
            players(list): of player ownership dict
        '''
        if day:
            day = convert_format(day, 'db')
            odds = self.parser.odds(self.scraper.odds(day), day)
            if odds and self.insert_db:
                self.db.insert_dicts(game_odds(odds), 'odds')
            return odds

        elif all_missing:
            allodds = {}
            for day in self.db.select_list(missing_odds()):
                odds = self.parser.odds(self.scraper.odds(day), day)
                if odds and self.insert_db:
                    self.db.insert_dicts(game_odds(odds), 'odds')
                allodds[day] = odds
            return allodds
        else:
            raise ValueError('must provide day or set all_missing to True')

        if self.insert_db:
            self.db.execute(update_odds())

if __name__ == '__main__':
    pass