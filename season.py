from collections import OrderedDict
from cachetools import cached, LRUCache
from nba.dates import *


cache = LRUCache(maxsize=100)


def in_what_season_year(d):
    '''
    Returns season year given a day

    Args:
        d (datetime.datetime)

    Returns:
        int
        
    '''
    y = d.year
    m = d.month

    if m >= 9:
        return y + 1
    else:
        return y


def in_what_season_code(d):
    '''
    Returns season code given a day

    Args:
        d (datetime.datetime)

    Returns:
        int

    '''
    y = d.year
    m = d.month

    if m >= 9:
        return season_year_to_season_code(y+1)
    else:
        return season_year_to_season_code(y)


def season_year_to_season_code(s):
    '''
    Converts 2014 to 2013-14, 2015 to 2014-15, etc.

    Args:
        s: int

    Returns:
        sy: str
    '''
    return '{}-{}'.format(s - 1, str(s)[-2:])


def season_code_to_season_year(sc):
    '''
    Converts season_code to season_year

    Args:
        sc (str): 2013-14 to 2014, 2014-15 to 2015, etc.

    Returns:
        int: 2014, 2015, etc.
        
    '''
    try:
        return int(sc[0:4]) + 1
    except:
        return None


def season(season_year=None, season_code=None):
    '''
    Returns dictionary of season

    Args:
        season_year (int): 2018, etc.
        season_code (str): 2017-18, etc.
        
    Returns:
        dict

    '''
    if season_year:
        return seasons().get(season_year_to_season_code(season_year))
    elif season_code:
        return seasons().get(season_code)
    else:
        raise ValueError('must pass season_year or season_code')


def season_dates(season_year=None, season_code=None, fmt='nba'):
    '''
    Creates list of datetime objects for entire season or in custom date range

    Args:
        season_year (int): 2018, etc.
        season_code (str): 2017-18, etc.
        fmt (str): format of game_dates, default is 2017-08-20
        
    Returns:
        list of datetime.datetime

    '''
    if season_year:
        return list(reversed(date_list(season_end(season_year), season_start(season_year))))
    elif season_code:
        return list(reversed(date_list(season_end(season_code), season_start(season_code))))
    else:
        raise ValueError('must pass season_year or season_code')


def season_gamedays(season_year=None, season_code=None, fmt='nba'):
    '''
    List of days with actual games during season (excludes all-star break, etc)

    TODO: implement this using game table
    
    Args:
        season_year (int): 2018, etc.
        season_code (str): 2017-18, etc.
        fmt (str): format of game_dates, default is 2017-08-20
        
    Returns:
        list of datetime.datetime

    '''
    pass


def season(season_year=None, season_code=None):
    '''
    Returns dictionary of season

    Args:
        season_year (int): 2018, etc.
        season_code (str): 2017-18, etc.

    Returns:
        dict
    
    '''

    if season_year:
        return seasons().get(season_year_to_season_code(season_year))
    elif season_code:
        return seasons().get(season_code)
    else:
        raise ValueError('must pass season_year or season_code')


@cached(cache)
def seasons():
    '''
    All nba seasons since 2000
    
    Args:
        None
        
    Returns:
        OrderedDict
        
    '''
    d = {
        "2017-18": {"start": datetime.datetime.strptime("10-17-2017", "%m-%d-%Y"), "end": datetime.datetime.strptime("04-11-2018", "%m-%d-%Y")},
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

    return OrderedDict(sorted(list(d.items()), reverse=True))


def season_end(season_year=None, season_code=None):
    '''
    Day season ends
    
    Args:
        season_year (int): 2018, etc.
        season_code (str): 2017-18, etc.
        
    Returns:
        datetime.datetime
    
    '''
    if season_year:
        s = seasons().get(season_year_to_season_code(season_year))
        return s.get('end')
    elif season_code:
        s = seasons().get(season_code)
        return s.get('end')
    else:
        raise ValueError('must pass season_year or season_code')


def season_start(season_year=None, season_code=None):
    '''
    Day season starts
    
    Args:
        season_year (int): 2018, etc.
        season_code (str): 2017-18, etc.
        
    Returns:
        datetime.datetime
    
    '''
    if season_year:
        s = seasons().get(season_year_to_season_code(season_year))
        return s.get('start')
    elif season_code:
        s = seasons().get(season_code)
        return s.get('start')
    else:
        raise ValueError('must pass season_year or season_code')


if __name__ == '__main__':
    pass
