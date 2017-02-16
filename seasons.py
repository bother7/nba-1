from collections import OrderedDict

from nba.dates import *


# see https://docs.python.org/2/library/collections.html#collections.OrderedDict
d = {
    "2016-17": {"start": datetime.datetime.strptime("10-25-2016", "%m-%d-%Y"), "end": datetime.datetime.strptime("04-12-2017", "%m-%d-%Y")},
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

_seasons = OrderedDict(sorted(list(d.items()), reverse=True))

def in_what_season(day, fmt=None):

    if isinstance(day, str):
        day = datetime.datetime.strptime(day, format_type(day))

    for season in _seasons:
        start = season_start(season)
        end = season_end(season)

        if (day >= start) & (day <= end):
            if fmt:
                return int(season.split('-')[0]) + 1
            else:
                return season

    return None

def season(key):
    '''
    Returns dictionary having keys start and end
    '''
    return _seasons.get(key)

def season_dates(season, start_date=None, end_date=None):
    '''
    Returns list of datetime objects for entire season or in custom date range
    '''

    # defaults are beginning and end of the season
    if not start_date:
        start_date = season_start(season)

    if not end_date:
        end_date = season_end(season)

    return list(reversed(date_list(end_date, start_date)))

def season_start(key):
    '''
    Returns value for start key
    '''
    s = _seasons.get(key)
    return s.get('start')

def season_end(key):
    '''
    Returns value for end key
    '''
    s = _seasons.get(key)
    return s.get('end')

def seasons(fn=None):
    '''
    Returns OrderedDict of all seasons
    '''
    return _seasons
        
if __name__ == '__main__':
    pass
