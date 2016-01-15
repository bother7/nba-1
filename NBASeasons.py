import datetime
import logging
import json

import memcache
import MySQLdb
import MySQLdb.cursors


class NBASeasons():
    '''
    Used to return data about seasons
    TODO: this doesn't do much besides return an entire dictionary
    
    '''

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

        if 'seasons' in kwargs:
            self._seasons = kwargs['seasons']
        else:
            self._seasons = {
            "2015-16": {"start": datetime.datetime.strptime("10-27-2015", "%m-%d-%Y"), "end": datetime.datetime.strptime("04-13-2016", "%m-%d-%Y")},
            "2014-15": {"start": datetime.datetime.strptime("10-28-2014", "%m-%d-%Y"), "end": datetime.datetime.strptime("04-15-2015", "%m-%d-%Y")},
            "2013-14": {"start": datetime.datetime.strptime("10-29-2013", "%m-%d-%Y"), "end": datetime.datetime.strptime("04-16-2014", "%m-%d-%Y")},
            "2012-13": {"start": datetime.datetime.strptime("10-30-2012", "%m-%d-%Y"), "end": datetime.datetime.strptime("04-17-2013", "%m-%d-%Y")},
            "2011-12": {"start": datetime.datetime.strptime("11-25-2011", "%m-%d-%Y"), "end": datetime.datetime.strptime("04-26-2012", "%m-%d-%Y")},
            "2010-11": {"start": datetime.datetime.strptime("10-26-2010", "%m-%d-%Y"), "end": datetime.datetime.strptime("04-13-2011", "%m-%d-%Y")},
            "2009-10": {"start": datetime.datetime.strptime("10-27-2009", "%m-%d-%Y"), "end": datetime.datetime.strptime("04-14-2010", "%m-%d-%Y")},
            "2008-09": {"start": datetime.datetime.strptime("10-28-2008", "%m-%d-%Y"), "end": datetime.datetime.strptime("04-15-2009", "%m-%d-%Y")},
            "2007-08": {"start": datetime.datetime.strptime("10-30-2007", "%m-%d-%Y"), "end": datetime.datetime.strptime("04-16-2008", "%m-%d-%Y")},
            "2006-07": {"start": datetime.datetime.strptime("10-31-2006", "%m-%d-%Y"), "end": datetime.datetime.strptime("04-18-2007", "%m-%d-%Y")},
            "2005-06": {"start": datetime.datetime.strptime("11-01-2005", "%m-%d-%Y"), "end": datetime.datetime.strptime("04-19-2006", "%m-%d-%Y")},
            "2004-05": {"start": datetime.datetime.strptime("11-02-2004", "%m-%d-%Y"), "end": datetime.datetime.strptime("04-20-2005", "%m-%d-%Y")},
            "2003-04": {"start": datetime.datetime.strptime("10-28-2003", "%m-%d-%Y"), "end": datetime.datetime.strptime("04-14-2004", "%m-%d-%Y")},
            "2002-03": {"start": datetime.datetime.strptime("10-29-2002", "%m-%d-%Y"), "end": datetime.datetime.strptime("04-16-2003", "%m-%d-%Y")},
            "2001-02": {"start": datetime.datetime.strptime("10-30-2001", "%m-%d-%Y"), "end": datetime.datetime.strptime("04-17-2002", "%m-%d-%Y")},
            "2000-01": {"start": datetime.datetime.strptime("10-31-2000", "%m-%d-%Y"), "end": datetime.datetime.strptime("04-18-2001", "%m-%d-%Y")},
            "1999-00": {"start": datetime.datetime.strptime("11-02-1999", "%m-%d-%Y"), "end": datetime.datetime.strptime("04-19-2000", "%m-%d-%Y")},
            "1998-99": {"start": datetime.datetime.strptime("02-05-1999", "%m-%d-%Y"), "end": datetime.datetime.strptime("05-05-1999", "%m-%d-%Y")},
            "1997-98": {"start": datetime.datetime.strptime("10-31-1997", "%m-%d-%Y"), "end": datetime.datetime.strptime("04-19-1998", "%m-%d-%Y")},
            "1996-97": {"start": datetime.datetime.strptime("11-01-1996", "%m-%d-%Y"), "end": datetime.datetime.strptime("04-20-1997", "%m-%d-%Y")}
        }
          
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

    def in_what_season(self, day):
        season = None
        # TODO: takes a date, returns the season in YYYY-YY format
        return season

    def season(self, key):
        '''
        Should return a dictionary having keys start and end
        '''
        return self._seasons.get(key, None)
        
    def seasons(self, fn=None):
        '''
        Probably won't need the other stuff, but have as a skeleton
        '''

        # try dict
        seasons = self._seasons
        
        # try cache
        if not seasons:
            try:
                seasons = self._cache_get()

            except:
                pass
            
        # try file if can't get from cache
        if not seasons:
            if os.path.isfile(fn):
                try:
                    with open(fn, 'r') as infile:
                        seasons = json.load(infile)

                        if seasons:
                            self._cache_put(seasons)

                except:
                    pass
                
        # if no file, try database
        if not seasons:
            tbl = 'seasons'
            
            try:
                db = self._db_setup()
                c = db.cursor()
                c.execute('select * from {0}'.format(tbl))
                seasons = c.fetchall()

                if seasons:
                    self._cache_put(seasons)

                db.close()
                
            except:
                pass
            
        return seasons

if __name__ == '__main__':
    pass
