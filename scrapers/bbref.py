from __future__ import print_function

import logging
import string

from nba.scrapers.scraper import BasketballScraper


class BBRefScraper(BasketballScraper):
    '''
    Usage:
        s = BBRefScraper()
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

    def players(self, initial):
        '''

        Returns:
            content: dict with keys of alphabet
        '''

        base_url = 'http://www.basketball-reference.com/players/{}/'
        return self.get(base_url.format(initial.lower()))

    def player_page(self, pid):
        '''
        Gets page for individual player
        
        Args:
            pid(str): 'smithje01'

        Returns:
            str: HTML of page
        '''

        base_url = 'http://www.basketball-reference.com/players/{}/{}.html'
        return self.get(base_url.format(pid[0].lower(), pid))


if __name__ == "__main__":
    pass