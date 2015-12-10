import json
import sys
sys.path.append("/home/sansbacon/workspace/nbacom-python/lib")
from NBAMongo import NBAMongo
import ming
import unittest

class NBAMongo_test(unittest.TestCase):

  # changed NBAMongo class to require passing a db object
  # this allows testing using ming in-memory instance
  # still need a better way of having test data, probably should just pickle some examples and load them in tests

  def setUp(self):
    self.mg = ming.create_datastore('mim://', db='nba', **kwargs)
    self.nbam = NBAMongo(self.mg.db)
    self.games = []
    self.standings = []
    self._get_scoreboard()

  def test_add_games(self):
    ids = self.nbam.add_games(self.games)
    self.assertGreater(ids.count, 0, "should have some ids after insert")

  def test_get_games(self):
    games = self.nbam.get_games()
    self.assertGreater(games.count, 0, "should have some games after query")

  '''
  def test_get_games(self):
    #,**kwargs):
    pass


  def test_add_standings(self):
    #,documents,collection_name='standings'):
    pass


  def test_get_standings(self):
    #,**kwargs):
    pass


  def test_add_player_boxscores(self):
    #,documents,collection_name='player_boxscores'):
    pass


  def test_get_player_boxscores(self):
    #,**kwargs):
    pass


  def test_add_team_boxscores(self):
    #,documents,collection_name='team_boxscores'):
    pass


  def test_get_team_boxscores(self):
    #,**kwargs):
    pass


  def test_add_playerstats(self):
    #,documents,collection_name='playerstats'):
    pass


  def test_get_playerstats(self):
    #,**kwargs):
    pass


  def test_add_players(self):
    #,documents,collection_name='players'):
    pass


  def test_get_players(self):
    #,**kwargs):
    pass

  def test_add_scoreboards(self):
    #,documents,collection_name='scoreboards'):
    pass

  def test_get_scoreboards(self):
    #,**kwargs):
    pass

  def test_add_player_gamelogs(self):
    #,documents,collection_name='player_gamelogs'):
    pass

  def test_get_player_gamelogs(self):
    #,**kwargs):
    pass

  def test_add_team_gamelogs(self):
    #,documents,collection_name='team_gamelogs'):
    pass

  def test_get_team_gamelogs(self):
    #,**kwargs):
    pass

  '''

  def _get_scoreboard(self):
    fn = '/home/sansbacon/workspace/nbacom-python/data/scoreboards/2015-01-24_scoreboard.json'
    json_data = open(fn)
    scoreboard = json.load(json_data)

    for row_set in scoreboard['resultSets'][0]['rowSet']:
      self.games.append(dict(zip(scoreboard['resultSets'][0]['headers'], row_set)))

    for row_set in parsed['resultSets'][4]['rowSet']:
      self.standings.append(dict(zip(parsed['resultSets'][4]['headers'], row_set)))

    for row_set in parsed['resultSets'][5]['rowSet']:
      standings.append(dict(zip(parsed['resultSets'][5]['headers'], row_set)))

    return self.games, self.standings

if __name__=='__main__':
  unittest.main()
