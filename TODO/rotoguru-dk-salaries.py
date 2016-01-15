'''
rotoguru-dk-salaries.py
1/15/2015 - can delete after test NBAComAgent.rg_salaries

'''
try:
    import cPickle as pickle

except:
    import pickle

from collections import defaultdict
import csv
import logging
import os
import pprint

import pandas as pd

from NBAPostgres import NBAPostgres 
from RotoGuruNBAParser import RotoGuruNBAParser

def rg_to_nbadotcom(name):
    return {
        'Amundson, Louis': 'Amundson, Lou',
        'Barea, Jose': 'Barea, Jose Juan',
        'Bhullar, Sim': '',
        'Brown, Jabari': '',
        'Datome, Luigi': '',
        'Drew II, Larry': '',
        'Hairston, P.J.': 'Hairston, PJ',
        'Hayes, Chuck': 'Hayes, Charles',
        'Hickson, J.J.': 'Hickson, JJ',
        'Hilario, Nene': 'Nene',
        'Hunter, R.J.': 'Hunter, RJ',
        'Jones III, Perry': 'Jones, Perry',
        'Kilpatrick, Sean': '',
        'Lucas, John': '',
        'Matthews, Wes': 'Matthews, Wesley',
        'McCollum, C.J.': 'McCollum, CJ',
        'McConnell, T.J.': 'McConnell, TJ',
        'McDaniels, K.J.': 'McDaniels, KJ',
        'Miles, C.J.': 'Miles, CJ',
        'Murry, Toure': '',
        'Redick, J.J.': 'Redick, JJ',
        'Robinson III, Glenn': 'Robinson, Glenn',
        'Smith, Ishmael': 'Smith, Ish',
        'Stoudemire, Amare': '''Stoudemire, Amar'e''',
        'Taylor, Jeffery': 'Taylor, Jeff',
        'Tucker, P.J.': 'Tucker, PJ',
        'Warren, T.J.': 'Warren, TJ',
        'Watson, C.J.': 'Watson, CJ',
        'Wear, David': '',
        'Wilcox, C.J.': 'Wilcox, CJ',
        'Williams, Louis': 'Williams, Lou',
        'Williams, Maurice': 'Williams, Mo'
    }.get(name, None)

def run(save_unmatched = False, create_df = False):
    '''
    Takes rotoguru pages saved in pickle file and
    creates pandas dataframe or inserts into postgres table
    '''
    
    logging.basicConfig(level=logging.WARNING)
    p = RotoGuruNBAParser()
    db = NBAPostgres()

    salaries = []
    players = {}
    unmatched = defaultdict(int)

    # load existing list of players (could also be sql query)
    csv_fname = os.path.join(os.path.dirname(__file__), 'players.csv')   
    with open(csv_fname, 'rb') as infile:
        for line in infile:
            line = line.strip()

            if line:
                pname, pid = line.split(';')
                players[pname] = pid

    # main loop
    with open('/home/sansbacon/2013-14_nba_rg_fd.pkl', 'rb') as infile:
        rg = pickle.load(infile) 
        for key in sorted(rg.keys()):
            daypage = rg.get(key)

            for sal in p.salaries(daypage, 'fd'):

                # players is key of nbacom_name and value of nbacom_id
                # need to match up rotoguru names with these
                pid = players.get(sal.get('site_player_name'), None)

                # if no match, try conversion dictionary
                if not pid:
                    nba_name = rg_to_nbadotcom(sal.get('site_player_name', None))
                    pid = players.get(nba_name, None)

                # if still no match, warn and don't add to database
                if not pid:
                    logging.warning('no player_id for {0}'.format(sal.get('site_player_name')))
                    unmatched[sal.get('site_player_name')] += 1
                    continue

                else:
                    sal['nbacom_player_id'] = pid

                # if no salary, warn and don't add to database    
                if not sal.get('salary', None):
                    logging.warning('no salary for {0}'.format(sal.get('site_player_name')))
                    continue

                salaries.append(sal)               

    db.insert_dicts(salaries, 'salaries')
        
if __name__ == '__main__':
    run()
