# -*- coding: utf-8*-
'''
'''
import logging
import re

from bs4 import BeautifulSoup as BS


class RealgmNBAParser():
    '''
    '''

    def __init__(self):
        logging.getLogger(__name__).addHandler(logging.NullHandler())


    def depth_charts(self, content):
        '''
        Parses HTML of NBA depth charts (all teams)
        Args:
            content: HTML string

        Returns:
            dc: list of dict
        '''
        dc = []
        teams = ['ATL', 'BOS', 'BKN', 'CHA', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW', 'HOU', 'IND', 'LAC', 'LAL',
                 'MEM', 'MIA', 'MIL', 'MIN', 'NOP', 'NYK', 'OKC', 'ORL', 'PHI', 'PHO', 'POR', 'SAC', 'SAS', 'TOR',
                 'UTA', 'WAS']

        soup = BS(content, 'lxml')
        for team, t in zip(teams, soup.find_all('table', {'class': 'basketball'})):
            p = {'team': team}
            tr = t.find('tr', {'class': 'depth_starters'})
            for td in tr.find_all('td'):
                a = td.find('a')
                if a:
                    p[td['data-th'].lower()] = a.text
                else:
                    p[td['data-th'].lower()] = td.text
            dc.append(p)

            p = {'team': team}
            tr = t.find('tr', {'class': 'depth_rotation'})
            for td in tr.find_all('td'):
                a = td.find('a')
                if a:
                    p[td['data-th'].lower()] = a.text
                else:
                    p[td['data-th'].lower()] = td.text
            dc.append(p)

        return dc


if __name__ == "__main__":
    pass