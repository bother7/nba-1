import logging

class NBADailyFantasy:

  def __init__(self,**kwargs):

    # can pass in logger, or just use package name
    if 'logger' in kwargs:
      self.logger = kwargs['logger']
    else:
      self.logger = logging.getLogger(__name__)

    # can pass in site or default to draftkings
    if 'site' in kwargs:
      self.site = kwargs['site']
    else:
      self.site = 'draftkings'

    # now set up scoring rules
    if 'scoring' in kwargs:
      self.scoring = kwargs['scoring']
    else:
      if self.site == 'draftkings':
        self.scoring = {'PTS': 1, 'FG3M': .5, 'REB': 1.25, 'AST': 1.5, 'STL': 2, 'BLK': 2, 'TOV': .5, 'DD': 1.5, 'TD': 3}
      elif self.site == 'fanduel':
        self.scoring = {'PTS': 1, 'REB': 1.2, 'AST': 1.5, 'STL': 2, 'BLK': 2, 'TOV': 1}

  def draftkings_fantasy_points (self, players):
    '''
    parameters: players
    returns: players
    adds key DK_FANTASY_PTS to player dictionary
    '''

    updated_players = []

    # loop through players
    try:
      for player in players:
        # start with zero points
        fantasy_points = 0
        self.logger.debug(player['PLAYER_NAME'])

        # go through scoring categories, multiply quantity and dk value
        for cat in ('PTS', 'FG3M', 'REB', 'AST', 'STL', 'BLK', 'TOV'):
          cat_fantasy_points = player[cat] * self.scoring[cat]
          self.logger.debug(cat + ' : ' + str(cat_fantasy_points))

          # python 2 is goofy with negatives, so this is workaround
          if cat == 'TOV':
            fantasy_points -= cat_fantasy_points
            self.logger.debug('fantasy_points are now: ' + str(fantasy_points))
          else:
            fantasy_points += cat_fantasy_points
            self.logger.debug('fantasy_points are now: ' + str(fantasy_points))

        # now see if there is a bonus for double-double or triple-double
        fantasy_points += self._dk_bonus(player)

        # assign to player and add to list
        player['DK_FANTASY_PTS'] = fantasy_points
        self.logger.debug('total fantasy_points are ' + str(fantasy_points))
        updated_players.append(player)

    except Exception, e:
      self.logger.exception('could not calculate dk fantasy points')

    # ship it
    return updated_players

  def _dk_bonus(self,player):
    # assume no bonus
    bonus = 0
    cat_10_or_more = 0

    # go through scoring categories, multiply quantity and dk value
    for cat in ('PTS', 'REB', 'AST', 'STL', 'BLK'):
      if player[cat] >= 10:
        cat_10_or_more += 1

    # check 3x, then 2x to avoid double counting
    if cat_10_or_more >= 3:
      bonus = 3
      self.logger.debug("** triple double ** " + player['PLAYER_NAME'])

    elif cat_10_or_more == 2:
      bonus = 1.5
      self.logger.debug("** double double ** " + player['PLAYER_NAME'])

    return bonus

if __name__ == '__main__':
  pass
