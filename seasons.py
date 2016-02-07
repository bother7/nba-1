from collections import OrderedDict
import datetime
import logging

from EWTFantasyTools import EWTFantasyTools

class NBASeasons(EWTFantasyTools):
    '''
    Finds NBA season start and end dates

    Usage:
        nbas = NBASeasons()
        current = nbas.season ('2015-16') # current is dict with start, end keys
        seas = nbas.in_what_season('2014-10-31') # seas is dict with start, end keys
        end = nbas.season_end('2015-16') # end is a datetime object representing last day of the season
        
    '''

    def __init__(self):

        EWTFantasyTools.__init__(self)
        logging.getLogger(__name__).addHandler(logging.NullHandler())

        # see https://docs.python.org/2/library/collections.html#collections.OrderedDict
        d = {
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

        self._seasons = OrderedDict(sorted(d.items(), reverse=True))

    def in_what_season(self, day):
        
        if isinstance(day, basestring):
            day = datetime.datetime.strptime(day, '%Y-%m-%d')
        
        for season in self._seasons:
            start = self.season_start(season)
            end = self.season_end(season)
            
            if (day >= start) & (day <= end):
                return season

        return None

    def season(self, key):
        '''
        Returns dictionary having keys start and end
        '''
        return self._seasons.get(key)

    def season_dates(self, season, start_date=None, end_date=None, date_format=None):
        '''
        Returns list of datetime objects for entire season or in custom date range
        '''

        # defaults are beginning and end of the season
        if not start_date:
            start_date = self.season_start(season)

        if not end_date:
            end_date = self.season_end(season)

        return self.date_list(end_date, start_date, date_format)

    def season_start(self, key):
        '''
        Returns value for start key
        '''
        s = self._seasons.get(key)
        return s.get('start')

    def season_end(self, key):
        '''
        Returns value for end key
        '''
        s = self._seasons.get(key)
        return s.get('end')
        
    def seasons(self, fn=None):
        '''
        Returns OrderedDict of all seasons
        '''
        return self._seasons
        
if __name__ == '__main__':
    pass
