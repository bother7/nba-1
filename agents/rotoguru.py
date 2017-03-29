import logging

from nba.scrapers.rotoguru import RotoGuruNBAScraper
from nba.parsers.rotoguru import RotoGuruNBAParser
from nba.seasons import season_gamedays


class RotoGuruNBAAgent(object):
    '''
    Performs script-like tasks using rotoguru scraper and parser
    Intended to replace standalone scripts so can use common API and tools

    Examples:
        a = RotoguruNBAAgent()
    '''

    def __init__(self, db=None, cache_name=None, cookies=None):
        '''
        Arguments:
            cache_name: str for scraper cache_name
            cookies: cookie jar
            db: NBAPg instance
        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.scraper = RotoGuruNBAScraper(cache_name=cache_name, cookies=cookies)
        self.parser = RotoGuruNBAParser()
        if db:
            self.db = db
            self.insert_db = True
        else:
            self.insert_db=False


    def salaries(self, game_day=None, all_missing=False, site='dk'):
        '''
        Gets rotoguru salary pages
        Args:
            game_day:
            all_missing:
            site:

        Returns:
            sals
        '''
        sals = []
        if game_day:
            content = self.scraper.salaries_day(sday=game_day, site=site)
            sal = self.parser.salaries(content=content, game_date=game_day, site=site)
            if self.insert_db:
                self.db.insert_dicts(sal, 'dfs_salaries')
            return sal

        elif all_missing:
            q = """
                select distinct to_char(game_date, 'YYYYmmdd') as game_date from games
                where season = 2017 and
                game_date NOT IN (select distinct game_date from dfs_salaries where source = 'rotoguru') and
                game_date < localdate()
            """
            if self.insert_db:
                for d in self.db.select_list(q):
                    content = self.scraper.salaries_day(sday=d, site=site)
                    sal = self.parser.salaries(content=content, game_date=d, site=site)
                    sals.append(sal)
                    self.db.insert_dicts(sal, 'dfs_salaries')
                    logging.info('finished salaries for {}'.format(d))
            else:
                for d in season_gamedays(2017, 'db'):
                    content = self.scraper.salaries_day(sday=d, site=site)
                    sal = self.parser.salaries(content=content, game_date=d, site=site)
                    sals.append(sal)
                    logging.info('finished salaries for {}'.format(d))
            return [item for sublist in sals for item in sublist]

        else:
            raise ValueError('must have value for game_day or all_missing parameters')


if __name__ == '__main__':
    pass
