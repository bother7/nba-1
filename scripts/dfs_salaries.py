'''
dfs_salaries.py
this shows how to parse the new NBA.com boxscores (data.nba.com)
should be integrated into the NBA library 
'''

import logging
import os
import sys
import time

from configparser import ConfigParser

from nba.scrapers.nbacom import NBAComScraper
from nba.db.nbacom import NBAComPg
from nba.db.queries import missing_games_meta

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

config = ConfigParser()
configfn = os.path.join(os.path.expanduser('~'), '.pgcred')
config.read(configfn)

s = NBAComScraper(cache_name='games-meta')
nbapg = NBAComPg(username=config['nbadb']['username'],
                        password=config['nbadb']['password'],
                        database=config['nbadb']['database'])

teams = []
url = 'http://data.nba.com/data/10s/prod/v1/{game_date}/{game_id}_boxscore.json'
headers = ['game_id', 'gamecode', 'game_date', 'team_code', ]
for item in nbapg.select_dict(missing_games_meta()):
    try:
        content = s.get_json(url.format(game_date=item['game_date'], game_id=item['game_id']))
        vteam_code = content['basicGameData']['vTeam']['triCode']
        vscore = int(content['basicGameData']['vTeam']['score'])
        vls = [int(l['score']) for l in content['basicGameData']['vTeam']['linescore']]
        hteam_code = content['basicGameData']['hTeam']['triCode']
        hscore = int(content['basicGameData']['hTeam']['score'])
        hls = [int(l['score']) for l in content['basicGameData']['hTeam']['linescore']]
        off = [o['firstNameLastName'] for o in content['basicGameData']['officials']['formatted']]
        gamecode = item['game_date'] + '/' + vteam_code + hteam_code
        if int(content['basicGameData']['period']['current']) > 4:
            is_ot = True
        else:
            is_ot = False

        v = {'game_id': item['game_id'],
             'game_date': item['game_date'], 'gamecode': gamecode,
             'team_code': vteam_code,
             'q1': vls[0], 'q2': vls[1], 'q3': vls[2], 'q4': vls[3], 's': vscore,
             'is_ot': is_ot,
             'ref1': off[0], 'ref2': off[1], 'ref3': off[2]
        }

        h = {'game_id': item['game_id'],
             'game_date': item['game_date'], 'gamecode': gamecode,
             'team_code': hteam_code,
             'q1': hls[0], 'q2': hls[1], 'q3': hls[2], 'q4': hls[3], 's': hscore,
             'is_ot': is_ot,
             'ref1': off[0], 'ref2': off[1], 'ref3': off[2]
        }

        if is_ot:
            if len(hls) == 5:
                h['ot1'] = hls[4]
                h['ot2'] = None
                h['ot3'] = None
                h['ot4'] = None
                v['ot1'] = vls[4]
                v['ot2'] = None
                v['ot3'] = None
                v['ot4'] = None
            elif len(hls) == 6:
                h['ot1'] = hls[4]
                h['ot2'] = hls[5]
                h['ot3'] = None
                h['ot4'] = None
                v['ot1'] = vls[4]
                v['ot2'] = vls[5]
                v['ot3'] = None
                v['ot4'] = None
            elif len(hls) == 7:
                h['ot1'] = hls[4]
                h['ot2'] = hls[5]
                h['ot3'] = hls[6]
                h['ot4'] = None
                v['ot1'] = vls[4]
                v['ot2'] = vls[5]
                v['ot3'] = vls[6]
                v['ot4'] = None
            elif len(hls) == 8:
                h['ot1'] = hls[4]
                h['ot2'] = hls[5]
                h['ot3'] = hls[6]
                h['ot4'] = hls[7]
                v['ot1'] = vls[4]
                v['ot2'] = vls[5]
                v['ot3'] = vls[6]
                v['ot4'] = vls[7]
        else:
            h['ot1'] = None
            h['ot2'] = None
            h['ot3'] = None
            h['ot4'] = None
            v['ot1'] = None
            v['ot2'] = None
            v['ot3'] = None
            v['ot4'] = None

        nbapg._insert_dict(v, 'games_meta')
        nbapg._insert_dict(h, 'games_meta')
        logging.info('finished {}'.format(gamecode))

    except (ValueError) as e:
        logging.exception('{} {}'.format(item, e))

    finally:
        time.sleep(1)
