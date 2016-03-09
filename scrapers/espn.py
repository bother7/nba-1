'''
ESPNNBAScraper
This is just a shell based on NFL - need to build out for NBA 
'''

import logging
import os

from bs4 import BeautifulSoup

from EWTScraper import EWTScraper


class ESPNNBAScraper(EWTScraper):
    '''

    '''

    def __init__(self, **kwargs):
        # see http://stackoverflow.com/questions/8134444
        EWTScraper.__init__(self, **kwargs)

        logger = logging.getLogger(__name__)

        if 'maxindex' in kwargs:
            self.maxindex = kwargs['maxindex']
        else:
            self.maxindex = 400

        if 'projection_urls' in 'kwargs':
            self.projection_urls = kwargs['projection_urls']
        else:
            base_url = 'http://games.espn.go.com/ffl/tools/projections?'
            idx = [0, 40, 80, 120, 160, 200, 240, 280, 320, 360]
            self.projection_urls = [base_url + 'startIndex=' + x for x in idx]

    def player_page(self, content):

        # <td align="left"><a href="http://espn.go.com/nba/player/_/id/110/kobe-bryant">Kobe Bryant</a>

        players = {}
        soup = BeautifulSoup(content)
        pattern = re.compile('player/_/id/(\d+)/(\w+[^\s]*)', re.IGNORECASE)
        links = soup.findAll('a', href=pattern)

        for link in links:
            match = re.search(pattern, link['href'])

            if match:
                players[match.group(1)] = match.group(2)

            else:
                print 'could not get {0}'.format(link['href'])

        return players

    def players(self):

        # now get all of the player pages
        base_url = 'http://stats.nba.com/stats/commonplayerinfo?PlayerID='
        ids = [p['PERSON_ID'] for p in players]
        for id in ids:
          
          # create url
          url = base_url + str(id)
          logging.debug('url is ' + url)
          
          # create filename
          fn = os.path.join(expanduser("~"), savedir, str(id) + '.json')
          logging.debug('filename is ' + fn)
          
          # get the resource
          resp, content = h.request(url, "GET")
          logging.debug('status is ' + str(resp.status))  

          # if request is success, then save resource to file
          if resp.status == 200:   
            try:
              with open(fn, 'w') as outfile:
                outfile.write(content)
                logging.debug('saved player ' + str(id) + ' to ' + fn)  
            except:
              logging.exception('could not save file ' + fn)

        return content

    def projections(self, subset=None):
        pages = []
        if subset:
            for idx in subset:
                content = self.get(self.projection_urls[idx])
                pages.append(content)
        else:
            for url in self.projection_urls:
                content = self.get(url)
                pages.append(content)

        return pages


class FiveThirtyEightNBAScraper(EWTScraper):
    '''

    '''

    def __init__(self, **kwargs):
        # see http://stackoverflow.com/questions/8134444
        EWTScraper.__init__(self, **kwargs)

        self.logger = logging.getLogger(__name__)

    def espn_player_ids(self, pklfname=None):

        # this is a list of lists
        all_players = {}

        page_numbers = range(1,11)

        for page_number in page_numbers:
            url = 'http://espn.go.com/nba/salaries/_/page/{0}/seasontype/1'.format(page_number)
            content = self.get(url)
            players = player_page(content)
            for id, name in players.items():
                all_players[id] = name

        if pklfname:
            with open(pklfname, 'w') as outfile:
                json.dump(all_players, outfile, indent=4, sort_keys=True)

        return all_players

    def fivethirtyeight_nba(self, pklfname, savedir):

        # get player_ids
        with open(pklfname, 'r') as infile:
            espn_players = json.load(infile)

        for player_code in espn_players.values():
            player_code = re.sub('[.\']', '', player_code)
            fn = os.path.join(savedir, '{0}.json'.format(player_code))

            if os.path.isfile(fn):
                print 'already have {0}'.format(fn)

            else:
                if len(player_code) > 3:
                    content, from_cache = simscores(player_code)

                    if content:
                        with open(fn, 'w') as outfile:
                            outfile.write(content)
                    else:
                        print 'could not get {0}'.format(player_code)

                    if from_cache:
                        print 'got url from cache'

                    else:
                        time.sleep(2)

                else:
                    print 'could not get {0}'.format(player_code)

    
    def simscores(self, player_code):
        url = 'http://projects.fivethirtyeight.com/carmelo/{0}.json'.format(player_code)

        try:
            content = self.get(url)
            return content
            
        except:
            self.logger.exception('could not get {0}'.format(url))
            return None

if __name__ == "__main__":
    pass
