import logging
import time

from nba.scrapers.nbacom import NBAComScraper
from nba.parsers.nbacom import NBAComParser
from nba.db.pgsql import NBAPostgres

from NameMatcher import match_player

class NBAPlayers(object):
    '''
    Utility function for comparing players from different sites and updating players table
    
    Usage:
        np = NBAComPlayers(db=True)
        np.missing_players('2015-16')

    '''
    
    def __init__(self, db=False):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.scraper = NBAComScraper()
        self.parser = NBAComParser()
        self.polite = False

        if db:
            self.nbadb = NBAPostgres()
        else:
            self.nbadb = None

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
            raise ValueError('must call db=True or set self.db value')

        missing = []

        # get list of ids that appear in current_season_gamelogs but not players
        sql = '''
            SELECT DISTINCT player_id FROM current_season_player_gamelogs
            WHERE player_id NOT IN (SELECT DISTINCT person_id FROM players)
        '''
        
        cursor = self.nbadb.conn.cursor()
        cursor.execute(sql)

        # loop through ids that need to be added and fetch json
        # nba.com json uses capitalized keys, also I have renamed some in the database
        # must drop unused keys (those that are not in the players table) otherwise insert_dicts method will fail
        results = cursor.fetchall()

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

                if pi.get('height', None):
                    try:
                        feet, inches = pi['height'].split('-')
                        pi['height'] = int(feet)*12 + int(inches)

                    except:
                        pass

                # have to convert empty strings to None, otherwise insert fails for integer/numeric columns
                player_info= {}
                for k,v in pi.iteritems():
                    if not v:
                        v = None
                        
                    player_info[k] = v
                    
                missing.append(player_info)

                if self.polite:
                    sleep(1)
                
        self.nbadb.insert_dicts(missing, 'players')
        return missing

    def rg_to_nbadotcom(self, name):
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

if __name__ == '__main__':
    pass
