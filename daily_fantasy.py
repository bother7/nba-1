import logging

class NBADailyFantasy:


    def __init__(self, **kwargs):

        logging.getLogger(__name__).addHandler(logging.NullHandler())

    def dk_points(self, player):
        '''
        Calculates draftkings NBA points, including 2x and 3x bonus
        '''

        dkpts = 0
        dkpts += player.get('pts', 0)
        dkpts += player.get('fg3m', 0) * .5
        dkpts += player.get('reb', 0) * 1.25
        dkpts += player.get('ast', 0) * 1.5
        dkpts += player.get('stl', 0) * 2
        dkpts += player.get('blk', 0) * 2
        dkpts += player.get('tov', 0) * -.5

        # add the bonus
        over_ten = 0
        for cat in ['pts', 'fg3m', 'reb', 'ast', 'stl', 'blk']:
            if player.get(cat) >= 10:
                over_ten += 1

        # bonus for triple double or double double
        if over_ten >= 3:
            dkpts += 3

        elif over_ten == 2:
            dkpts += 1.5

        return round(dkpts, 5)

    def fd_points(self, player):
        '''
        Calculates fanduel NBA points
        '''

        fd_points = 0
        fd_points += player.get('pts', 0)
        fd_points += player.get('reb', 0) * 1.2
        fd_points += player.get('ast', 0) * 1.5
        fd_points += player.get('stl', 0) * 2
        fd_points += player.get('blk', 0) * 2
        fd_points -= player.get('tov', 0)

        return round(fd_points, 5)

if __name__ == '__main__':
    pass
