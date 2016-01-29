import logging
import os
import pprint
import sys
sys.path.append("/home/sansbacon/workspace/nbacom-python/lib")
from NBAComParser import NBAComParser
import unittest

class NBAComScraper_test(unittest.TestCase):

  def setUp(self):
    self.logger = logging.getLogger()
    self.logger.setLevel(logging.WARN)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    self.logger.addHandler(ch)
    self.nbp = NBAComParser()

  def team_game_logs_data(self,fn='team_game_logs.json'):
    return self._get_from_file(fn)

  def test_team_game_logs(self):
    tgl = self.nbp.team_game_logs(self.team_game_logs_data())
    self.assertIn('Game_ID', tgl[0], "team game log should have Game_ID")

  def boxscore_data(self,fn='boxscore.json'):
    return self._get_from_file(fn)

  def test_boxscore(self):
    #self, game_id, game_date='', season='2014-15'):
    players, teams = self.nbp.boxscore(self.boxscore_data(),game_date='1-25-15')
    self.assertIn('MIN_PLAYED', players[0], "players should have min_played")
    self.assertIn('MIN_PLAYED', players[8], "players should have min_played")
    self.assertIn('MIN', teams[0], "teams should have min")
    self.assertIn('MIN', teams[1], "teams should have min")
    #self.logger.info(pprint.pprint(players))
    #self.logger.info(pprint.pprint(teams))

  def player_stats_data(self,fn='player_stats.json'):
    return self._get_from_file(fn)

  def test_player_stats(self):
    #self, game_id, game_date='', season='2014-15'):
    players = self.nbp.player_stats(self.player_stats_data(),stat_date='1-25-15')
    self.assertIn('MIN_PLAYED', players[0], "players should have min_played")

  def player_info_data(self,fn='player_info.json'):
    return self._get_from_file(fn)

  def test_player_info(self):
    info = self.nbp.player_info(self.player_info_data())
    self.assertIn('LAST_NAME', info, "info should have last name")

  def player_game_logs_data(self,fn='player_gamelogs.json'):
    return self._get_from_file(fn)

  def test_player_game_logs(self):
    gl = self.nbp.player_gamelogs(self.player_game_logs_data(), season='2014-15')
    self.assertIn('Game_ID', gl[0], "game_logs should have game_id")

  def player_data(self,fn='players.json'):
    return self._get_from_file(fn)

  def test_players(self):
    p = self.nbp.players(self.player_data())
    self.assertIn('PERSON_ID', p[0], "player should have person_id")

  def scoreboard_data(self,fn='scoreboard.json'):
    return self._get_from_file(fn)

  def test_scoreboard(self):
    # {'date': game_date, 'game_headers': game_headers, 'standings': standings}
    s = self.nbp.scoreboard(self.scoreboard_data())
    self.assertIn('GAME_ID', s['game_headers'][0], "game should have game_id")
    self.assertIn('HOME_RECORD', s['standings'][0], "standings should have home record")

  def player_data(self,fn='players.json'):
    return self._get_from_file(fn)

  def test_players(self):
    p = self.nbp.players(self.player_data())
    self.assertIn('PERSON_ID', p[0], "player should have person_id")

  def _get_from_file(self, fn):
    # content is none if file does not exist
    content = None

    # test if file exists, if so, slurp it into content
    if os.path.isfile(fn):
      self.logger.debug(fn)

      try:
        with open(fn) as x:
          content = x.read()

      except:
        self.logger.exception('could not read from file ' + fn)

    return content

if __name__=='__main__':
  unittest.main()