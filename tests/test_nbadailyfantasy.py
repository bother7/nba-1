from nba.daily_fantasy import NBADailyFantasy
import unittest

class NBADailyFantasy_test(unittest.TestCase):

    def setUp(self):
        self.df = NBADailyFantasy()
        self.valid_player = {'pts': 20, 'fg3m': 0, 'reb': 10, 'ast': 0, 'stl': 0, 'blk': 0, 'tov': 0}
        self.invalid_player = {'pts': 'XX', 'fg3m': 0, 'reb': 10, 'ast': 0, 'stl': 0, 'blk': 0, 'tov': 0}

    def test_dk_points (self):
        dkpts = self.df.dk_points(self.valid_player)
        self.assertTrue(dkpts == 34)
        
    def test_fd_points(self):
        fdpts = self.df.fd_points(self.valid_player)
        self.assertTrue(fdpts == 32)

if __name__=='__main__':
    unittest.main()
