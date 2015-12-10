'''
ESPNNBAScraper
This is just a shell based on NFL - need to build out for NBA 
'''

from EWTScraper import EWTScraper
import logging

class ESPNNBAScraper(EWTScraper):
    '''

    '''

    def __init__(self, **kwargs):
        # see http://stackoverflow.com/questions/8134444
        EWTScraper.__init__(self, **kwargs)

        if 'logger' in kwargs:
            self.logger = kwargs['logger']
        else:
            self.logger = logging.getLogger(__name__) \
                .addHandler(logging.NullHandler())

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

if __name__ == "__main__":
    pass
