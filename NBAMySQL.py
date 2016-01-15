import datetime
import logging
import os
import subprocess
import tarfile

import MySQLdb
import MySQLdb.cursors


class NBAMySQL(object):

    def __init__(self, with_db=True, **kwargs):
        '''
        Arguments:
            host (str): mysql hostname
            user (str): mysql username
            password (str): mysql password
            database (str): mysql database name

        '''

        logging.getLogger(__name__).addHandler(logging.NullHandler())

        if 'host' in kwargs:
            self.host = kwargs['host']
        else:
            self.host = os.environ['MYSQL_NBA_HOST']

        if 'user' in kwargs:
            self.user = kwargs['user']
        else:
            self.user = os.environ['MYSQL_NBA_USER']

        if 'password' in kwargs:
            self.password = kwargs['password']
        else:
            self.password = os.environ['MYSQL_NBA_PASSWORD']

        if 'database' in kwargs:
            self.database = kwargs['database']
        else:
            self.database = os.environ['MYSQL_NBA_DATABASE']

        if with_db:
            self.conn = MySQLdb.connect(host=self.host, user=self.user, passwd=self.password, db=self.database)

    def _backup_compress(self, dirname, bfile):
        tar = tarfile.open(os.path.join(dirname, bfile)+'.tar.gz', 'w:gz')
        tar.add(os.path.join(dirname, bfile), arcname=bfile)
        tar.close()
        os.remove(os.path.join(dirname, bfile))

    def create_current_season_player_gamelogs(self):
        '''
        Drops then creates table `current_season_player_gamelogs`
        '''
        cursor = self.conn.cursor()
        
        sql = '''
            DROP TABLE IF EXISTS `current_season_player_gamelogs`;
            CREATE TABLE `current_season_player_gamelogs` (
            `player_gamelogs_id` int(11) NOT NULL AUTO_INCREMENT, `season_id` int(11) DEFAULT NULL, `player_id` int(11) DEFAULT NULL, `player_name` varchar(250) DEFAULT NULL, `team_abbreviation` varchar(5) DEFAULT NULL, `team_name` varchar(50) DEFAULT NULL, `game_id` int(11) DEFAULT NULL, `game_date` datetime DEFAULT NULL, `matchup` varchar(255) DEFAULT NULL, `wl` enum('W','L') DEFAULT NULL, `min` smallint(6) DEFAULT NULL, `fgm` smallint(6) DEFAULT NULL, `fga` smallint(6) DEFAULT NULL, `fg_pct` float DEFAULT NULL, `fg3m` smallint(6) DEFAULT NULL, `fg3a` smallint(6) DEFAULT NULL, `fg3_pct` float DEFAULT NULL, `ftm` smallint(6) DEFAULT NULL, `fta` smallint(6) DEFAULT NULL, `ft_pct` float DEFAULT NULL, `oreb` smallint(6) DEFAULT NULL, `dreb` smallint(6) DEFAULT NULL, `reb` smallint(6) DEFAULT NULL, `ast` smallint(6) DEFAULT NULL, `stl` smallint(6) DEFAULT NULL, `blk` smallint(6) DEFAULT NULL, `tov` smallint(6) DEFAULT NULL, `pf` smallint(6) DEFAULT NULL, `pts` smallint(6) DEFAULT NULL, `plus_minus` smallint(6) DEFAULT NULL, `dk_points` decimal(10,0) DEFAULT '0', `fd_points` decimal(10,0) DEFAULT '0', PRIMARY KEY (`player_gamelogs_id`), FOREIGN KEY (`game_id`) REFERENCES `games` (`game_id`) ON DELETE SET NULL ON UPDATE SET NULL, KEY `game_id` (`game_id`), KEY `player_id_dk_points` (`player_id`,`dk_points`), KEY `dk_points` (`dk_points`,`player_name`,`player_id`), KEY `team_abbreviation` (`team_abbreviation`,`player_name`,`dk_points`), KEY `team_abbreviation_game_id` (`team_abbreviation`,`game_id`,`player_id`), KEY `team_abbreviation_game_id_date` (`team_abbreviation`,`game_id`,`game_date`), KEY `team_game_date` (`team_abbreviation`,`game_date`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        '''

        cursor.execute(sql)
        cursor.close()
        
    def _insert_dict(self, dict_to_insert, table_name):
        '''
        Generic routine to insert dictionary into mysql table
        '''

        cursor = self.conn.cursor()
        placeholders = ', '.join(['%s'] * len(dict_to_insert))
        columns = ', '.join(dict_to_insert.keys())
        sql = 'INSERT INTO %s ( %s ) VALUES ( %s )' % (table_name, columns, placeholders)
        cursor.execute(sql, dict_to_insert.values())
        cursor.close()

    def call(self, procedure_name, params=None):
        '''
        Calls stored procedure, returns resultset (if any)
        TODO: generate SQL for params
        '''
        
        cursor = self.conn.cursor()

        if not params: 
            sql = '''CALL {0}()'''.format(procedure_name)
            cursor.execute(sql)

        else:
            raise ValueError('Cannot pass parameters at this time')

        # this needs to improve, should have method for testing if procedure returns results
        try:
            return cursor.fetchall()
        except:
            pass

    def insert_dicts(self, dicts_to_insert, table_name):
        '''
        Generic routine to insert dictionary into mysql table
        '''

        cursor = self.conn.cursor()
        placeholders = ', '.join(['%s'] * len(dicts_to_insert[0]))
        columns = ', '.join(dicts_to_insert[0].keys())
        sql = 'INSERT INTO %s ( %s ) VALUES ( %s )' % (table_name, columns, placeholders)
        
        try:
            for dict_to_insert in dicts_to_insert:
                cursor.execute(sql, dict_to_insert.values())

            self.conn.commit()
            
        except MySQLdb.Error as e:
            logging.exception('insert_dicts failed: {0}'.format(e.message))      
            self.conn.rollback()

        finally:
            cursor.close()

    def mysql_backup_db(self, dbname, dirname=None):
        '''
        Compressed backup of mysql database
        Based on https://mcdee.com.au/python-mysql-backup-script/

        Args:
            dbname (str): the name of the mysql database
            dirname (str): the name of the backup dirnameectory, default is home
        '''

        bdate = datetime.datetime.now().strftime('%Y%m%d%H%M')
        bfile = '{0}_{1}.sql'.format(dbname ,bdate)

        if dirname and os.path.exists(dirname):
            pass

        else:
            dirname = os.path.expanduser('~')

        with open(os.path.join(dirname, bfile), 'w') as dumpfile:
            cmd = ['mysqldump', "--routines", "--user=" + os.environ['MYSQL_NBA_USER'], "--password=" + os.environ['MYSQL_NBA_PASSWORD'], dbname]

            p = subprocess.Popen(cmd, stdout=dumpfile)
            retcode = p.wait()

            if retcode > 0:
                print('Error:', dbname, 'backup error')

            else:
                self._backup_compress(dirname, bfile)

    def mysql_backup_table(self, dbname, tablename, dirname=None):
        '''
        Compressed backup of mysql database table
        Based on https://mcdee.com.au/python-mysql-backup-script/

        Args:
            dbname (str): the name of the mysql database
            dbname (str): the name of the mysql database table
            dirname (str): the name of the backup dirnameectory, default is home
        '''

        bdate = datetime.datetime.now().strftime('%Y%m%d%H%M')
        bfile = 'db-{0}_table-{1}_{2}.sql'.format(dbname, tablename, bdate)

        if dirname and os.path.exists(dirname):
            pass

        else:
            dirname = os.path.expanduser('~')

        with open(os.path.join(dirname, bfile), 'w') as dumpfile:
            cmd = ['mysqldump', "--routines", "--user=" + os.environ['MYSQL_NBA_USER'], "--password=" + os.environ['MYSQL_NBA_PASSWORD'], dbname, tablename]

            p = subprocess.Popen(cmd, stdout=dumpfile)
            retcode = p.wait()

            if retcode > 0:
                print('Error:', dbname, 'backup error')

            else:
                self._backup_compress(dirname, bfile)

    def players_to_add(self):

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

        cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(sql)
        return cursor.fetchall()

    def select_dict(self, sql):
        '''
        Generic routine to get list of dictionaries from mysql table
        '''
        cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(sql)
        return cursor.fetchall()
