import logging
import os

import MySQLdb


class NBAStufferDB:

    def __init__(self):
        host = os.environ['MYSQL_NBA_HOST']
        user = os.environ['MYSQL_NBA_USER']
        password = os.environ['MYSQL_NBA_PASSWORD']
        database = os.environ['MYSQL_NBA_DATABASE']

        try:
            self.db = MySQLdb.connect(host=host, user=user, passwd=password, db=database, cursorclass=MySQLdb.cursors.DictCursor)

        except:
            pass

    def insert_games(self, games, tbl='nbastuffer'):

        cursor = self.db.cursor()

        for game in games:

            if isinstance(game, list):
                for team in game:
                    try:
                        placeholders = ', '.join(['%s'] * len(team))
                        columns = ', '.join(team.keys())
                        sql = "INSERT INTO %s ( %s ) VALUES ( %s )" % (tbl, columns, placeholders)

                        values = []

                        for value in team.values():
                            if not value:
                                if value == 0:
                                    values.append(value)
                                else:
                                    values.append(None)
                            else:
                                values.append(value)

                        cursor.execute(sql, values)

                    except MySQLdb.Error, e:
                        try:
                            logging.exception('MySQL Error [{0}]: {1}'.format(e.args[0], e.args[1]))
                        except IndexError:
                            logging.exception('MySQL Error: {0}'.format(str(e)))

            else:
                try:
                    placeholders = ', '.join(['%s'] * len(game))
                    columns = ', '.join(game.keys())
                    sql = "INSERT INTO %s ( %s ) VALUES ( %s )" % (tbl, columns, placeholders)
                    values = []

                    for value in game.values():
                        if not value:
                            if value == 0:
                                values.append(value)
                            else:
                                values.append(None)
                        else:
                            values.append(value)

                    cursor.execute(sql, values)

                except MySQLdb.Error, e:
                    try:
                        logging.exception('MySQL Error [{0}]: {1}'.format(e.args[0], e.args[1]))
                    except IndexError:
                        logging.exception('MySQL Error: {0}'.format(str(e)))    
                
        self.db.commit()

if __name__ == '__main__':
    pass
