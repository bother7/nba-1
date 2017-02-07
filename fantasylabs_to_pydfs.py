

def make_player(p, weights=[.6,.3,.1]):
    name = p.get('Player_Name')
    if name and ' ' in name:
        first, last = name.split(' ')[0:2]
    else:
        first = name
        last = None      
    mean = p.get('AvgPts')
    floor = p.get('Floor')
    ceiling = p.get('Ceiling')
    fppg = mean * weights[0] + ceiling * weights[1] + floor * weights[2]
    
    return Player(
                    '',
                    first,
                    last,
                    p.get('Position').split('/'),
                    p.get('Team'),
                    float(p.get('Salary', 0)),
                    fppg
                )

def run():
    opt_players = [make_player(p) for p in players]

if __name__ == '__main__':
    pass
