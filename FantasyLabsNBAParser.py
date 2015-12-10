import json
import logging
import pprint


class FantasyLabsNBAParser():
    '''
    FantasyLabsNBAParser

    Usage:
        p = FantasyLabsNBAParser()
        games = p.games(games_json)
        model = p.model(model_json)

        for model_json) in models:
            p.model(model_json)

    TODO: can make FantasyLabsParser base class
    Most of this code is identical with FantasyLabsNFLParser           
    '''

    def __init__(self,**kwargs):
        '''

        '''

        logging.getLogger(__name__).addHandler(logging.NullHandler())
                        

    def games(self, content, **kwargs):
        '''
        Parses json that is list of games

        Usage:
            games = p.games(games_json)
            games = p.games(games_json, omit=[])

        '''

        if 'omit' in kwargs:
            omit = kwargs['omit']

        else:
            omit = ['ErrorList', 'ReferenceKey', 'HomePrimaryPlayer', 'VisitorPrimaryPlayer', 'HomePitcherThrows', 'VisitorPitcherThrows','LoadWeather', 'StadiumDirection','StadiumStatus', 'StadiumType', 'PeriodDescription', 'IsExcluded' 'SportEventStagingId', 'IsChecked', 'IsPPD', 'AdjWindBearing', 'AdjWindBearingDisplay', 'SelectedTeam', 'IsWeatherLevel1', 'IsWeatherLevel2', 'IsWeatherLevel3', 'WeatherIcon', 'WeatherSummary', 'EventWeather', 'EventWeatherItems', 'UseWeather', 'IsExcluded']

        games = []

        try:
            parsed = json.loads(content)

        except:
            logging.error('parser.today(): could not parse json')
            return None

        if parsed:
            for item in parsed:
                game = {k:v for k,v in item.items() if not k in omit}
                games.append(game)
            
        return games

    def model(self, content):
        '''
        Parses json associated with model (player stats / projections)

        Usage:
            model = p.model(model_json)
            model = p.model(model_json, omit_properties=[])
            model = p.model(model_json, omit_other=[])

        '''

        players = []
        omit_properties = ['IsLocked']
        omit_other = ['ErrorList', 'LineupCount', 'CurrentExposure', 'ExposureProbability', 'IsExposureLocked', 'Positions', 'PositionCount', 'Exposure', 'IsLiked', 'IsExcluded']

        try:
            parsed = json.loads(content)

        except:
            logging.error('could not parse json')

        if parsed:
            for playerdict in parsed:
                player = {}

                for k,v in playerdict.items():

                    if k == 'Properties':

                        for k2,v2 in v.items():

                            if not k2 in omit_properties:
                                player[k2] = v2

                    elif not k in omit_other:
                        player[k] = v

                players.append(player)

        return players
        

if __name__ == "__main__":
    pass
