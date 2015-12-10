from datetime import datetime
import logging

from EWTScraper import EWTScraper


class FantasyLabsNBAScraper(EWTScraper):
    '''
    Usage:

        s = FantasyLabsNBAScraper()
        games_json = s.today()
        model_json = s.model() # model_name optional
        model_json = s.model('bales')

        for d in s._date_list('10_09_2015', '10_04_2015'):
            datestr = datetime.strf
            model_json = s.model(model_date=datestr)

    TODO: can make FantasyLabsParser base class
    Most of this code is identical with NFL
    '''

    def __init__(self,**kwargs):

        '''
        EWTScraper parameters: 'dldir', 'expire_time', 'headers', 'keyprefix', 'mc', 'use_cache'
        '''

        # see http://stackoverflow.com/questions/8134444
        EWTScraper.__init__(self, **kwargs)

        logging.getLogger(__name__).addHandler(logging.NullHandler())

        if 'model_urls' in kwargs:
            self.model_urls = kwargs['models']
        else:
            self.model_urls = {
                'bales': 'http://www.fantasylabs.com/api/playermodel/2/{0}/?modelId=193714',
                'phan': 'http://www.fantasylabs.com/api/playermodel/2/{0}/?modelId=193718',
                'tournament': 'http://www.fantasylabs.com/api/playermodel/2/{0}/?modelId=193722',
                'cash': 'http://www.fantasylabs.com/api/playermodel/2/{0}/?modelId=193723'
            }

    def _date_list(self, d1, d2):
        '''
        Takes two dates or datestrings and returns a list of days

        Usage:
            for d in s._date_list('10_09_2015', '10_04_2015'):
                print datetime.strftime(d, '%m_%d_%Y')
        '''
        if isinstance(d1, basestring):
            try:
                d1 = datetime.strptime(d1, '%m_%d_%Y')

            except:
                logging.error('{0} is not in %m_%d_%Y format'.format(d1))
                
        if isinstance(d2, basestring):
            try:
                d2 = datetime.strptime(d2, '%m_%d_%Y')

            except:
                logging.error('{0} is not in %m_%d_%Y format'.format(d1))

        season = d1-d2

        return [d1 - datetime.timedelta(days=x) for x in range(0, season.days+1)]

    def model(self, **kwargs):
        '''
        Gets json for model, default to Phan model
        Stats in most models the same, main difference is the ranking based on weights of factors present in all models

        Usage:
            phan_model_json = s.model()
            bales_model_json = s.model('bales')

        '''

        if 'model_name' in kwargs:
            model_name = kwargs['model_name']
        else:
            model_name='phan'

        if 'model_day' in kwargs:
            model_day = kwargs['model_day']
        else:
            model_day=datetime.strftime(datetime.today(),'%m_%d_%Y')

        content = None       
        url = self.model_urls.get(model_name, None)

        if not url:
            logging.error('could not find url for {0} model'.format(model_name))

        else:
            # have to add today's date in mm_dd_yyyy format to URL
            content = self.get(url.format(model_day))

            if not content:
                logging.error('could not get content from url: {0}'.format(url))

        return content

    def models(self, start_date, end_date, model_name='phan'):
        '''
        Gets json for models in date range, default to Phan model
        Stats in most models the same, main difference is the ranking based on weights of factors present in all models

        Usage:
            s = FantasyLabsNBAScraper()
            models = s.models(start_date='10_04_2015', end_date='10_09_2015', model_name='phan')
            
        '''

        contents = {}

        for d in self._date_list(end_date, start_date):
            datestr = datetime.strftime(d, '%m_%d_%Y')
            contents[datestr] = self.model(model_day=datestr)

        return contents

    def games_day(self, game_date):
        '''
        Gets json for games on single date

        Usage:
            s = FantasyLabsNBAScraper()
            content = s.game(game_date='10_04_2015')
            
        '''

        url = 'http://www.fantasylabs.com/api/sportevents/2/{0}'.format(game_date)
        content = self.get(url)

        if not content:
            logging.error('could not get content from url: {0}'.format(url))

        return content

    def games_days(self, start_date, end_date):
        '''
        Gets json for games in date range

        Usage:
            s = FantasyLabsNBAScraper()
            games = s.games(start_date='10_04_2015', end_date='10_09_2015')
            
        '''

        contents = {}

        for d in self._date_list(end_date, start_date):
            datestr = datetime.strftime(d, '%m_%d_%Y')
            contents[datestr] = self.game_day(game_date=datestr)

        return contents

    def games_today(self):
        '''
        Gets json for today's games

        Usage:
            s = FantasyLabsNBAScraper()
            content = s.games_today()
            
        '''

        day = datetime.strftime(datetime.today(), '%m_%d_%Y')
        url = 'http://www.fantasylabs.com/api/sportevents/2/{0}'.format(day)
        content = self.get(url)

        if not content:
            logging.error('could not get content from url: {0}'.format(url))

        return content

if __name__ == "__main__":
    pass
