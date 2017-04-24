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


    def odds(self, game_date):
        '''
        Gets odds for specific date

        Args:
            game_date: str
        '''
        results = []
        q = """SELECT data FROM rotogrinders WHERE game_date = '{}'"""
        data = self.select_scalar(q.format(convert_format(game_date, 'nba')))

        for gid, gdata in data.items():
            hid = gdata['data']['home_id']
            vid = gdata['data']['away_id']
            hcode = gdata['data']['team_home']['data']['hashtag']
            vcode = gdata['data']['team_away']['data']['hashtag']
            vegas = gdata['data']['vegas']

            # they have odds with various timestamps during the day
            if vegas:
                stamps = [datetime.strptime(k, '%Y-%m-%d %H:%M:%S') for k in vegas]
                if stamps:
                    fmt = '%Y-%m-%d %H:%M:%S'
                    maxts = datetime.strftime(max(stamps), fmt)
                    newest = vegas[maxts]
                    results.append({'game_id': gid,
                        'ts': maxts,
                        'visitor_team_id': vid,
                        'visitor_team_code': vcode.upper(),
                        'visitor_team_spread': float(newest['spread']['spread_visiting']),
                        'home_team_id': hid,
                        'home_team_code': hcode.upper(),
                        'home_team_spread': float(newest['spread']['spread_home']),
                        'game_ou': float(newest['total']['total_points']),
                        'delta_visiting': float(newest['team_total']['delta_visiting']),
                        'delta_home': float(newest['team_total']['delta_home']),
                        'team_total_home': float(newest['team_total']['team_total_home']),
                        'team_total_visiting': float(newest['team_total']['team_total_visiting'])
                    })

        return results

if __name__ == '__main__':
    pass