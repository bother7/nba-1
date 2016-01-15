import csv
import logging
import numbers
import pprint
import re
import xlrd

from NBAGames import NBAGames
from NBATeamNames import NBATeamNames


class NBAStufferParser():

    '''
    Parses xls file of NBA game info from nbastuffer.com into game dictionaries

    Example:
        p = NBAStufferParser()
        fn='stuffer.xlsx'
        wb = xlrd.open_workbook(fn)
        sheet = wb.sheet_by_index(0)
        if sheet:
            games = p.xlsx_game_pairs(sheet, p.xlsx_headers(sheet))
    
    '''

    def __init__(self, **kwargs):
        '''
        Args:
            **kwargs: 
        '''

        logging.getLogger(__name__).addHandler(logging.NullHandler())

        if 'names' in kwargs:
            self.names = kwargs['names']
        else:
            self.names = NBATeamNames()
        
        if 'nbadotcom_games' in kwargs:
            self.nbadotcom_games = kwargs['nbadotcom_games']
        else:
            self.nbadotcom_games = {}
            logging.error('no nbadotcom_games')

        if 'omit' in kwargs:
            self.omit = kwargs['omit']
        else:
            self.omit = ['teams', 'f', 'moneyline', 'movements', 'opening_odds']

    def _fix_headers(self, headers_):
        '''
        Standardize with field names used by nba.com
        '''

        fixed = []

        convert = {
            'date': 'gamedate',
            'team_abbreviation': 'team_code',
            'fg': 'fgm',
            'ft': 'ftm',
            'dr': 'dreb',
            'or': 'oreb',
            'tot': 'reb',
            'a': 'ast',
            'st': 'stl',
            'bl': 'blk',
            'to': 'tov',
            '3p': 'fg3m',
            '3pa': 'fg3a',
            'spread': 'opening_spread',
            'total': 'opening_total'
        }

        for header in headers_:
            converted = convert.get(header, None)

            if converted:
                fixed.append(converted)

            else:
                fixed.append(header)

        return fixed

    def _fix_new_orleans(self, gamecode, season):
        '''
        Inconsistent naming of New orleans pelicans / hornets / oklahoma city (katrina year)
        This produces the correct 3-letter code to match up to nba.com gamecodes
        '''

        if season in ['2007', '2008', '2009', '2010', '2011', '2012']:
            gamecode = gamecode.replace('NOP', 'NOH')

        elif season in ['2005', '2006']:
            gamecode = gamecode.replace('NOP', 'NOK')

        return gamecode

    def _fix_starters(self, *args):
        '''
        Strange unicode characters in some of the player (starter) fields
        '''
        fixed = []
        
        for team in args:
            for k in team:
                if 'starter' in k:
                    team[k] = team[k].replace('\xc2\xa0', '')

            fixed.append(team)
            
        return fixed
        
    def _gameid(self, gamecode, dataset):
        '''
        Takes gamecode in format 20151027/CLECHI
        Returns game_id used by nba.com
        '''
        game = self.nbadotcom_games.get(gamecode)
        gameid = None

        if game:
            gameid = game.get('game_id', None)
            logging.debug('_gameid returns {0}'.format(gameid))

        else:
            # right now, don't have playoffs in games database, no need to print all of those errors
            if 'Regular' in dataset:
                logging.error('_gameid: could not find id for gamecode {0}'.format(gamecode))
    
            else:
                logging.debug('_gameid: could not find id for playoff gamecode {0}'.format(gamecode))
            
        return gameid

    def _gamecode(self, away, home):
        '''
        Game_pair is a list with two elements: first is dictionary of away team, second is dictionary of home team
        Returns gamecode in format 20141013/CHIBOS
        '''

        gamecode = None
        gamedate = away.get('gamedate', None)
        
        away_team = away.get('team_code', None)
        home_team = home.get('team_code', None)

        if gamedate and away_team and home_team:
            match = re.search(r'(\d+)\/(\d+)\/(\d+)', gamedate)
            
            if match:
                if len(match.group(3)) > 2:
                    gamecode = '{0}{1}{2}/{3}{4}'.format(match.group(3), match.group(1), match.group(2), away_team, home_team)
                    logging.debug('gamecode: {0}'.format(gamecode))
                else:
                    gamecode = '20{0}{1}{2}/{3}{4}'.format(match.group(3), match.group(1), match.group(2), away_team, home_team)
                    logging.debug('gamecode: {0}'.format(gamecode))

            else:
                gamecode = '{0}/{1}{2}'.format(gamedate, away_team, home_team)

        # new orleans pelicans / hornets / oklahoma city (katrina year) fix
        if gamecode and 'NOP' in gamecode:
            season = away.get('dataset', 'XXXX')[0:4]
            gamecode = self._fix_new_orleans(gamecode, season)

        logging.debug('_gamecode returns {0}'.format(gamecode))
        return gamecode

    def _get_closing(self, team1, team2, rowidx):
        '''
        Takes 2 team dictionaries, extracts cell with closing odds / closing (could be line or spread) or sets to None
        Various formats:
            Sometimes total like 198
            Sometimes + odds like 7
            Sometimes - odds like -7
            Sometimes a hybrid like -5.5 -05
            Sometimes includes PK (which is Pick'Em, 0 spread)
            Sometimes looks like -1.5-05
        '''
        
        team1_odds = team1.get('closing_odds', None)
        team2_odds = team2.get('closing_odds', None)
        
        # odds are stored under 'closing_odds' and 'closing' depending on the year
        if team1_odds == None or team1_odds == '':
            team1_odds = team1.get('closing', None)

            # if can't get closing, rely on opening
            if team1_odds == None or team1_odds == '':
                team1_odds = team1.get('spread', None)
                team2_odds = team1.get('total', None)
                logging.error('have to rely on opening odds: {0}, {1}: {2}'.format(team2.get('gamedate', 'Gamedate N/A'), team1.get('teams', 'Team N/A'), team2.get('teams', 'Team N/A')))

        # odds are stored under 'closing_odds' and 'closing' depending on the year
        if team2_odds == None or team1_odds == '':
            team2_odds = team2.get('closing', None)

            if team2_odds == None or team1_odds == '':
                team2_odds = team2.get('total', None)
                team1_odds = team1.get('spread', None)
                logging.error('have to rely on opening odds: {0}, {1}: {2}'.format(team2.get('gamedate', 'Gamedate N/A'), team1.get('teams', 'Team N/A'), team2.get('teams', 'Team N/A')))

        # if can't obtain anything, then skip further processing on odds
        if team1_odds == None or team1_odds == '':
            logging.error('error _get_closing: line %d | team1_odds: %s  team2_odds %s' % (rowidx, team1_odds, team2_odds))

        elif team2_odds == None or team1_odds == '':
            logging.error('error _get_closing: line %d | team1_odds: %s  team2_odds %s' % (rowidx, team1_odds, team2_odds))

        else:
            '''
            Takes 2 team dictionaries, extracts cell with closing odds / closing (could be line or spread) or sets to None
            Various formats:
                Sometimes a hybrid like -5.5 -05
                Sometimes includes PK (which is Pick'Em, 0 spread)
                Sometimes looks like -1.5-05
            '''

            # remove PK and set to zero
            if 'PK' in team1_odds:
                team1_odds = 0

            # otherwise strip out multiple odds if present
            else:
                match = re.search(r'([-]?\d+)\s?.*?', team1_odds)

                if match:
                    team1_odds = match.group(1)

            # remove PK and set to zero
            if 'PK' in team2_odds:
                team2_odds = 0

            # otherwise strip out multiple odds if present
            else:
                match = re.search(r'([-]?\d+)\s?.*?', team2_odds)

                if match:
                    team2_odds = match.group(1)

        logging.debug('team odds: {0}, {1}: {2}, {3}'.format(team1.get('teams', 'Team N/A'), team2.get('teams', 'Team N/A'), team1_odds, team2_odds))
               
        return team1_odds, team2_odds

    def _implied_total(self, game_total, spread):
        '''
        Takes game total and spread and returns implied total based on those values
        '''

        try:
            return (game_total/float(2)) - (spread/float(2))

        except TypeError, e:
            logging.error('implied total error: {0}'.format(e.message))
            return None
                
    def _is_total_or_spread(self, val1, val2):
        '''
        Tests if it is a game total or a point spread; former is always larger
        '''

        if (isinstance(val1, numbers.Number) and isinstance(val2, numbers.Number)):
            if val1 > val2:
                return 'total'
            else:
                return 'spread'

        else:
            try:
                if float(val1) > float(val2):
                    return 'total'
                else:
                    return 'spread'

            except:
                logging.error('{0} or {1} is not a number'.format(val1, val2))
                return None

    def _point_spread(self, odds):
        '''
        Takes point spread, can be negative or positive, assumes that spread is for team1
        Returns point spread for team1 and team2
        '''

        if odds == 0:
            team1_spread = 0
            team2_spread = 0

        elif isinstance(odds, numbers.Number):
            team1_spread = odds
            team2_spread = float(0) - odds

        else:
            team1_spread = None
            team2_spread = None

        return team1_spread, team2_spread

    def _rest(self, team):
        '''
        `days_last_game` tinyint not null,
        `back_to_back` bool not null,
        `back_to_back_to_back` bool not null,
        `three_in_four` bool not null,
        `four_in_five` bool not null,
        3+, B2B, B2B2B, 3IN4, 3IN4-B2B, 4IN5, 4IN5-B2B

        '''

        team['days_last_game'] = None
        rest_days = team.get('rest_days', None)
        
        if rest_days is not None:

            # B2B and B2B2B
            if 'B2B' in rest_days:
                team['back_to_back'] = True
                team['days_last_game'] = 0
            else:
                team['back_to_back'] = False

            if 'B2B2B' in rest_days:
                team['back_to_back_to_back'] = True
            else:
                team['back_to_back_to_back'] = False

            # 3IN4
            if '3IN4' in rest_days:
                team['three_in_four'] = True
                team['days_last_game'] = 1
            else:
                team['three_in_four'] = False

            # 4IN5
            if '4IN5' in rest_days:
                team['three_in_four'] = True
                team['four_in_five'] = True
                team['days_last_game'] = 0

            else:
                team['four_in_five'] = False

            if re.match(r'\d{1}', rest_days):
                team['days_last_game'] = rest_days[0]

        return team

    def _team_abbrev(self, team_name):
        '''
        NBAStuffer uses the city name only, not the team name, which is annoying b/c New Orleans / Charlotte multiple teams over time
        '''
        
        return self.names.city_to_short(team_name)

    def _total_and_spread(self, team1, team2, rowidx):
        '''
        Spreadsheet/csv has odds in an inconsistent format, so have to wrangle to make it uniform
        Returns game_ou, away_spread, home_spread
        '''

        # team1_odds, team2_odds are in -8 195 format (depending on whether total or spread
        # type will be "total" or "spread"
        team1_odds, team2_odds = self._get_closing(team1, team2, rowidx)
        team1_type = self._is_total_or_spread(team1_odds, team2_odds)

        game_ou = None
        away_spread = None
        home_spread = None
        
        if team1_odds is not None and team2_odds is not None:
            # if team1_odds is total, then team2_odds is spread
            # set the game_ou and then calculate spreads
            if team1_type == 'total':       
                game_ou = team1_odds
                away_spread, home_spread = self._point_spread(team2_odds)
                
            # if team1_odds is a spread,
            # calculate spreads for both teams and then set the game_ou
            elif team1_type == 'spread':
                away_spread, home_spread = self._point_spread(team1_odds)
                game_ou = team2_odds
                
            else:
                logging.error('row {0}: not spread or line - {1} {2}'.format(rowidx, team1_odds, team2_odds))

        else:
            logging.error('row {0}: not spread or line - {1} {2}'.format(rowidx, team1_odds, team2_odds))
       
        return game_ou, away_spread, home_spread

    def game_pairs(self, rows, headers):
        '''
        Goes through data rows two at a time (grouped by home/away team in same game)
        Returns list of (list of 2 dictionaries (home and away info) that represents one game)
        '''

        gp = []
        
        for rowidx in range(1,len(rows),2):
            # merge all of the cells in the row with the headers
            # proceed in pairs because 2 rows make for one game

            team1 = dict(zip(headers, rows[rowidx]))
            team2 = dict(zip(headers, rows[rowidx+1]))

            team1, team2 = self._fix_starters(team1, team2)
            
            if team1 and team2:
                # convert team city to 3-letter code
                # add codes to both teams in game_pair
                team1['team_code'] = self._team_abbrev(team1.get('teams', None))
                team2['team_code'] = self._team_abbrev(team2.get('teams', None))
                team1['opponent_team_code'] = team2['team_code']
                team2['opponent_team_code'] = team1['team_code']
                team1['away_team'] = team1['team_code']
                team1['home_team'] = team2['team_code']
                team2['away_team'] = team1['team_code']
                team2['home_team'] = team2['team_code']

                # opponent points
                team1['opponent_points'] = team2['pts']
                team2['opponent_points'] = team1['pts']
                
                # spread and totals will be 196, -8 or -8, 196
                # add game_ou, away_spread, home_spread to both teams in game_pair
                game_ou, away_spread, home_spread = self._total_and_spread(team1, team2, rowidx)
                team1['game_ou'] = game_ou
                team1['away_spread'] = away_spread
                team1['home_spread'] = home_spread
                team2['game_ou'] = game_ou
                team2['away_spread'] = away_spread
                team2['home_spread'] = home_spread

                # gamecode is in 20151030/DETCHI
                # gameid is nbadotcom identifier for games
                gamecode = self._gamecode(team1, team2)
                game_id = self._gameid(gamecode, team1.get('dataset', 'Regular'))
                team1['gamecode'] = gamecode
                team2['gamecode'] = gamecode
                team1['game_id'] = game_id
                team2['game_id'] = game_id
                gp.append([team1, team2])

                # rest
                team1 = self._rest(team1)
                team2 = self._rest(team2)

                # omit some fields - can pass parameter or use defaults
                for field in self.omit:
                    team1.pop(field, None)
                    team2.pop(field, None)
                    
            else:
                logging.error('%s | row %d: could not get team1 or team2 - %s' % (sheet.name, rowidx))

        return gp

    def headers(self, row):
        '''
        Takes first row of sheet or csv file and returns lowercase column header with no spaces
        '''

        return self._fix_headers([re.sub(r'\s+', '_', c).strip().lower() for c in row])
        
    def xlsx_game_pairs(self, sheet, headers):
        '''
        Goes through data rows two at a time (grouped by home/away team in same game)
        Returns list of (list of 2 dictionaries (home and away info) that represents one game)
        '''
        
        gp = []
        
        for rowidx in range(1,sheet.nrows,2):
            team1 = dict(zip(headers, rows[rowidx]))
            team2 = dict(zip(headers, rows[rowidx+1]))

            if team1 and team2:
                # convert team city to 3-letter code
                team1['team_code'] = self._team_abbrev(team1.get('teams', None))
                team2['team_code'] = self._team_abbrev(team2.get('teams', None))
                team1['away_team'] = team1['team_code']
                team1['home_team'] = team2['team_code']
                team2['away_team'] = team1['team_code']
                team2['home_team'] = team2['team_code']

                # spread and totals will be 196, -8 or -8, 196
                game_ou, away_spread, home_spread = self._total_and_spread(team1, team2, rowidx)
                team1['game_ou'] = game_ou
                team1['away_spread'] = away_spread
                team1['home_spread'] = home_spread
                team2['game_ou'] = game_ou
                team2['away_spread'] = away_spread
                team2['home_spread'] = home_spread

                # gamecode is in 20151030/DETCHI
                # gameid is nbadotcom identifier for games
                gamecode = self._gamecode(game_pair)
                game_id = self._gameid(gamecode)
                team1['gamecode'] = gamecode
                team2['gamecode'] = gamecode
                team1['game_id'] = game_id
                team2['game_id'] = game_id
                gp.append([team1, team2])

                # rest
                team1 = self._rest(team1)
                team2 = self._rest(team2)
                
            else:
                logging.error('%s | row %d: could not get team1 or team2 - %s' % (sheet.name, rowidx))

        return gp

    def xlsx_headers(self, sheet):
        '''
        Takes first row of sheet and returns lowercase column header with no spaces
        Still need to address issue of starting players, format in spreadsheet is off
        '''

        _headers = []

        for colidx in range(0, sheet.ncols):
            header = sheet.cell(0, colidx).value.strip()
            header = re.sub(r'\s+', '_', header)

            if header == '':
                header = 'starting_lineups'

            _headers.append(header.lower())

        return _headers

if __name__ == "__main__":
    pass
