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

        site = 'dk'
        wanted = ['Score', 'Player_Name', 'Position', 'Team', 'Ceiling', 'Floor', 'Salary', 'AvgPts', 'p_own', 'PlayerId']
        salaries = [{k:v for k,v in p.items() if k in wanted} for p in self.model(content, site=site, gamedate=day)]

        # add columns to ease insertion into salaries table
        for idx, salary in enumerate(salaries):
            fx = {'source': 'fantasylabs', 'dfs_site': site, 'game_date': day}
            fx['source_player_id'] = salary.get('PlayerId')
            fx['source_player_name'] = salary.get('Player_Name')
            fx['salary'] = salary.get('Salary')
            fx['team_code'] = salary.get('Team')
            fx['dfs_position'] = salary.get('Position')
            salaries[idx] = fx

        return salaries


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


    def model(self, content, site, gamedate):
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
        players = {}
        omit_properties = ['IsLocked']
        omit_other = ['ErrorList', 'LineupCount', 'CurrentExposure', 'ExposureProbability', 'IsExposureLocked', 'Positions', 'PositionCount', 'Exposure', 'IsLiked', 'IsExcluded']

        if content:
            for md in content.get('PlayerModels'):
                player = {'site': site, 'gamedate': gamedate}

                for k,v in list(md.items()):

                    if k == 'Properties':

                        for k2,v2 in list(v.items()):

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

            for pid, player in list(players.items()):
                for p in player:
                    if p.get('SourceId', None) == site_ids.get(site, None):
                        site_players.append(p)

            players = site_players
        
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
