# nba-daily.py

import copy
import datetime
import logging
import cPickle as pickle
import random


from nba import NBAComAgent
from nba import FantasyLabsNBAAgent

logger = logging.getLogger('__name__')
logger.setLevel(logging.DEBUG)

a = NBAComAgent(db=True, safe=False)
fla = FantasyLabsNBAAgent(db=True, safe=False)

# update players
players = a.commonallplayers('2015-16')

# Update cs_player_gamelogs table through yesterday's games
all_gamelogs = a.cs_player_gamelogs('2015-16')

# Update cs_playerstats table through yesterday's games
playerstats = a.cs_playerstats('2015-16')

# Update cs_team_gamelogs table through yesterday's games
team_gamelogs = a.cs_team_gamelogs('2015-16')

# Update cs_teamstats table through yesterday's games
teamstats = a.cs_teamstats('2015-16')

# Get models and salaries from today's games
players = fla.today_models(model_name='phan')

# insert salaries / models into database
