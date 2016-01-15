#!/usr/bin/python
#nbacom-bootstrap.py

'''
This commandline script should take various parameters and then do the bootstrap using NBAComScraper
arguments:
--start_date
--end_date
--all
--boxscores
--games
'''

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--verbosity", help="increase output verbosity")
parser.parse_args()

  def bootstrap (self, **kwargs):

    # takes up to 2 dates: d1 = newest date, d2 = oldest date
    # default starting point is yesterday
    # default ending point is the start of the season
    if 'd1' in kwargs:
      d1 = kwargs['d1']
    else:
      d1 = date.today() - timedelta(days=1)

    if 'd2' in kwargs:
      d2 = kwargs['d2']
    else:
      d2 = self.season_starts

    # returns player_boxes and team_boxes
    player_boxes = []
    team_boxes = []

    # now loop through each day in the range
    for day in self._date_list(d1,d2):

      # convert date object to YYYY-MM-DD format
      game_date = date.strftime(day, "%Y-%m-%d")

      # get list of games from box page
      game_headers, standings = self.scoreboard(game_date)

      try:
        for game in game_headers:
           # two lists of boxes: players and teams
           players, teams = self.boxscore(game_id=game['GAME_ID'],game_date=game_date)
           player_boxes.append(players)
           team_boxes.append(teams)
           sleep(self.delay)

        else:
          self.logger.info("no games on %s" % game_date)

      except:
        self.logger.exception('bootstrap failed')

    return player_boxes, team_boxes

