'''
nba-daily.py
Downloads data from nba.com and fantasylabs, updates relevant tables
'''


import logging
import random

from nba.agents.nbacom import NBAComAgent
from nba.agents.fantasylabs import FantasyLabsNBAAgent


def run():

    logging.basicConfig(level=logging.INFO)
    a = NBAComAgent(db=True, safe=False)
    fla = FantasyLabsNBAAgent(db=True, safe=False)

    # update players
    logging.info('start update players')
    a.commonallplayers('2015-16')
    logging.info('completed update players')

    # Update cs_player_gamelogs table through yesterday's games
    logging.info('start update player_gamelogs')
    a.cs_player_gamelogs('2015-16')
    logging.info('end update player_gamelogs')

    # Update cs_playerstats table through yesterday's games
    logging.info('start update playerstats')
    a.cs_playerstats('2015-16')
    logging.info('end update playerstats')

    # Update cs_team_gamelogs table through yesterday's games
    logging.info('start update team_gamelogs')
    a.cs_team_gamelogs('2015-16')
    logging.info('end update team_gamelogs')

    # Update cs_teamstats table through yesterday's games
    logging.info('start update teamstats')
    a.cs_teamstats('2015-16')
    logging.info('end update teamstats')

    # Get models and salaries from today's games
    # insert salaries into database
    logging.info('start update models')
    players, pp_players = fla.today_models(insert_db=True)
    logging.info('end update models')

    # insert models into database
    # TODO: preprocess_models + insert models code

    return players, pp_players

if __name__ == '__main__':
    players, pp_players = run()
