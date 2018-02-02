# -*- coding: utf-8*-
'''
'''
import logging

from bs4 import BeautifulSoup as BS


class RealgmNBAParser():
    '''
    '''

    def __init__(self):
        logging.getLogger(__name__).addHandler(logging.NullHandler())


    def depth_charts(self, content, as_of=None):
        '''
        Parses HTML of NBA depth charts (all teams)
        Args:
            content: HTML string

        Returns:
            dc: list of dict
        '''
        dc = []
        teams = ['ATL', 'BOS', 'BKN', 'CHA', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW', 'HOU',
                 'IND', 'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 'NOP', 'NYK', 'OKC', 'ORL',
                 'PHI', 'PHO', 'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS']
        soup = BS(content, 'lxml')
        for team, t in zip(teams, soup.find_all('table', {'class': 'basketball'})):
            tb = t.find('tbody')
            for role, tr in zip(['Starter', 'Rotation'], tb.find_all('tr')[0:2]):
                for td in tr.find_all('td'):
                    p = {'source': 'realgm', 'team_code': team, 'as_of': as_of, 'source_role': role}
                    try:
                        a = td.find('a')
                        parts = a['href'].split('/')
                        p['source_player_name'] = parts[-3].replace('-', ' ')
                        p['source_player_id'] = parts[-1]
                        p['source_position'] = td['data-th'].upper()
                        dc.append(p)
                    except:
                        pass
                    finally:
                        if p.get('source_player_name') and p.get('source_player_id'):
                            dc.append(p)
        return dc


    def players(self, content):
        '''
        List of realgm players with player_ids
        Args:
            content: 

        Returns:
            players: list of dict
        '''
        ps = []
        teams = ['ATL', 'BOS', 'BKN', 'CHA', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW', 'HOU', 'IND', 'LAC', 'LAL', 'MEM', 'MIA',
         'MIL', 'MIN', 'NOP', 'NYK', 'OKC', 'ORL', 'PHI', 'PHO', 'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS']
        soup = BS(content, 'lxml')
        for team, t in zip(teams, soup.find_all('table', {'class': 'basketball'})):
            for a in t.find_all('a'):
                try:
                    if 'Summary' in a['href']:
                        ps.append((team, a['href']))
                except:
                    logging.error('no href for {}'.format(a))
        return ps


if __name__ == "__main__":
    pass