import logging
import os

from nba.db.pgsql import NBAPostgres


class NBAStufferPgSQL(NBAPostgres):
    '''
    Need to port this to postgres
    Makes sense to inherit from NBAPostgres

    '''


    def __init__(self):

        # see http://stackoverflow.com/questions/8134444
        nba_postgres.NBAPostgres.__init__(self, **kwargs)
        logging.getLogger(__name__).addHandler(logging.NullHandler())


    def insert_games(self, games):
        '''
        TODO: code this out
        '''
        
        for game in games:
            pass


if __name__ == '__main__':
    pass
