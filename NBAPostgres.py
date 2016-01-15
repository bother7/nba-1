import datetime
import logging
import os
import pprint
import subprocess
import tarfile

import psycopg2
import psycopg2.extras

class NBAPostgres(object):

    def __init__(self, with_db=True, **kwargs):
        '''
        Arguments:
            user (str): postgres username
            database (str): postgres database name

        '''

        logging.getLogger(__name__).addHandler(logging.NullHandler())

        if 'user' in kwargs:
            self.user = kwargs['user']
        else:
            self.user = 'postgres'

        if 'database' in kwargs:
            self.database = kwargs['database']
        else:
            self.database = 'nba'

        if with_db:
            self.conn = psycopg2.connect('dbname={0} user={1}'.format(self.database, self.user))

    def create_current_season_player_gamelogs(self):
        '''
        Drops then creates table `current_season_player_gamelogs`
        TODO: adapt to postgresql table structure
        cursor = self.conn.cursor()
        
        sql = '''
        '''

        cursor.execute(sql)
        cursor.close()
        '''
        pass
        
    def _insert_dict(self, dict_to_insert, table_name):
        '''
        Generic routine to insert dictionary into mysql table
        TODO: not sure what purpose serving - not called by insert_dicts
        '''

        cursor = self.conn.cursor()
        placeholders = ', '.join(['%s'] * len(dict_to_insert))
        columns = ', '.join(dict_to_insert.keys())
        sql = 'INSERT INTO %s ( %s ) VALUES ( %s )' % (table_name, columns, placeholders)
        logging.debug('insert statement is {0}'.format(sql))
        cursor.execute(sql, dict_to_insert.values())
        cursor.close()

    def insert_dicts(self, dicts_to_insert, table_name):
        '''
        Generic routine to insert dictionary into mysql table
        Will rollback with any errors

        Arguments:
            dicts_to_insert(list): list of dictionaries to insert, keys match columns
            table_name(str): name of database table

        Returns:
            None
        '''

        cursor = self.conn.cursor()
        placeholders = ', '.join(['%s'] * len(dicts_to_insert[0]))
        columns = ', '.join(dicts_to_insert[0].keys())
        sql = 'INSERT INTO %s ( %s ) VALUES ( %s )' % (table_name, columns, placeholders)

        try:
            for dict_to_insert in dicts_to_insert:
                cursor.execute(sql, dict_to_insert.values())

            self.conn.commit()
                
        except Exception as e:
            logging.error('insert statement is {0}'.format(sql))
            logging.error(pprint.pformat(dict_to_insert))
            logging.exception('insert_dicts failed: {0}'.format(e.message))
            self.conn.rollback()

        finally:
            cursor.close()
                
    def postgres_backup_db(self, dbname, dirname=None):
        '''
        Compressed backup of database

        Args:
            dbname (str): the name of the database
            dirname (str): the name of the backup dirnameectory, default is home

        Returns:
            None           
        '''

        bdate = datetime.datetime.now().strftime('%Y%m%d%H%M')
        bfile = '{0}_{1}.sql'.format(dbname ,bdate)

        if dirname and os.path.exists(dirname):
            pass

        else:
            dirname = os.path.expanduser('~')

        cmd = ['pg_dump', "--compress=9", "--file=" + bfile, dbname]
        p = subprocess.Popen(cmd, stdout=dumpfile)
        retcode = p.wait()

        if retcode > 0:
            print('Error:', dbname, 'backup error')


    def postgres_backup_table(self, dbname, tablename, dirname=None):
        '''
        Compressed backup of mysql database table
        Based on https://mcdee.com.au/python-mysql-backup-script/

        Args:
            dbname (str): the name of the mysql database
            dbname (str): the name of the mysql database table
            dirname (str): the name of the backup dirnameectory, default is home

        Returns:
            None           
        '''

        bdate = datetime.datetime.now().strftime('%Y%m%d%H%M')
        bfile = '{0}_{1}.sql'.format(dbname ,bdate)

        if dirname and os.path.exists(dirname):
            pass

        else:
            dirname = os.path.expanduser('~')

        cmd = ['pg_dump', "--compress=9", "--file=" + bfile, dbname]
        p = subprocess.Popen(cmd, stdout=dumpfile)
        retcode = p.wait()

        if retcode > 0:
            print('Error:', dbname, 'backup error')

    def players_to_add(self):
        '''
        TODO: Adapt to postgres
        Purpose is to compare current_season_gamelogs and players tables to see if missing players in latter
        '''

        sql = '''
            SELECT  DISTINCT player_id, player_name
            FROM    current_season_player_gamelogs AS c
            WHERE   NOT EXISTS
                    (
                    SELECT  1
                    FROM    players p
                    WHERE   p.person_id = c.player_id
                    )
        '''

        cursor = self.conn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()

    def select_dict(self, sql):
        '''
        Generic routine to get list of dictionaries from table

        Arguments:
            sql (str): the select statement you want to execute

        Returns:
            results (list): list of dictionaries representing rows in table
        '''
        
        cursor = self.conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        cursor.execute(sql)
        results = cursor.fetchall()
        return results

if __name__ == '__main__':
    pass
