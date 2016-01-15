import sys
sys.path.append("/home/sansbacon/workspace/nbacom-python/lib")
from NBADailyFantasy import NBADailyFantasy
import unittest

class NBADailyFantasy_test(unittest.TestCase):

  def setUp(self):
    self.first_name = 'Eric'

  def test_attr(self):
    self.assertEqual(self.first_name, 'Eric', 'name should be the same')
    self.assertNotEqual(self.first_name, 'Walter', 'name should not be the same')


  def test_draftkings_fantasy_points (self):
    #, players):

  def test_dk_bonus(self):
    #,player):

if __name__=='__main__':
  unittest.main()
