import csv
import logging
import json
import memcache
import os

import MySQLdb
import MySQLdb.cursors

class NBAGames():

    def __init__(self,**kwargs):

        logging.getLogger(__name__).addHandler(logging.NullHandler())

        if 'expire_time' in kwargs:
            self.expire_time = kwargs['expire_time']
        else:
            self.expire_time = 3600

        if 'keyprefix' in kwargs:
            self.keyprefix = kwargs['keyprefix']
        else:
            self.keyprefix = 'nbadotcom-games'

        if 'mc' in kwargs:
            self.mc = mc
        else:
            self.mc = memcache.Client(['127.0.0.1:11211'], debug=0)

        if 'use_cache' in kwargs:
          self.use_cache = kwargs['use_cache']
        else:
          self.use_cache = True

        # http://stackoverflow.com/questions/8134444/python-constructor-of-derived-class
        self.__dict__.update(kwargs)

    def _cache_get(self, key = 'nbadotcom_game_list'):

        try:
            val = self.mc.get(key)
            logging.debug('got %s from cache' % key)

        except:
            val = None
            
        return val 

    def _cache_put(self, content, key='nbadotcom_game_list'):

        try:
            status = self.mc.set(key, content, time=self.expire_time)
            logging.debug('saved %s to cache' % key)

        except:
            status = None

        return status

    def _db_setup(self):
        host = os.environ['MYSQL_NBA_HOST']
        user = os.environ['MYSQL_NBA_USER']
        password = os.environ['MYSQL_NBA_PASSWORD']
        database = os.environ['MYSQL_NBA_DATABASE']

        try:
            db = MySQLdb.connect(host=host, user=user, passwd=password, db=database, cursorclass=MySQLdb.cursors.DictCursor)

        except:
            db = None

        return db
        
    def games(self, fn='nbadotcom_games.json'):

        # try cache
        try:
            games = self._cache_get()

        except:
            pass
            
        # try file if can't get from cache
        if not games:
            if os.path.isfile(fn):
                try:
                    with open(fn, 'r') as infile:
                        games = json.load(infile)

                        if games:
                            self._cache_put(games)

                except:
                    pass
                
        # if no file, try database
        if not games:

            try:
                db = self._db_setup()
                c = db.cursor()
                c.execute('select * from games')
                games = c.fetchall()

                if games:
                    self._cache_put(games)

                db.close()
                
            except:
                pass
            
        return games

if __name__ == '__main__':
    pass
