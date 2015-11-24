'''
NBATeamNames.py
Converts various team name formats to others
Different sites use different names for the same NBA teams
'''

import logging

class NBATeamNames:
    '''
    Converts NBA team name formats to others

    Usage:
        n = NBATeamNames()

        n.long_to_short('Utah Jazz')
            'UTA'

        n.short_to_long('UTA')
            'Utah Jazz'
    '''

    def __init__(self):
        '''
        Sets long names, uses dictionary comprehension for short names
        '''

        logging.getLogger(__name__).addHandler(logging.NullHandler())

        self.long_names = {
            'Atlanta Hawks': 'ATL',
            'Boston Celtics': 'BOS',
            'Brooklyn Nets': 'BKN',
            'Charlotte Hornets': 'CHA',
            'Chicago Bulls': 'CHI',
            'Cleveland Cavaliers': 'CLE',
            'Dallas Mavericks': 'DAL',
            'Denver Nuggets': 'DEN',
            'Detroit Pistons': 'DET',
            'Golden State Warriors': 'GSW',
            'Houston Rockets': 'HOU',
            'Indiana Pacers': 'IND',
            'Los Angeles Clippers': 'LAC',
            'Los Angeles Lakers': 'LAL',
            'Memphis Grizzlies': 'MEM',
            'Miami Heat': 'MIA',
            'Milwaukee Bucks': 'MIL',
            'Minnesota Timberwolves': 'MIN',
            'New Orleans Pelicans': 'NOP',
            'New York Knicks': 'NYK',
            'Oklahoma City Thunder': 'OKC',
            'Orlando Magic': 'ORL',
            'Philadelphia 76ers': 'PHI',
            'Phoenix Suns': 'PHO',
            'Portland Trail Blazers': 'POR',
            'Sacramento Kings': 'SAC',
            'San Antonio Spurs': 'SAN',
            'Toronto Raptors': 'TOR',
            'Utah Jazz': 'UTA',
            'Washington Wizards': 'WAS'
        }

        self.nbacom_codes = {
            "1610612737": "ATL",
            "1610612738": "BOS",
            "1610612751": "BKN",
            "1610612766": "CHA",
            "1610612741": "CHI",
            "1610612739": "CLE",
            "1610612742": "DAL",
            "1610612743": "DEN",
            "1610612765": "DET",
            "1610612744": "GSW",
            "1610612745": "HOU",
            "1610612754": "IND",
            "1610612746": "LAC",
            "1610612747": "LAL",
            "1610612763": "MEM",
            "1610612748": "MIA",
            "1610612749": "MIL",
            "1610612750": "MIN",
            "1610612740": "NOP",
            "1610612752": "NYK",
            "1610612760": "OKC",
            "1610612753": "ORL",
            "1610612755": "PHI",
            "1610612756": "PHX",
            "1610612757": "POR",
            "1610612758": "SAC",
            "1610612759": "SAS",
            "1610612761": "TOR",
            "1610612762": "UTA",
            "1610612764": "WAS"
        }

        self.nbacom_names = {v:k for k,v in self.nbacom_codes.items()}
        self.short_names = {v:k for k,v in self.long_names.items()}

    def long_to_short(self, name):
        return self.long_names.get(name, None)

    def nbacom_code_to_short(self, code):
        return self.nbacom_codes.get(code, None)

    def nbacom_short_to_code(self, name):
        return self.nbacom_names.get(name, None)

    def short_to_long(self, name):
        return self.short_names.get(name, None)


if __name__ == '__main__':
    pass
