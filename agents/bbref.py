import datetime
import logging
from string import ascii_lowercase

from nba.dates import datetostr
from nba.names import fuzzy_match
from nba.parsers.bbref import BBRefParser
from nba.pipelines.bbref import *
from nba.player.nbacom import *
from nba.scrapers.bbref import BBRefScraper

from dateutil.parser import *


class BBRefAgent(object):
    '''
    Performs script-like tasks using NBA.com API
    '''

    def __init__(self, db=None, cache_name='bbref-agent', cookies=None, table_names=None):
        '''
        Args:
            cache_name (str): for scraper cache_name
            cookies: cookie jar
            db (NBAPostgres): instance
            table_names (dict): Database table names

        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.scraper = BBRefScraper(cache_name=cache_name, cookies=cookies)
        self.parser = BBRefParser()
        self.db = db
        self.bbref_players = {}

    def match_gamelog_player(self, gamelog_player):
        '''
        Matches player from nbacom_gamelog with bbref player

        Args:
            gamelog_player (dict):

        Returns:
            dict

        '''
        # gamelog player
        # {'PLAYER_ID': 2544, 'PLAYER_NAME': 'LeBron James',
        # 'TEAM_ABBREVIATION': 'CLE', 'TEAM_NAME': 'Cleveland Cavaliers'}
        #
        # bbref player
        # {'source': 'bref', source_player_dob': '1992-03-23', 'source_player_id': 'irvinky01',
        # 'source_player_name': 'Kyrie Irving', 'source_player_position': 'Point Guard',
        # 'source_player_team_code': 'BOS', 'source_player_team_name': 'Boston Celtics'}

        # bbref_players caches pages for each letter
        # helpful if doing more than a few players
        fn, ln = gamelog_player['PLAYER_NAME'].split()
        letter = ln[0].lower()
        if not self.bbref_players.get(letter):
            content = self.scraper.players(letter)
            self.bbref_players[letter] = self.parser.players(content)

        # step one: find all players with the same name
        matches = [p for p in self.bbref_players.get(letter) if
                   p['source_player_name'] == gamelog_player['PLAYER_NAME']]

        # if no matches, then look for individual player page on bbref
        # newer players may not have been added to the letter index page ('a', 'b', 'c')
        if not matches:
            pid = bbref_player_id(fn, ln)
            logging.info('trying player page for {}'.format(pid))
            content = self.scraper.player_page(pid)
            bbref_player = self.parser.player_page(content, pid)
            if bbref_player:
                return bbref_player

        # if there is only 1 match, then assume it is the right player
        # need to get the player page, which has the full position
        elif matches and len(matches) == 1:
            logging.info('add_gamelog_player: found 1 match')
            pid = matches[0].get('source_player_id')
            content = self.scraper.player_page(pid)
            bbref_player = self.parser.player_page(content, pid)
            if bbref_player:
                return bbref_player

        # if more than 1 match, then try to match team as well
        # very unlikely to have duplicate
        elif matches and len(matches) > 1:
            logging.info('add_gamelog_player: found >1 match')
            for match in matches:
                pn = gamelog_player['PLAYER_NAME']
                pt = gamelog_player['TEAM_NAME']
                for match in matches:
                    bbrefn = match['source_player_name']
                    bbreft = match['source_player_team_name']
                    if (pn == bbrefn and pt == bbreft):
                        pid = match.get('source_player_id')
                        content = self.scraper.player_page(pid)
                        bbref_player = self.parser.player_page(content, pid)
                        if bbref_player:
                            return bbref_player

        else:
            logging.info('no match for {}'.format(gamelog_player['PLAYER_NAME']))
            return None

    def match_nbacom_player(self, nbacom_player):
        '''
        Matches nbacom player with bbref player
           
        Args:
            nbacom_player (dict):
    
        Returns:
            dict

        '''
        # nbacom player
        # {'birthdate': datetime.datetime(1993, 8, 1, 0, 0), 'country': 'Spain',
        # 'display_first_last': 'Alex Abrines', 'draft_number': 32, 'draft_round': 2, 'draft_year': 2013,
        # 'first_name': 'Alex', 'from_year': 2016, 'height': 42, 'jersey': 8,
        # 'last_affiliation': 'Spain/Spain', 'last_name': 'Abrines', 'nbacom_player_id': 203518,
        # 'nbacom_position': 'G', 'school': '', 'weight': 190}
        #
        # bbref player
        #{'source': 'bref', source_player_dob': '1992-03-23', 'source_player_id': 'irvinky01',
        # 'source_player_name': 'Kyrie Irving', 'source_player_position': 'Point Guard',
        # 'source_player_team_code': 'BOS', 'source_player_team_name': 'Boston Celtics'}

        # bbref_players caches pages for each letter
        # helpful if doing more than a few players
        letter = nbacom_player['last_name'][0].lower()
        if not self.bbref_players.get(letter):
            content = self.scraper.players(letter)
            self.bbref_players[letter] = self.parser.players(content)

        # step one: find all players with the same name
        matches = [p for p in self.bbref_players.get(letter) if
                   p['source_player_name'] == nbacom_player.get('display_first_last')]

        # if no matches, then look for individual player page on bbref
        # newer players may not have been added to the letter index page ('a', 'b', 'c')
        if not matches:
            pid = bbref_player_id(nbacom_player['first_name'], nbacom_player['last_name'])
            logging.info('trying player page for {}'.format(pid))
            content = self.scraper.player_page(pid)
            bbref_player = self.parser.player_page(content, pid)
            if bbref_player:
                return bbref_player

        # if there is only 1 match, then assume it is the right player
        # need to get the player page, which has the full position
        elif matches and len(matches) == 1:
            logging.info('add_gamelog_player: found 1 match')
            pid = matches[0].get('source_player_id')
            content = self.scraper.player_page(pid)
            bbref_player = self.parser.player_page(content, pid)
            if bbref_player:
                return bbref_player

        # if more than 1 match, then try to match team as well
        # very unlikely to have duplicate
        elif matches and len(matches) > 1:
            logging.info('add_gamelog_player: found >1 match')
            for match in matches:
                dob = match['source_player_dob']
                if dob == datetostr(nbacom_player.get('birthdate'), fmt='nba'):
                    return match

        else:
            logging.info('no match for {}'.format(nbacom_player['display_first_last']))
            return None

    def update_player_xref(self):
        '''
        Updates player_xref table with bbref players
        
        Args:
            None
            
        Returns:
            None
            
        '''
        nbacom_players_d = nbacom_xref(self.db)
        nbacom_players_d2 = nbacom_xref(self.db, with_pos=True)
        wanted = ['source', 'source_player_id', 'source_player_name', 'source_player_position']

        # loop through each 'letter' page of players
        for letter in ascii_lowercase:
            if letter == 'x':
                continue
            logging.info('starting {}'.format(letter))
            content = self.scraper.players(letter)
            for p in self.parser.players(content):
                # try direct name match first
                # if no match, then use fuzzy matching
                # if 1 match, then add to database
                # if more then 1 result, then consider positions as well
                match = nbacom_players_d.get(p['source_player_name'].lower())
                if not match:
                    # try fuzzy matching
                    # TODO: implement fuzzy match
                    if p.get('active'):
                        logging.error('could not match {}'.format(p))
                elif len(match) == 1:
                    toins = {k: v for k, v in p.items() if k in wanted}
                    toins['source'] = 'bbref'
                    toins['nbacom_player_id'] = match[0]['nbacom_player_id']
                    toins['source_player_dob'] = datetime.datetime.strftime(parse(p['birth_date']),
                                                                            '%Y-%m-%d')
                    self.db._insert_dict(toins, 'extra_misc.player_xref')
                else:
                    key = '{}_{}'.format(p['source_player_name'], p['source_player_position']).lower()
                    match2 = nbacom_players_d2.get(key)
                    if not match2:
                        if p.get('active'):
                            match3 = fuzzy_match(key, list(nbacom_players_d2.keys()))
                            if match3:
                                try:
                                    toins = {k: v for k, v in p.items() if k in wanted}
                                    toins['source'] = 'bbref'
                                    toins['nbacom_player_id'] = nbacom_players_d2.get(match3).get('nbacom_player_id')
                                    toins['source_player_dob'] = datetime.datetime.strftime(parse(p['birth_date']),
                                                                                        '%Y-%m-%d')
                                    self.db._insert_dict(toins, 'extra_misc.player_xref')
                                except:
                                    logging.error('could not match {}'.format(p))
                        else:
                            logging.error('could not match {}'.format(p))
                    elif match2 and len(match2) == 1:
                        toins = {k: v for k, v in p.items() if k in wanted}
                        toins['source'] = 'bbref'
                        toins['nbacom_player_id'] = match2[0]['nbacom_player_id']
                        toins['source_player_dob'] = datetime.datetime.strftime(parse(p['birth_date']),
                                                                                '%Y-%m-%d')
                        self.db._insert_dict(toins, 'extra_misc.player_xref')
                    else:
                        if p.get('active'):
                            logging.error('could not match {}'.format(p))

        '''
        TODO: can match DOB for multiple players
        more accurate than fuzzy match
        wanted = ['source_player_id', 'source_player_position', 'source_player_name']
        for m in tomatch:
            dob = parse(m.get('birth_date')).date()
            nbap = nbadb2.select_scalar(q.format(m['source_player_name'].split()[-1] , dob))
            if nbap:
                toins = {k:v for k,v in m.items() if k in wanted}
                toins['source'] = 'bbref'
                toins['nbacom_player_id'] = nbap
                toins['source_player_dob'] = m['birth_date']
                nbadb2._insert_dict(toins, 'extra_misc.player_xref') 
        '''


if __name__ == '__main__':
    a = BBRefAgent(db=getdb())
    a.update_player_xref()

    #pass