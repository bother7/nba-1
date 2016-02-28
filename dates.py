import datetime
import logging
import re

def date_list(d1, d2):
    '''
    Takes two datetime objects or datestrings and returns a list of datetime objects

    Usage:
        for d in s._date_list('10_09_2015', '10_04_2015'):
            print datetime.strftime(d, '%m_%d_%Y')
    '''

    # convert datestring into datetime object
    # strtodate knows the formats used by various sites
    if isinstance(d1, basestring):
        try:
            d1 = strtodate(d1)

        except:
            logging.error('{0} is not in %m_%d_%Y format'.format(d1))

    # convert datestring into datetime object
    # strtodate knows the formats used by various sites
    if isinstance(d2, basestring):
        try:
            d2 = strtodate(d2)

        except:
            logging.error('{0} is not in %m_%d_%Y format'.format(d1))

    season = d1-d2

    return [d1 - datetime.timedelta(days=x) for x in range(0, season.days+1)]

def format_type(d):
    '''
    Uses regular expressions to determine format of datestring
    '''

    fmt = None

    if re.match(r'\d{2}_\d{2}_\d{4}', d):
        fmt = site_format('fl')

    elif re.match(r'\d{4}-\d{2}-\d{2}', d):
        fmt = site_format('nba')

    elif re.match(r'\d{2}-\d{2}-\d{4}', d):
        fmt = site_format('std')

    return fmt

def site_format(site):
    '''
    Stores date formats used by different sites
    '''
    fmt = {
        'std': '%m-%d-%Y',
        'fl': '%m_%d_%Y',
        'nba': '%Y-%m-%d'
    }

    return fmt.get(site)

def strtodate(d):
    '''
    Converts date formats used by different sites
    '''
    return datetime.datetime.strptime(d, format_type(d))