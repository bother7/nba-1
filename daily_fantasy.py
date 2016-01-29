from decimal import *
import logging
import pprint

class NBADailyFantasy:


    def __init__(self, **kwargs):

        logging.getLogger(__name__).addHandler(logging.NullHandler())

    def dk_points(self, player):
        '''
        Calculates draftkings NBA points, including 2x and 3x bonus
        '''

        dkpts = Decimal(0)
        dkpts += Decimal(player.get('pts', 0))
        dkpts += Decimal(player.get('fg3m', 0) * .5)
        dkpts += Decimal(player.get('reb', 0) * 1.25)
        dkpts += Decimal(player.get('ast', 0) * 1.5)
        dkpts += Decimal(player.get('stl', 0) * 2)
        dkpts += Decimal(player.get('blk', 0) * 2)
        dkpts += Decimal(player.get('tov', 0) * -.5)

        # add the bonus
        over_ten = 0
        for cat in ['pts', 'fg3m', 'reb', 'ast', 'stl', 'blk']:
            if player.get(cat.upper(), 0) >= 10:
                over_ten += 1

        # bonus for triple double or double double
        if over_ten >= 3:
            dkpts += Decimal(3)

        elif over_ten == 2:
            dkpts += Decimal(1.5)

        return round(dkpts, 5)

    def fd_points(self, player):
        '''
        Calculates fanduel NBA points
        '''
    
        fd_points = Decimal(0)
        fd_points += Decimal(player.get('pts', 0))
        fd_points += Decimal(player.get('reb', 0) * 1.2)
        fd_points += Decimal(player.get('ast', 0) * 1.5)
        fd_points += Decimal(player.get('stl', 0) * 2)
        fd_points += Decimal(player.get('blk', 0) * 2)
        fd_points -= Decimal(player.get('tov', 0))

        return round(fd_points, 5)

if __name__ == '__main__':
    pass
