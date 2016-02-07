import datetime
import logging
import os
import pprint
import subprocess

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


    def _insert_dict(self, dict_to_insert, table_name):
        '''
        Generic routine to insert dictionary into mysql table
        TODO: not sure what purpose serving - not called by insert_dicts
        '''

        cursor = self.conn.cursor()
        placeholders = ', '.join(['%s'] * len(dict_to_insert))
        columns = ', '.join(dict_to_insert.keys())
        sql = 'INSERT INTO %s ( %s ) VALUES ( %s )' % (table_name, columns, placeholders)

        try:
            cursor.execute(sql, dict_to_insert.values())
            self.conn.commit()

        except Exception as e:
            logging.error('insert statement is {0}'.format(sql))
            logging.error(pprint.pformat(dict_to_insert))
            logging.exception('insert_dicts failed: {0}'.format(e.message))
            self.conn.rollback()

        finally:
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

        cmd = ['pg_dump', "-Upostgres", "--compress=9", "--file=" + bfile, dbname]
        p = subprocess.Popen(cmd)
        retcode = p.wait()

        if retcode > 0:
            print('Error:', dbname, 'backup error')


    def postgres_backup_table(self, dbname, tablename, username='postgres'):
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
        bfile = '{0}_{1}_{2}.sql.gz'.format(dbname, tablename, bdate)

        cmd = ['pg_dump', "--table=" + tablename, "--username=" + username, "--compress=9", "--file=" + bfile, dbname]
        p = subprocess.Popen(cmd)
        retcode = p.wait()

        if retcode > 0:
            print('Error:', dbname, 'backup error')

    def select_dict(self, sql):
        '''
        Generic routine to get list of dictionaries from table

        Arguments:
            sql (str): the select statement you want to execute

        Returns:
            results (list): list of dictionaries representing rows in table
        '''
        
        cursor = self.conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

        try:
            cursor.execute(sql)
            return cursor.fetchall()

        except Exception as e:
            logging.error('sql statement failed: {0}'.format(sql))
            return None

        finally:
            cursor.close()

    def select_list(self, sql):
        '''
        Generic routine to get list of values from one column of table

        Arguments:
            sql (str): the select statement you want to execute

        Returns:
            results (list): list of rows in column
        '''

        cursor = self.conn.cursor()

        try:
            cursor.execute(sql)
            return cursor.fetchall()

        except Exception as e:
            logging.error('sql statement failed: {0}'.format(sql))
            return None

        finally:
            cursor.close()

    def select_scalar(self, sql):
        '''
        Generic routine to get a single value from a table

        Arguments:
            sql (str): the select statement you want to execute

        Returns:
            result: type depends on the query
        '''

        cursor = self.conn.cursor()

        try:
            cursor.execute(sql)
            return cursor.fetchone()[0]

        except Exception as e:
            logging.error('sql statement failed: {0}'.format(sql))
            return None

        finally:
            cursor.close()

    def update(self, sql):
        '''
        Generic routine to update table
        Will rollback with any errors

        Arguments:
            sql(str): UPDATE statement

        Returns:
            None
        '''

        cursor = self.conn.cursor()

        try:
            cursor.execute(sql)
            self.conn.commit()
                
        except Exception as e:
            logging.exception('update failed: {0}'.format(e.message))
            self.conn.rollback()

        finally:
            cursor.close()

if __name__ == '__main__':
    pass
