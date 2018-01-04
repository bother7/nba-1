from datetime import datetime
import json
import logging

from psycopg2 import Error

from nba.dates import convert_format, datetostr
from nba.db.pgsql import NBAPostgres


class RotoGrindersNBAPg(NBAPostgres):
    '''
    RG-specific routines for inserting data into tables
    '''


    def __init__(self, username, password, database = 'nbadb',
                 host = 'localhost', port = 5432):
        '''
        Args:
            username: str 'nba'
            password: str 'abc123'
            database: str 'nba'
            host: default localhost
            port: defalut 5432
        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        NBAPostgres.__init__(self, user=username, password=password,
                             database=database)



if __name__ == '__main__':
    pass