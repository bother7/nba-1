import logging

from nba.db import pgsql

class FantasyLabsNBAPg(pgsql.NBAPostgres):
    '''
    Need to port this to postgres
    Makes sense to inherit from NBAPostgres

    '''


    def __init__(self, **kwargs):

        # see http://stackoverflow.com/questions/8134444
        pgsql.NBAPostgres.__init__(self, **kwargs)
        self.logger = logging.getLogger(__name__)

    def insert_models(self, models):
        '''
        TODO: code this out
        '''
        pass

    def insert_salaries(self, models):
        '''
        TODO: code this out
        '''
        pass

if __name__ == '__main__':
    pass
