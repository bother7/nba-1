import httplib2
import logging
import mock
import re
import sys
sys.path.append("/home/sansbacon/workspace/nbacom-python/lib")
from NBAComScraper import NBAComScraper
import unittest

class NBAComScraper_test(unittest.TestCase):

  def setUp(self):
    self.logger = logging.getLogger(__name__)
    self.nbs = NBAComScraper()

  def tearDown(self):
    self.patcher.stop()

  def test_boxscore(self,request_mock):
    #self, game_id, game_date='', season='2014-15'):
    @patch('httplib2.request')
    request_mock.return_value = 'hello world'
    content, debug = self.nbs.boxscore()
    assert content == 'hello world'
    assert debug['game_date'] == None
    assert debug['season'] == '2014-15'

  '''
  def test_player_stats(self):
    #self,season='2014-15',per_mode='Totals',season_type='Regular Season',stat_date=None):
    pass

  def test_player_info(self):
    pass

  def test_player_game_logs(self):
    #,player_id,season='2014-15',season_type='Regular Season'):
    pass

  def test_players (self):
    #, **kwargs):
    pass

  def test_scoreboard(self):
    #, **kwargs):
    pass


  def test_team_game_logs(self):
    #,team_id,season='2014-15',season_type='Regular Season'):
    pass

  '''

if __name__=='__main__':
  unittest.main()
