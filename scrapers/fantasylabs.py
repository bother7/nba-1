import logging

#import browsercookie

from ewt.scraper import EWTScraper
from nba.dates import *


class FantasyLabsNBAScraper(EWTScraper):
    '''
    Usage:

        s = FantasyLabsNBAScraper()
        games_json = s.today()
        model_json = s.model() # model_name optional
        model_json = s.model('bales')

        for d in date_list('10_09_2015', '10_04_2015'):
            datestr = datetime.strf
            model_json = s.model(model_date=datestr)

    TODO: can make FantasyLabsParser base class
    Most of this code is identical with NFL
    '''

    def __init__(self, use_cache=1, **kwargs):

        '''
        EWTScraper parameters: 'expire_time', 'headers', 'use_cache'
        '''

        # see http://stackoverflow.com/questions/8134444
        EWTScraper.__init__(self, use_cache=use_cache, **kwargs)

        self.logger = logging.getLogger(__name__)

        if 'default_model' in kwargs:
            self.default_model = kwargs['default_model']
        else:
            self.default_model = 'default'

        if 'model_urls' in kwargs:
            self.model_urls = kwargs['model_urls']
        else:
            self.model_urls = {
                'default': 'http://www.fantasylabs.com/api/playermodel/2/{0}/?modelId=100605',
                'bales': 'http://www.fantasylabs.com/api/playermodel/2/{0}/?modelId=193714',
                'phan': 'http://www.fantasylabs.com/api/playermodel/2/{0}/?modelId=193718',
                'tournament': 'http://www.fantasylabs.com/api/playermodel/2/{0}/?modelId=193722',
                'cash': 'http://www.fantasylabs.com/api/playermodel/2/{0}/?modelId=193723'
            }

    def games_day(self, game_date):
        '''
        Gets json for games on single date

        Usage:
            s = FantasyLabsNBAScraper()
            content = s.game(game_date='10_04_2015')

        '''

        # test for datestring
        url = 'http://www.fantasylabs.com/api/sportevents/2/{0}'.format(game_date)
        content = self.get_json(url)

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

        for d in date_list(end_date, start_date):
            datestr = datetime.datetime.strftime(d, site_format('fl'))
            contents[datestr] = self.games_day(game_date=datestr)

        return contents

    def games_today(self):
        '''
        Gets json for today's games

        Usage:
            s = FantasyLabsNBAScraper()
            content = s.games_today()

        '''

        day = datetime.datetime.strftime(datetime.datetime.today(), site_format('fl'))
        url = 'http://www.fantasylabs.com/api/sportevents/2/{0}'.format(day)
        content = self.get_json(url)

        if not content:
            logging.error('could not get content from url: {0}'.format(url))

        return content

    def model(self, model_day=None, model_name='default'):
        '''
        Gets json for model, default to Phan model
        Stats in most models the same, main difference is the ranking based on weights of factors present in all models

        Usage:
            phan_model_json = s.model()
            bales_model_json = s.model('bales')

        '''

        # if model_name is none or not in dict, use default
        if self.model_urls.get(model_name):
            url = self.model_urls.get(model_name)
            logging.debug('model: model_url is {0}'.format(url))

        else:
            logging.warn('scraper.model: could not find url for {0} model'.format(model_name))
            url = self.model_urls.get(self.default_model)
            logging.debug('scraper.model: using default model'.format(url))

        # does not require date in specific format, so need to convert to datetime then properly format
        if model_day:
            # ensure proper date format: infer format using format_type, convert to datetime and then back to string
            fmt = format_type(model_day)
            logging.debug('scraper.model: date format is {0}'.format(fmt))
            dt = datetime.datetime.strptime(model_day, fmt)
            logging.debug('scraper.model: dt is {0}'.format(dt))
            model_day = datetime.datetime.strftime(dt, site_format('fl'))
            logging.debug('scraper.model: model_day is {0}'.format(model_day))

        else:
            model_day=datetime.datetime.strftime(datetime.datetime.today(), site_format('fl'))
            logging.debug('scraper.model: model_day is {0}'.format(model_day))

        #return self.get_json(url=url.format(model_day))
        #cj = browsercookie.chrome()
        return self.get_json(url=url.format(model_day)) #, cookies=cj)

    def models(self, start_date, end_date, model_name=None):
        '''
        Gets json for models in date range, default to Phan model
        Stats in most models the same, main difference is the ranking based on weights of factors present in all models

        Usage:
            s = FantasyLabsNBAScraper()
            models = s.models(start_date='10_04_2015', end_date='10_09_2015', model_name='phan')
            
        '''

        if not model_name:
            model_name = self.default_model

        contents = {}

        for d in date_list(end_date, start_date):
            datestr = datetime.datetime.strftime(d, site_format('fl'))
            contents[datestr] = self.model(model_day=datestr, model_name=model_name)

        return contents

if __name__ == "__main__":
    pass
