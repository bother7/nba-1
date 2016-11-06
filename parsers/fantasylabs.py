import logging


class FantasyLabsNBAParser(object):
    '''
    FantasyLabsNBAParser

    Usage:
        p = FantasyLabsNBAParser()
        games = p.games(games_json)
        model = p.model(model_json)

        for model_json in models:
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

        for item in content:
            game = {k:v for k,v in item.items() if not k in omit}
            games.append(game)
            
        return games


    def model(self, content, site, gamedate):
        '''
        Parses json associated with model (player stats / projections)
        The model has 3 dicts for each player: DraftKings, FanDuel, Yahoo
        SourceIds: 4 is DK, 11 is Yahoo, 3 is FD

        Arguments:
            model_day: list of dict representing player model

        Returns:
            players: list of parsed models
            
        Usage:
            model = p.model(content)
            model = p.model(content, omit_properties=[])
            model = p.model(content, omit_other=[])

        '''

        players = {}
        omit_properties = ['IsLocked']
        omit_other = ['ErrorList', 'LineupCount', 'CurrentExposure', 'ExposureProbability', 'IsExposureLocked', 'Positions', 'PositionCount', 'Exposure', 'IsLiked', 'IsExcluded']

        if content:
            for md in content.get('PlayerModels'):
                player = {'site': site, 'gamedate': gamedate}

                for k,v in md.items():

                    if k == 'Properties':

                        for k2,v2 in v.items():

                            if not k2 in omit_properties:
                                player[k2] = v2

                    elif not k in omit_other:
                        player[k] = v

                # test if already have this player
                # use list where 0 index is DK, 1 FD, 2 Yahoo
                pid = player.get('PlayerId', None)
                pid_players = players.get(pid, [])
                pid_players.append(player)
                players[pid] = pid_players

        if site:
            site_players = []
            
            site_ids = {'dk': 4, 'fd': 3, 'yahoo': 11}               

            for pid, player in players.items():
                for p in player:
                    if p.get('SourceId', None) == site_ids.get(site, None):
                        site_players.append(p)

            players = site_players
        
        return players

if __name__ == "__main__":
    pass
