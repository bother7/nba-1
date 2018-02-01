# -*- coding: utf-8*-
'''
ESPNNBAParser
'''

import json
import logging
import re

from bs4 import BeautifulSoup
from nba.teams import long_to_code


class ESPNNBAParser():


    def __init__(self):
        '''
        Creates ESPNNBAParser instance
        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())


    def carmelo(self, content):
        '''
        Parses JSON from CARMELO data

        Args:
            content:

        Returns:
            player: dict of relevant data
        '''
        # comps, playerstats, years
        # need to decide what to do with this data
        comps = content.get('comps')
        ps = content.get('player_stats')
        years = content.get('years')
        return (comps, ps, years)

    def fantasy_players(self, content):
        '''
        
        Args:
            content (str): HTML page 

        Returns:
            list: of dict
            
        '''
        players = []
        soup = BeautifulSoup(content, 'lxml')
        tbl = soup.find('table', {'id': 'playertable_0'})
        for tr in tbl.find_all('tr'):
            p = {'source': 'espn_fantasy'}
            if tr.attrs.get('id'):
                td = tr.find_all('td')[1]
                a = td.find('a')
                player_name = a.text
                pid = a['playerid']
                parts = td.text.split(',')
                team, pos = parts[1].split()[0:2]
                p['source_player_name'] = player_name
                p['source_player_id'] = pid
                p['source_player_position'] = pos
                players.append(p)
        return players

    def linescores(self, content, d):
        '''
        
        Args:
            content: 
            d: 

        Returns:

        '''
        ls = []
        patt = re.compile(r'scoreboardData\s+=\s+({"leagues":.*?});window\.espn\.scoreboardSettings',
                          re.MULTILINE | re.DOTALL)
        match = re.search(patt, content)
        if match:
            var = json.loads(match.group(1))
            if var:
                try:
                    for e in var['events']:
                        gid = e['id']
                        for c in e['competitions'][0]['competitors']:
                            tm = c['team']['displayName']
                            tmtype = c['homeAway']
                            s = c['score']
                            tmls = [item['value'] for item in c['linescores']]
                            ls.append({'espn_game_id': gid, 'game_date': d,
                                       'team_code': long_to_code(tm), 'team_name': tm, 'home_away': tmtype,
                                       'score': s, 'quarters': tmls})
                except:
                    pass

        return ls

    def players(self, content):
        '''

        Returns:

        '''
        players = {}
        pattern = re.compile('player/_/id/(\d+)/(\w+[^\s]*)', re.IGNORECASE)
        for c in content:
            soup = BeautifulSoup(c, 'lxml')
            links = soup.findAll('a', href=pattern)
            for link in links:
                match = re.search(pattern, link['href'])
                if match:
                    players[match.group(1)] = match.group(2)
        return players


    def projections(self, content):
        '''

        Args:
            content: list of HTML pages

        Returns:
            list of players
        '''
        players = []
        urlp = re.compile(r'plyr\d+')
        headers = ['rank', 'player_id', 'player_name',
                   'fgp', 'ftp', 'tpm', 'reb',
                   'ast', 'stl', 'blk', 'pts']
        for c in content:
            soup = BeautifulSoup(c, 'lxml')
            for tr in soup.find_all('tr', {'id': urlp}):
                vals = []
                tds = tr.find_all('td')
                vals.append(tds[0].text)
                a= tds[1].find('a')
                vals.append(a['playerid'])
                vals.append(a.text)
                for td in tds[2:]:
                    vals.append(td.text)
                players.append(dict(zip(headers, vals)))
        return players


if __name__ == "__main__":
    pass