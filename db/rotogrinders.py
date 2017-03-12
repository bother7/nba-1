import json
import logging

from psycopg2 import Error

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


    def insert_odds(self, game_date, data):
        '''
        Adds odds JSON to table

        Args:
            game_date: str
            data: javascript string
        '''
        with self.conn.cursor() as cursor:
            try:
                cursor.execute(
                    '''INSERT INTO rotogrinders ("game_date", "data")
                    VALUES (%s, %s) ON CONFLICT ("game_date") DO UPDATE SET "data" = EXCLUDED.data;''',
                    (game_date, json.dumps(data))
                )
                self.conn.commit()
            except Error as e:
                logging.exception('update failed: {0}'.format(e))
                self.conn.rollback()


if __name__ == '__main__':
    pass