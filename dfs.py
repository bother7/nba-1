import logging

logger = logging.getLogger(__name__)


def dk_points(player):
    '''
    Calculates draftkings NBA points, including 2x and 3x bonus

    Arguments:
        player(dict): has pts, reb, etc.

    Returns:
        float: number of draftkings points scored by the player

    '''
    cleaned_player = {k.lower(): v for k,v in player.items()}
    dkpts = 0
    dkpts += cleaned_player.get('pts', 0)
    dkpts += cleaned_player.get('fg3m', 0) * .5
    dkpts += cleaned_player.get('reb', 0) * 1.25
    dkpts += cleaned_player.get('ast', 0) * 1.5
    dkpts += cleaned_player.get('stl', 0) * 2
    dkpts += cleaned_player.get('blk', 0) * 2
    dkpts += cleaned_player.get('tov', 0) * -.5

    # add the bonus
    over_ten = 0
    for cat in ['pts', 'fg3m', 'reb', 'ast', 'stl', 'blk']:
        if cleaned_player.get(cat) >= 10:
            over_ten += 1
    # bonus for triple double or double double
    if over_ten >= 3:
        dkpts += 4.5
    elif over_ten == 2:
        dkpts += 1.5

    return round(dkpts, 5)


def fd_points(player, new_scoring=True):
    '''
    Calculates fanduel NBA points

    Arguments:
        player(dict): has pts, reb, etc.

    Returns:
        fd_pts(float): number of fanduel points

    '''

    # fanduel adopted nba.com scoring for the 2017-18 season
    fd_points = 0
    if new_scoring:
        fd_points += player.get('pts', 0)
        fd_points += player.get('reb', 0) * 1.2
        fd_points += player.get('ast', 0) * 1.5
        fd_points += player.get('stl', 0) * 3
        fd_points += player.get('blk', 0) * 3
        fd_points -= player.get('tov', 0)
    else:
        fd_points += player.get('pts', 0)
        fd_points += player.get('reb', 0) * 1.2
        fd_points += player.get('ast', 0) * 1.5
        fd_points += player.get('stl', 0) * 2
        fd_points += player.get('blk', 0) * 2
        fd_points -= player.get('tov', 0)

    return round(fd_points, 5)


if __name__ == '__main__':
    pass
