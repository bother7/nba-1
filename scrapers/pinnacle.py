'''
PinnacleNBAScraper.py
Gets daily odds xml feed from pinnacle sports
http://xml.pinnaclesports.com/pinnaclefeed.aspx?sporttype=Basketball&sportsubtype=nba
'''

from nba.scrapers import scraper
import logging

class PinnacleNBAScraper(scraper.EWTScraper):
    '''
    Gets daily nba game/odds xml feed from pinnacle sports
    '''

    def __init__(self, **kwargs):
        '''
        EWTScraper parameters: 'dldir', 'expire_time', 'headers', 'keyprefix', 'mc', 'use_cache'
        '''

        # see http://stackoverflow.com/questions/8134444
        EWTScraper.__init__(self, expire_time=300, **kwargs)

        logging.getLogger(__name__).addHandler(logging.NullHandler())

        if 'odds_url' in kwargs:
            self.odds_url = kwargs['odds_url']
        else:
            self.odds_url = 'http://xml.pinnaclesports.com/pinnaclefeed.aspx?sporttype=Basketball'

    def odds(self):
        return self.get(self.odds_url)

if __name__ == "__main__":
    pass
