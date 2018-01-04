game_id integer NOT NULL,
season smallint,
game_date date NOT NULL,
gamecode character varying(30),
visitor_team_id integer,
visitor_team_code character varying(3),
home_team_id integer,
home_team_code character varying(3),
game_type character varying(10)

import pandas as pd
import requests
from nba.dates import subtract_datestr
from nba.utility import getdb

url = 'http://data.nba.com/data/10s/v2015/json/mobile_teams/nba/2017/league/00_full_schedule.json'
r = requests.get(url)
data = r.json()
nbadb = getdb()

games = []
for item in data['lscd']:
    mscd = item['mscd']
    for game in mscd['g']:
        g = {'season': 2018}
        g['game_id'] = game['gid']
        g['gamecode'] = game['gcode']
        g['game_date'] = game['gdte']
        if 'AS1' in game['gcode'] or 'WLDUSA' in game['gcode']:
            continue   
        elif (subtract_datestr(g['game_date'], '2017-10-17') >= 0):
            g['game_type'] = 'regular'
        else:
            continue
        v = game['v']
        g['visitor_team_id'] = v['tid']
        g['visitor_team_code'] = v['ta']
        h = game['h']
        g['home_team_id'] = h['tid']
        g['home_team_code'] = h['ta']
        nbadb._insert_dict(g, 'games')
        games.append(g)
        
