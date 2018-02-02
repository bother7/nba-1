# -*- coding: utf-8*-
import logging
from urlparse import urlparse

from bs4 import BeautifulSoup
from nba.seasons import in_what_season


class RotoworldNBAParser():
    '''
    '''

    def __init__(self):
        logging.getLogger(__name__).addHandler(logging.NullHandler())


    def _team_table(self, t, tc, as_of):
        '''
        Each team depth chart is in a table embedded in a td element
        There are 3 side-by-side team depth charts (3 tds in tr element)
        '''
        ps = []
        currpos = 'PG'
        for tr in t.find_all('tr'):
            p = {'team_code': tc, 'as_of': as_of, 'source': 'rotoworld'}
            p['season'] = in_what_season(as_of, fmt='season_year')
            position, rank = tr.find_all('td')
            if position.text and position.text != '':
                currpos = position.text
            p['source_position'] = currpos
            p['source_rank'] = rank.text.split('.')[0]
            if p['source_rank'] == 1:
                p['source_role'] = 'Starter'
            p['source_player_id'], p['pcode'] = tr.a.get('href').split('/')[-2:]
            p['source_player_name'] = ' '.join([pt.capitalize() for pt in p['pcode'].split('-')])
            p.pop('pcode', None)
            ps.append(p)
        return ps


    def depth_charts(self, content, as_of=None):
        '''
        Parses HTML of NBA depth charts (all teams)
        Args:
            content: HTML string

        Returns:
            dc: list of dict
        '''

        dc = []
        soup = BeautifulSoup(content, 'lxml')
        t = soup.find('table', {'id': 'cp1_tblDepthCharts'})
        for i in xrange(1, len(t.contents) - 1, 2):
            # should produce two lists of len 3
            teams = []
            tables = []
            for ch in t.contents[i].children:
                if ch.name == 'th':
                    a = ch.find('a')
                    parsed = urlparse(a.get('href'))
                    teams.append(parsed.path.split('/')[-2].upper())
            for ch in t.contents[i+1].children:
                if ch.name == 'td':
                    tables.append(ch.find('table'))
            # now loop through lists
            for tm, tbl in zip(teams, tables):
               dc += self._team_table(tbl, tm, as_of)
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
        soup = BeautifulSoup(content, 'lxml')
        for team, t in zip(teams, soup.find_all('table', {'class': 'basketball'})):
            for a in t.find_all('a'):
                try:
                    if 'Summary' in a['href']:
                        ps.append((team, a['href']))
                except:
                    logging.error('no href for {}'.format(a))
        return ps


if __name__ == "__main__":
    from nba.parsers.rotoworld import RotoworldNBAParser
    from nba.scrapers.scraper import BasketballScraper

    s = BasketballScraper(cache_name='rwtest')
    url = 'http://www.rotoworld.com/teams/depth-charts/nba.aspx'
    content = s.get(url)
    p = RotoworldNBAParser()
    print(p.depth_charts(content, '20170102'))

    #pass