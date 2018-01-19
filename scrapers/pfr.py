'''
PfrNFLScraper

'''

import logging
from string import ascii_lowercase

from nba.scrapers.scraper import BasketballScraper


class PfrNBAScraper(BasketballScraper):

    '''
    @property
    def pgl_finder_url(self):
        return 'https://www.pro-football-reference.com/play-index/pgl_finder.cgi?'

    @property
    def tgl_finder_url(self):
        return 'https://www.pro-football-reference.com/play-index/tgl_finder.cgi?'

    @property
    def params(self):
        return {
            'request': 1, 'match': 'game', 'year_min': 2016, 'year_max': 2016,
            'season_start': 1, 'season_end': -1, 'age_min': 0, 'age_max': 0, 'pos': '', 'game_type': 'R',
            'career_game_num_min': 0, 'career_game_num_max': 499, 'game_num_min': 0, 'game_num_max': 99,
            'week_num_min': 1, 'week_num_max': 20, 'c1stat': 'fantasy_points', 'c1comp': 'gt',
            'c1val': -5, 'c5val': 1.0, 'c2stat': 'choose', 'c2comp': 'gt', 'c3stat': 'choose', 'c3comp': 'gt',
            'c4stat': 'choose', 'c4comp': 'gt', 'c5comp': 'choose', 'c5gtlt': 'lt', 'c6mult': 1.0,
            'c6comp': 'choose', 'offset': 0, 'order_by': 'game_date', 'order_by_asc': 'Y'
        }
    '''

    def player_page(self, pid):
        '''
        Gets player page for one player

        Args:
            pid (str): e.g. AllenRa01

        Returns:
            str
            
        '''
        url = 'https://www.basketball-reference.com/players/{}/{}.html'
        return self.get(url.format(pid[0].lower(), pid.lower()))

    def players(self, last_initial):
        '''
        Gets player page for last initial, such as A, B, C
        
        Args:
            last_initial: str A, B, C

        Returns:
            HTML string
        '''
        last_initial = last_initial.lower()
        if last_initial in ascii_lowercase:
            url = 'https://www.basketball-reference.com/players/{}/'.format(last_initial)
            logging.info('getting {}'.format(url))
            return self.get(url)
        else:
            raise ValueError('invalid last_initial')


if __name__ == "__main__":
    pass