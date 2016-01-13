from decimal import *
import logging


class NBADailyFantasy:


    def __init__(self, **kwargs):

        logging.getLogger(__name__).addHandler(logging.NullHandler())
        getcontext().prec = 3

    def dk_points(self, player):
        '''
        Calculates draftkings NBA points, including 2x and 3x bonus
        '''

        dkpts = 0
        dkpts += player.get('pts'.upper(), 0)
        dkpts += player.get('fg3m'.upper(), 0) * .5
        dkpts += player.get('reb'.upper(), 0) * 1.25
        dkpts += player.get('ast'.upper(), 0) * 1.5
        dkpts += player.get('stl'.upper(), 0) * 2
        dkpts += player.get('blk'.upper(), 0) * 2
        dkpts += player.get('tov'.upper(), 0) * -.5

        # add the bonus
        over_ten = 0
        for cat in ['pts', 'fg3m', 'reb', 'ast', 'stl', 'blk']:
            if player.get(cat.upper(), 0) >= 10:
                over_ten += 1

        # bonus for triple double or double double
        if over_ten >= 3:
            dkpts += 3

        elif over_ten == 2:
            dkpts += 1.5

        return Decimal(dkpts)

    def fd_points(self, player):
        '''
        Calculates fanduel NBA points
        '''
    
        fd_points = 0
        fd_points += player.get('pts'.upper(), 0)
        fd_points += player.get('reb'.upper(), 0) * 1.2
        fd_points += player.get('ast'.upper(), 0) * 1.5
        fd_points += player.get('stl'.upper(), 0) * 2
        fd_points += player.get('blk'.upper(), 0) * 2
        fd_points -= player.get('tov'.upper(), 0)

        return Decimal(fd_points)

if __name__ == '__main__':
    pass
