'''
ESPNNBAScraper
'''

import logging

from nba.scrapers.scraper import BasketballScraper


class ESPNNBAScraper(BasketballScraper):
    '''

    '''

    def __init__(self, headers=None, cookies=None, cache_name=None):
        '''

        Args:
            headers:
            cookies:
            cache_name:
        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        BasketballScraper.__init__(self, headers=headers, cookies=cookies, cache_name=cache_name)

        self.maxindex = 400
        base_url = 'http://games.espn.go.com/fba/tools/projections?startIndex={}'
        idx = [0, 40, 80, 120, 160, 200, 240, 280, 320, 360]
        self.projection_urls = [base_url.format(x) for x in idx]


    def carmelo (self, player_code):
        '''
        Gets CARMELO data for player

        Args:
            player_code: str, ex. lebron-james, dwayne-wade

        Returns:
            JSON parsed into python dict
        '''
        url = 'http://projects.fivethirtyeight.com/carmelo/{0}.json'
        return self.get_json(url.format(player_code))


    def players(self, pages=range(1,11)):
        '''
        Gets all of the ESPN player salaries pages
        Returns:
            pages: list of HTML pages
        '''
        url = 'http://espn.go.com/nba/salaries/_/page/{0}/seasontype/1'
        return [self.get(url.format(page_number)) for page_number in pages]



    def projections(self, subset=None):
        '''
        Gets ESPN's NBA projections

        Args:
            subset: list of offsets

        Returns:
            list of HTML pages
        '''
        if subset:
            return [self.get(self.projection_urls[idx]) for idx in subset]
        else:
            return [self.get(url) for url in self.projection_urls]

    def linescores(self, d):
        url = 'http://www.espn.com/nba/scoreboard/_/date/{}'
        return self.get(url.format(d))


if __name__ == "__main__":
    pass