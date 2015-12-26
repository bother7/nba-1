from datetime import datetime
import logging
import pprint
import re


class RotoGuruNBAParser:
    '''
    RotoGuruNBAParser

    Usage:
        site = 'dk'
        p = RotoGuruNBAParser()

        from RotoGuruNBAScraper import RotoGuruNBAScraper
        s = RotoGuruNBAScraper()
        content = s.salaries_day('2015-12-09', 'dk')

        pprint.pprint(p.salaries(content, site))

    '''

    def __init__(self):
        logging.getLogger(__name__).addHandler(logging.NullHandler())

    def _pre_ssv(self, content):
        '''
        On rotoguru, the ssv list is enclosed in a <pre> block
        '''

        pattern = re.compile(r'<pre>(Date;.*?)</pre>',  re.IGNORECASE | re.MULTILINE | re.DOTALL)
        match = re.search(pattern, content)

        if match:
            ssv = match.group(1)
            return ssv.split('\n')

        else:
            return None
            
        return rows

    def _salaries_headers(self, row):
        '''
        Date;GID;Pos;Name;Starter;DK Pts;DK Salary;Team;H/A;Oppt;Team Score;Oppt Score;Minutes;Stat line
        '''

        return ['game_date', 'rotoguru_gid', 'pos', 'player_name', 'starter', 'points', 'salary', 'team_abbreviation',
                'venue', 'opponent_team', 'team_score', 'opponent_score', 'min', 'stat_line']
        

    def data(self, content):    
        '''

        '''
        players = []

        # odd error in content - uses ", instead of semicolon
        content = content.replace('",', ';')    

        # they have HIDEOUS html in these files
        # first have to find where the good stuff starts and ends
        match = re.search(r'(gid;.*?)<br>\n(.*?)<br>\s+<hr>', content, re.MULTILINE|re.DOTALL|re.IGNORECASE)

        if match:
            # group 1 is gid;xxx;final_header
            header_line = match.group(1)

            # group 2 is everything else; will have to split on <br> and newline
            player_lines = match.group(2).split("<br>\n")

            # header_line should be semi-colon separated data
            if header_line:
                header_parts = header_line.split(';')
                logging.debug("header parts\n % s" % pprint.pformat(header_parts))
                headers = [re.sub('\s+', '_', p).strip() for p in header_parts]

            # each player_line is semi-colon separated, need to remove whitespace
            # use ordered collection for debugging ease (parameter order in GET)
            # but can also use an ordinary dictionary
            if player_lines:
                for pl in player_lines:
                    player_parts = [p.strip() for p in pl.split(';')]
                    player = dict(zip(headers, player_parts))
                    players.append(player)

        return players

    def salaries(self, content, site):
        '''
        Returns list of dictionaries with player salary information

        Usage:
            players = p.salaries(content, 'dk')
            dk = p.draftkings(content, 'dk')

        '''
        
        players = []
        rows = self._pre_ssv(content)
        header_row = rows.pop(0)
        headers = self._salaries_headers(header_row)
            
        for row in rows:
            cells = row.split(';')
            player = dict(zip(headers, cells))
            player['site'] = site

            # fix gamedate
            # mysql default is YYYY-MM-DD
            d = player.get('game_date', None)

            if d:
                player['game_date'] = datetime.strftime(datetime.strptime(d,'%Y%m%d'),'%Y-%m-%d')               
                players.append(player)

            # team abbreviations should be uppercase
            t = player.get('team_abbreviation', None)

            if t:
                player['team_abbreviation'] = t.upper()

            t = player.get('opponent_team', None)

            if t:
                player['opponent_team'] = t.upper()


            # salary has non-numeric characters
            points = player.get('points', None)
            salary = player.get('salary', None)
            minutes = player.get('min', None)

            if salary:
                player['salary'] = int(re.sub("[^0-9]", "", salary))

            # player value
            if minutes == 'DNP' or minutes == 'NA':
                pass
                
            else:
                try:
                    player['points_per_minute'] = float(points)/float(minutes)
                    player['multiple'] = float(points)/(player['salary']/1000)

                except:
                    logging.error('could not convert {0} {1}'.format(points, minutes))

            # fix missing - want NULL value instead of empty string
            stat_line = player.get('stat_line', None)
            starter = player.get('starter', None)

            if not stat_line or stat_line == '':
                player['stat_line'] = None
                
            if not starter or player['starter'] == '':
                player['starter'] = 0
                
        return players
        
    def draftkings(self, lines):    
        '''
        
        '''
        players = []

        # header_line should be semi-colon separated data
        #header_line = [p.strip() for p in lines.pop(0).split(';')]
        #headers = [re.sub('\s+', '_', p).strip() for p in header_line.split(';')]
        headers = [p.strip() for p in lines.pop(0).split(';')]
                
        # each player_line is semi-colon separated, need to remove whitespace
        # use ordered collection for debugging ease (parameter order in GET)
        # but can also use an ordinary dictionary
        for line in lines:
            player_parts = [p.strip() for p in line.split(';')]
            player = dict(zip(headers, player_parts))
            players.append(player)

        return players

if __name__ == '__main__':  
    pass
