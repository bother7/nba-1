import logging


class FantasyLabsNBAParser(object):
    '''
    FantasyLabsNBAParser

    Usage:
        p = FantasyLabsNBAParser()
        games = p.games(games_json)
        model = p.model(model_json)
    '''

    def __init__(self):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
                        
    def dk_salaries(self, content, day):
        '''
        Gets list of salaries for one day
        Args:
            content (str):
            day(str): in mm_dd_YYYY format
        Returns:
            players (list): of player dict
        '''
        return self.model(content, site='dk', gamedate=day)

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

        for item in content:
            game = {k:v for k,v in list(item.items()) if not k in omit}
            games.append(game)
            
        return games


    def model(self, content, site='dk', gamedate=None):
        '''
        Parses dict associated with model (player stats / projections)
        The model has 3 dicts for each player: DraftKings, FanDuel, Yahoo
        SourceIds: 4 is DK, 11 is Yahoo, 3 is FD
        Arguments:
            content(dict):
            site(str):
            gamedate(str):
        Returns:
            players: list of parsed models
        Usage:
            model = p.model(content, site='dk', gamedate='1_14_2017')
        '''
        players = []

        for md in content.get('PlayerModels'):
            player = {'site': site}
            for k,v in list(md.items()):
                if k == 'Properties':
                    for k2,v2 in list(v.items()):
                        player[k2] = v2
                else:
                    player[k] = v
            if player.get('SourceId', None) == 4:
                players.append(player)
        return players

if __name__ == "__main__":
    pass
    '''
    import json
    with open('model-1_26_2017.json', 'r') as infile:
        content = json.load(infile)

    from nba.parsers.fantasylabs import FantasyLabsNBAParser
    p = FantasyLabsNBAParser()

    '''
