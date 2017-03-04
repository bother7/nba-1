# -*- coding: utf-8*-
'''
ESPNNBAParser
'''

import logging
import re

from bs4 import BeautifulSoup


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