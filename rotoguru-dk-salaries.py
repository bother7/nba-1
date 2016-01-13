'''
rotoguru-dk-salaries.py
TODO: this is kind of whacked out right now
need to walk through call stack during lunch, figure out where it is going awry

'''
try:
    import cPickle as pickle

except:
    import pickle

import logging
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
        'Jones III, Perry': 'Jones, Perry',
        'Kilpatrick, Sean': '',
        'Lucas, John': '',
        'Matthews, Wes': 'Matthews, Wesley',
        'McCollum, C.J.': 'McCollum, CJ',
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
    
    logging.basicConfig(level=logging.ERROR)
    p = RotoGuruNBAParser()
    db = NBAPostgres()
    wanted = ['salary', 'site', 'player_name', 'game_date', 'pos']
    salaries = []
    unmatched = {}
    players = {}

    frame = pd.read_csv('players.csv')
    for player in frame.T.to_dict().values():
        players[player.get('display_last_comma_first')] = player.get('person_id')

    with open('/home/sansbacon/nba/data/2014-15_nba_rg_dk.pkl', 'rb') as infile:
        rg = pickle.load(infile) 
        for key in sorted(rg.keys()):
            daypage = rg.get(key)

            for sal in p.salaries(daypage, 'dk'):
                '''
                to_keep = {k:v for k,v in sal.iteritems() if k in wanted}

                pos = to_keep.get('pos', None)

                if pos:
                    to_keep['site_position'] = to_keep['pos']
                    to_keep.pop('pos', None)

                # need to match up rotoguru names with nbacom_player_id
                pid = players.get(to_keep['player_name'], None)

                # if no match, try conversion dictionary
                if not pid:
                    nba_name = rg_to_nbadotcom(to_keep['player_name'])
                    pid = players.get(nba_name, None)

                # if still no match, add to unmatched and don't add to database
                if not pid:
                    logging.warning('no player_id for {0}'.format(to_keep['player_name']))
                    unmatched[to_keep['player_name']] = 1
                    
                else:
                    to_keep['nbacom_player_id'] = int(pid)

                if not to_keep['salary']:
                    logging.warning('no salary: {0}'.format(to_keep))

                else:
                    to_keep['site_player_name'] = to_keep['player_name']
                    to_keep.pop('player_name', None)
                    salaries.append(to_keep)
                '''
                
    if save_unmatched:
        with open('unmatched.txt', 'w') as outfile:
            outfile.write(pprint.pformat(sorted(unmatched.keys())))

    if create_df:
        frame = pd.DataFrame(salaries)
        frame.game_date = pd.to_datetime(frame.game_date)
        frame.salary = pd.to_numeric(frame.salary)
        return frame

    else:
        pprint.pprint(salaries)
        #db.insert_dicts(salaries, 'salaries')
        
if __name__ == '__main__':
    frame = run(create_df=False)
