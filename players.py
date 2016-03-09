import logging
import time

from nba.scrapers.nbacom import NBAComScraper
from nba.parsers.nbacom import NBAComParser
from nba.db.pgsql import NBAPostgres

from nba.names import match_player

class NBAPlayers(object):
    '''
    Provides for updating nba.com players table (stats.players)
    Also permits cross-reference of player names and player ids from various sites(stats.player_xref)

    Usage:
        np = NBAComPlayers(db=True)
        np.missing_players('2015-16')

    '''
    
    def __init__(self, db=False, polite=False):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.scraper = NBAComScraper()
        self.parser = NBAComParser()
        self.polite = polite
        self.sites = ['dk', 'draftkings', 'draft kings', 'doug', 'dougstats', 'espn', 'fd', 'fanduel', 'fan duel',
                 'fantasylabs', 'fantasy labs', 'rg', 'rotoguru', 'roto guru']

        if db:
            self.nbadb = NBAPostgres()
        else:
            self.nbadb = None

    def _dk_name(self, name):
        return {
        }.get(name, None)

    def _doug_name(self, name):
        return {
        }.get(name, None)

    def _espn_name(self, name):
        return {
        }.get(name, None)

    def _fd_name(self, name):
        return {
        }.get(name, None)

    def _fl_name(self, name):
        return {
        }.get(name, None)

    def _rg_name(self, name):
        return {
            'Amundson, Louis': 'Amundson, Lou',
            'Barea, Jose': 'Barea, Jose Juan',
            'Bhullar, Sim': '',
            'Brown, Jabari': '',
            'Datome, Luigi': '',
            'Drew II, Larry': '',
            'Hairston, P.J.': 'Hairston, PJ',
            'Hayes, Chuck': 'Hayes, Charles',
            'Hickson, J.J.': 'Hickson, JJ',
            'Hilario, Nene': 'Nene',
            'Hunter, R.J.': 'Hunter, RJ',
            'Jones III, Perry': 'Jones, Perry',
            'Kilpatrick, Sean': '',
            'Lucas, John': '',
            'Matthews, Wes': 'Matthews, Wesley',
            'McCollum, C.J.': 'McCollum, CJ',
            'McConnell, T.J.': 'McConnell, TJ',
            'McDaniels, K.J.': 'McDaniels, KJ',
            'Miles, C.J.': 'Miles, CJ',
            'Murry, Toure': '',
            'Redick, J.J.': 'Redick, JJ',
            'Robinson III, Glenn': 'Robinson, Glenn',
            'Smith, Ishmael': 'Smith, Ish',
            'Stoudemire, Amare': '''Stoudemire, Amar'e''',
            'Taylor, Jeffery': 'Taylor, Jeff',
            'Tucker, P.J.': 'Tucker, PJ',
            'Warren, T.J.': 'Warren, TJ',
            'Watson, C.J.': 'Watson, CJ',
            'Wear, David': '',
            'Wilcox, C.J.': 'Wilcox, CJ',
            'Williams, Louis': 'Williams, Lou',
            'Williams, Maurice': 'Williams, Mo'
        }.get(name, None)

    def missing_players(self, season):
        '''
        Looks for missing players by comparing current_season_gamelogs and players tables
        Fetches player_info by id, inserts player into players table

        Arguments:
            season (str): example '2015-16' for the current season

        Returns:
            missing (list): list of dictionaries that represent row in players table
        '''

        if not self.nbadb:
            raise ValueError('missing_players requires a database connection')

        missing = []

        # get list of ids that appear in current_season_gamelogs but not players
        sql = '''
            SELECT DISTINCT player_id FROM stats.cs_player_gamelogs
            WHERE player_id NOT IN (SELECT DISTINCT nbacom_player_id FROM stats.players)
        '''
        
        results = self.nbadb.select_list(sql)

        if results:
            for pid in results:
                content = self.scraper.player_info(pid, season)
                pi = self.parser.player_info(content)
                
                pi = {k.lower(): v for k,v in pi.iteritems()}
                pi.pop('games_played_flag', None)
                pi['nbacom_team_id'] = pi.get('team_id', None)
                pi.pop('team_id', None)
                pi['nbacom_position'] = pi.get('position', None)
                pi.pop('position', None)
                pi['nbacom_player_id'] = pi.get('person_id', None)
                pi.pop('person_id', None)

                if pi.get('height', None):
                    try:
                        feet, inches = pi['height'].split('-')
                        pi['height'] = int(feet)*12 + int(inches)

                    except: pass

                # have to convert empty strings to None, otherwise insert fails for integer/numeric columns
                player_info= {}
                for k,v in pi.iteritems():
                    if not v:
                        player_info[k] = None
                    else:
                        player_info[k] = v
                missing.append(player_info)

                if self.polite: time.sleep(1)

        if missing: self.nbadb.insert_dicts(missing, 'stats.players')

        return missing

    def nbacom_player(self, site, player_name):
        '''
        Returns name and id of player on nba.com

        Arguments:
            site (str): 'dk', 'fd', 'rg', 'doug', 'espn'
            player_name (str): 'Kevin Durant', 'Lebron James'

        Returns:
            player (list): first item is player name, second item is player id
        '''
        sites = ['dk', 'draftkings', 'draft kings', 'doug', 'dougstats', 'espn', 'fd', 'fanduel', 'fan duel',
                 'fantasylabs', 'fantasy labs', 'rg', 'rotoguru', 'roto guru']

        if site.lower() not in sites:
            # should try name matcher
            pass

        elif site.lower() == 'dk':
            return self._dk_name(player_name)

        elif 'doug' in site.lower():
            return self._doug_name(player_name)

        elif 'espn' in site.lower():
            return self._espn_name(player_name)

        elif site.lower() == 'fd' or 'duel' in site.lower():
            return self._fd_name(player_name)

        elif site.lower() == 'fl' or 'labs' in site.lower():
            return self._fl_name(player_name)

        elif site.lower() == 'rg' or 'guru' in site.lower():
            return self._rg_name(player_name)

    def recent_nbacom_players(self):
        '''
        Gets last couple of years of players from nba.com
        Returns dictionary with key of name + team
        '''
        if not self.nbadb:
            raise ValueError('missing_players requires a database connection')

        sql = '''SELECT * FROM recent_nba_players'''

        # can also return in dict format
        # {'{0} {1}'.format(item['player_name'], item.get('team_code')):item for item in self.nbadb.select_dict(sql)}
        return self.nbadb.select_dict(sql)

    def site_to_nbacom(self, site):
        '''
        Returns dictionary with name of player on site, value is list of name and id of player on nba.com

        Arguments:
            site (str): 'dk', 'fd', 'rg', 'doug', 'espn'

        Returns:
            players (dict): key is player name on site, value is list [nbacom_player_name, nbacom_player id]
        '''

        if site.lower() not in self.sites:
            # should try name matcher
            pass

        elif site.lower() == 'dk':
            return self._dk_name(player_name)

        elif 'doug' in site.lower():
            return self._doug_name(player_name)

        elif 'espn' in site.lower():
            return self._espn_name(player_name)

        elif site.lower() == 'fd' or 'duel' in site.lower():
            return self._fd_name(player_name)

        elif site.lower() == 'fl' or 'labs' in site.lower():
            return self._fl_name(player_name)

        elif site.lower() == 'rg' or 'guru' in site.lower():
            return self._rg_name(player_name)

if __name__ == '__main__':
    pass
