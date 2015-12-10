import json
import logging
from math import modf
import pprint
import re


class NBAComParser:
    '''
    Parses json endpoints of stats.nba.com into lists of dictionaries

    Usage:
        s = NBAComScraper()
        jsondoc = s.player_stats()
        p = NBAComParser()
        stats = p.player_stats(jsondoc)

        content = s.teams()
        teams = p.teams(content)

    '''

    def __init__(self, **kwargs):

        logging.getLogger(__name__).addHandler(logging.NullHandler())

    def boxscore(self, content, game_date=None):

        players = []
        teams = []

        try:
            parsed = json.loads(content)
            player_results, team_results = parsed['resultSets']

            # do players first
            # add game_date for convenience
            # standardize on TOV rather than TO; playerstats uses TOV
            for row_set in player_results['rowSet']:
                player = dict(zip(player_results['headers'], row_set))

                if game_date:
                    player['GAME_DATE'] = game_date

                if 'MIN' in player:
                    player['MIN_PLAYED'], player['SEC_PLAYED'] = player['MIN'].split(':')

                if 'TOV' in player:
                    player['TOV'] = player.pop('TO')

                players.append(player)

            # now do teams
            # add game_date for convenience
            for result in team_results['rowSet']:
                team = dict(zip(team_results['headers'], result))

                if game_date:
                    team['GAME_DATE'] = game_date

                teams.append(team)

        except:
            logging.exception('boxscore failed')

        # ship it
        return players, teams

    def leaguegamelog_players(self, content):
        '''
        URL: http://stats.nba.com/stats/leaguegamelog?Direction=DESC&Season=2015-16&Counter=0&Sorter=PTS&
        LeagueID=00&PlayerOrTeam=P&SeasonType=Regular+Season
        '''
        player_games = []

        try:
            parsed = json.loads(content)
            result_set = parsed['resultSets'][0]
            headers = [h.lower() for h in result_set['headers']]

            for row_set in result_set['rowSet']:
                player_game = dict(zip(headers,row_set))
                player_games.append(player_game)

        except:
            logging.exception('leaguegamelog_players failed')

        return player_games

    def player_game_logs(self,content,player_info=None,season=None):

        player_gl =[]

        try:
            parsed = json.loads(content)
            result_set = parsed['resultSets'][0]

            for row_set in result_set['rowSet']:
                game_log = dict(zip(result_set['headers'], row_set))

                # add season & year to player_game_logs
                if season:
                    game_log['SEASON'] = season
                    game_log['YEAR'] = season.split("-")[0]

                # add info from commonplayerinfo to player_game_logs
                if player_info:
                    if 'DISPLAY_FIRST_LAST' in player_info:
                        game_log['DISPLAY_FIRST_LAST'] = player_info['DISPLAY_FIRST_LAST']

                    if 'DISPLAY_LAST_COMMA_FIRST' in player_info:
                        game_log['DISPLAY_LAST_COMMA_FIRST'] = player_info['DISPLAY_LAST_COMMA_FIRST']

                    if 'DISPLAY_FI_LAST' in player_info:
                        game_log['DISPLAY_FI_LAST'] = player_info['DISPLAY_FI_LAST']

                player_gl.append(game_log)
                logging.debug(game_log)

        except:
            logging.exception('player_game_logs failed')

        # ship it
        return player_gl

    def player_info(self,content):

        player_info = None

        try:
            parsed = json.loads(content)
            result_set = parsed['resultSets'][0]
            player_info = dict(zip(result_set['headers'],result_set['rowSet'][0]))

        except:
            logging.exception('player_game_logs failed')

        return player_info

    def player_stats(self,content,stat_date=None):

        ps = []

        # now parse, return list of dictionaries which represent players
        try:
            parsed = json.loads(content)
            result_set = parsed['resultSets'][0]

            for row_set in result_set['rowSet']:
                p = dict(zip(result_set['headers'], row_set))

                if stat_date:
                    p['STATDATE'] = stat_date

                if 'MIN' in p:
                    p['SEC_PLAYED'], p['MIN_PLAYED'] = modf(p['MIN'])

                ps.append(p)

        except:
            logging.exception('player_stats failed')

        return ps

    def players (self,content):

        p = []

        try:
            parsed = json.loads(content)
            result_set = parsed['resultSets'][0]

            for row_set in result_set['rowSet']:
                p.append(dict(zip(result_set['headers'], row_set)))

        except:
            logging.exception('players failed')

        return p

    def scoreboard(self,content,game_date=None):
        '''
        returns {'date': game_date,
        'game_headers': game_headers.values(),
        'game_linescores': game_linescores,
        'standings': standings}
        '''
        game_headers = {}
        game_linescores = []
        standings = []

        # now do something with the content
        # want to get game_headers, east_standings, and west_standings
        parsed = None

        try:
            parsed = json.loads(content)

        except Exception, e:
            logging.exception('scoreboard failed: %s' % e)

        if parsed:

            # resultSets[0] is a list of games, with game_id, gamecode, teams, etc.
            for row_set in parsed['resultSets'][0]['rowSet']:
                game_header = dict(zip(parsed['resultSets'][0]['headers'], row_set))
                gamecode = game_header.get('GAMECODE', None)

                if gamecode:
                    game_headers[gamecode] = game_header
                else:
                    logging.error('no gamecode')

            # resultSets[1] are the game_linescores (includes results on a team-by-team, game-by-game basis)
            for row_set in parsed['resultSets'][1]['rowSet']:
                linescore_headers = [h.lower() for h in parsed['resultSets'][1]['headers']]
                linescore = dict(zip(linescore_headers, row_set))
                game_linescores.append(linescore)

            # resultSets[4] is a list of eastern_conference_standings
            for row_set in parsed['resultSets'][4]['rowSet']:
                standings.append(dict(zip(parsed['resultSets'][4]['headers'], row_set)))

            # resultSets[5] is a list of western_conference_standings
            for row_set in parsed['resultSets'][5]['rowSet']:
                standings.append(dict(zip(parsed['resultSets'][5]['headers'], row_set)))

            return {'date': game_date, 'game_headers': game_headers.values(), 'game_linescores': game_linescores, 'standings': standings}

        else:
            return parsed

    def season_gamelogs(self,content,season,player_or_team):

        gamelogs =[]

        if player_or_team == 'T':

            try:
                parsed = json.loads(content)

            except:
                pass

            if parsed:
                results = parsed['resultSets'][0]
                headers = [h.lower() for h in results['headers']]

                for result in results['rowSet']:
                    gamelog = dict(zip(headers, result))
                    gamelog['season'] = season

                    # add opponent_score
                    points = gamelog.get('pts', None)
                    plus_minus = gamelog.get('plus_minus', None)

                    if points and plus_minus:
                        gamelog['opponent_pts'] = points - plus_minus

                    # add away/home teams, 3 fields
                    pattern = re.compile(r'([A-Z]+)\s+[@|vs\.]+\s+([A-Z]+)')
                    match = re.search(pattern, gamelog['matchup'])

                    if match:
                        gamelog['away_team_abbreviation'] = match.group(1)
                        gamelog['home_team_abbreviation'] = match.group(2)

                        if gamelog['away_team_abbreviation'] == gamelog['team_abbreviation']:
                            gamelog['home_away'] = 'A'

                        elif gamelog['home_team_abbreviation'] == gamelog['team_abbreviation']:
                            gamelog['home_away'] = 'H'

                    gamelogs.append(gamelog)

        return gamelogs

    def team_dashboard(self, content):
        '''
        Dashboard has keys: parameters, overall, location, days_rest, wins_losses
        The value of each key is a list of dictionaries
        parameters: 1 item in list
        overall: 1 item in list
        location: 2 items - home and away
        days_rest: multiple items that vary - 0 days, 1 day, 2 days, 3 days, 4 days
        wins_losses: 2 items - wins and losses
        '''

        dashboard = {'parameters': [], 'overall': [], 'location': [], 'days_rest': [], 'wins_losses': []}

        try:
            parsed = json.loads(content)
            dashboard['parameters'] = parsed['parameters']

            for result_set in parsed['resultSets']:
                logging.debug('result_set name: {0}'.format(result_set['name']))

                if result_set['name'] == 'OverallTeamDashboard':
                    headers = result_set['headers']

                    for row_set in result_set['rowSet']:
                        result = dict(zip(headers, row_set))
                        dashboard['overall'].append(result)

                elif result_set['name'] == 'LocationTeamDashboard':
                    for row_set in result_set['rowSet']:
                        result = dict(zip(headers, row_set))
                        dashboard['location'].append(result)

                elif result_set['name'] == 'DaysRestTeamDashboard':
                    for row_set in result_set['rowSet']:
                        result = dict(zip(headers, row_set))
                        dashboard['days_rest'].append(result)

                elif result_set['name'] == 'WinsLossesTeamDashboard':
                    for row_set in result_set['rowSet']:
                        result = dict(zip(headers, row_set))
                        dashboard['wins_losses'].append(result)

        except Exception as e:
            logging.exception('team_dashboard failed')

        return dashboard

    def team_game_logs(self,content,season=None):
        '''

        '''
        team_gl =[]

        try:
            parsed = json.loads(content)
            result_set = parsed['resultSets'][0]

            for row_set in result_set['rowSet']:
                game_log = dict(zip(result_set['headers'], row_set))

                if season:
                    game_log['SEASON'] = season
                    game_log['YEAR'] = season.split("-")[0]

                team_gl.append(game_log)

        except:
            logging.exception('team_game_logs failed')

        return team_gl

    def team_opponent_dashboard(self, content):
        '''
        Returns list of dictionaries, stats of opponents vs. each team
        '''

        teams = []

        try:
            parsed = json.loads(content)
            result_set = parsed['resultSets'][0]
            headers = [h.lower() for h in result_set['headers']]

            for row_set in result_set['rowSet']:
                teams.append(dict(zip(headers, row_set)))

        except Exception as e:
            logging.exception('team_opponent_dashboard failed')

        return teams

    def team_stats(self,content,stat_date=None):

        ts = []

        # now parse, return list of dictionaries which represent players
        try:
            parsed = json.loads(content)
            result_set = parsed['resultSets'][0]

            for row_set in result_set['rowSet']:
                t = dict(zip(result_set['headers'], row_set))

                if stat_date:
                    t['STATDATE'] = stat_date

                ts.append(t)

        except Exception as e:
            logging.exception('team_stats failed: %s' % e.message)

        return ts

    def teams(self, content):
        '''
        Returns list of string - "1610612737","ATL"
        TODO: parse this into dictionaries
        '''

        teams = {}
        pattern = re.compile(r'("(\d{10})","(\w{3})"),conf')

        return {match[2]: match[1] for match in re.findall(pattern, content)}

if __name__ == "__main__":
    pass
