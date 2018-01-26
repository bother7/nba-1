import logging
import re

from bs4 import BeautifulSoup


class BBRefParser():
    '''
    '''

    def __init__(self,**kwargs):
        '''

        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())

    def players(self, content):
        '''
        Parses page of players with same last initial (A, B, C, etc.) 

        Args:
            content: HTML string

        Returns:
            list of dict
        '''
        results = []
        soup = BeautifulSoup(content, 'lxml')
        for row in soup.find('table', {'id': 'players'}).find('tbody').find_all('tr'):
            player = dict([(td['data-stat'], td.text) for td in row.find_all('td')])
            player['source_player_id'] = row.find('th').get('data-append-csv')
            player['source_player_name'] = row.find('th').find('a').text
            th = row.find('th')
            if th.find('strong'):
                player['active'] = True
            else:
                player['active'] = False
            if player.get('pos'):
                player['source_player_position'] = player['pos']
                player.pop('pos', None)
            results.append(player)
        return results

    def player_page(self, content, pid):
        '''
        Parses player page 

        Args:
            content: HTML string

        Returns:
            dict: source, source_player_id, source_player_name, 
                  source_player_position, source_player_dob, 
                  source_player_team_code, source_player_team_name

        '''
        player = {'source': 'bref', 'source_player_id': pid}
        soup = BeautifulSoup(content, 'lxml')

        #source_player_name
        h1 = soup.find('h1', {'itemprop': 'name'})
        if h1:
            player['source_player_name'] = h1.text

        #source_player_position
        positions = ['Shooting Guard', 'Power Forward and Small Forward', 'Small Forward', 'Center', 'Point Guard',
                     'Center and Power Forward', 'Power Forward and Center', 'Shooting Guard and Small Forward',
                     'Power Forward', 'Small Forward and Shooting Guard', 'Point Guard and Shooting Guard',
                     'Guard', 'Forward']
        div = soup.find('div', {'itemtype': 'https://schema.org/Person'})
        for p in div.find_all('p'):
            if 'Position:' in p.text:
                for line in [l.strip() for l in p.text.split('\n')]:
                    if line in positions:
                        player['source_player_position'] = line
            elif 'Team:' in p.text:
                a = p.find('a')
                if a:
                    player['source_player_team_code'] = a['href'].split('/')[2]
                    player['source_player_team_name'] = a.text

        # source_player_dob
        bd = soup.find('span', {'id': 'necro-birth'})
        if bd:
            player['source_player_dob'] = bd.attrs.get('data-birth')

        return player


if __name__ == "__main__":
    pass