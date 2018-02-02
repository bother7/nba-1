# -*- coding: utf-8 -*-

from functools import lru_cache
from multiprocessing import Pool

import click
import numpy as np
import pandas as pd

from nba.scrapers.nbacom import NBAComScraper
from nba.parsers.nbacom import NBAComParser


@lru_cache(maxsize=None)
def load_data(per_mode, playerpool_size, lastn=0):
    '''

    Args:
        per_mode (str): 'Totals', 'PerGame', 'Per48'
        player_thresh (int): number of players in pool
        lastn (int): last number of games, default 0

    Returns:
        DataFrame

    '''
    scraper = NBAComScraper(cache_name='fbasim')
    parser = NBAComParser()
    content = scraper.playerstats(season_code='2017-18', per_mode=per_mode, lastn=lastn)
    df = pd.DataFrame(parser.playerstats(content, per_mode=per_mode))
    return df.sort_values('NBA_FANTASY_PTS', ascending=False)[0:playerpool_size]


def sim(playersdf, i, chunkn, numteams, sizeteams):
    '''
    Function to multiprocess
    '''
    size = numteams * sizeteams
    nplayers = len(playersdf)

    # preallocate teams
    teams = np.zeros((chunkn*size,14), dtype=int)

    # this assigns simID to the first column
    teams[:, 0] = i
    
    # this assigns iterID
    # will have 100 repeats of 0 through n
    teams[:,1] = np.repeat(np.arange(0,chunkn), size)

    # this assigns teamid to the third column
    # need to repeat 0-9, then tile that 100-element array n times
    teams[:,2] = np.tile(A=np.repeat(np.arange(0,sizeteams), numteams), reps=chunkn)

    # now assign players to teams
    # use size to determine the slice
    start = 0
    end = size
    for ii in range(0, chunkn):
        idx = np.random.randint(0,nplayers,size)
        teams[start:end,3:] = playersdf.values[idx,:]
        start += size
        end += size

    # setup df & columns
    groupcol = ['simID', 'iterID', 'teamID']
    wanted = ['PLAYER_ID', 'FGA', 'FGM', 'FTM', 'FG3M', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PTS']
    dfteams = pd.DataFrame(teams)
    dfteams.columns = groupcol + wanted

    # aggregates
    dfteamtot = dfteams.groupby(groupcol).aggregate({'FG3M': np.sum,
                  'AST': np.sum, 'BLK': np.sum, 'FGA': np.sum,
                  'FGM': np.sum, 'FTM': np.sum,
                  'PTS': np.sum, 'STL': np.sum,
                  'REB': np.sum, 'TOV': np.sum})
    dfteamtot['FGP'] = dfteamtot['FGM']/dfteamtot['FGA']

    # get ranks
    statcols = ['FGP', 'FTM', 'FG3M', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PTS']
    rankcols = ['{}_RK'.format(col) for col in statcols]
    for statcol, rankcol in zip(statcols, rankcols):
        if statcol == 'TOV':
            dfteamtot[rankcol] = dfteamtot.groupby('iterID').aggregate(statcol).rank(ascending=False)
        else:
            dfteamtot[rankcol] = dfteamtot.groupby('iterID').aggregate(statcol).rank()
    dfteamtot['TOT'] = dfteamtot[rankcols].sum(axis=1)
    rankcols.append('TOT')
    return dfteams.join(dfteamtot[rankcols], on=groupcol, how='left')
    

@click.command()
@click.option('--n', type=int, default=500)
@click.option('--per_mode', type=str, default='Totals')
@click.option('--playerpool_size', default=300, type=int)
@click.option('--numteams', default=10, type=int)
@click.option('--sizeteams', default=10, type=int)
def run(n, per_mode, playerpool_size, numteams, sizeteams):
    '''
    Simulate nba fantasy team, 9 cat league
    
    Args:
        n (int): number of iterations
        per_mode (str): 'Totals' or 'PerGame'
        playerpool_size (int): number of players in pool
        numteams (int): number of teams in league
        sizeteams (int): number of players on team

    Returns:
        None

    '''
    pd.set_option('display.width', 1200)
    wanted = ['PLAYER_ID', 'FGA', 'FGM', 'FTM', 'FG3M', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PTS']
    df = load_data(per_mode, playerpool_size)
    playersdf = df[wanted].astype(np.int)
    df.set_index('PLAYER_ID')

    numproc = 4
    with Pool(processes=numproc) as pool:
        interim = [pool.apply_async(sim, (playersdf, i, int(n/numproc), numteams, sizeteams))
                    for i in range(numproc)]
        results = pd.concat([result.get() for result in interim]) 
    
    simdf = df.join(results.groupby('PLAYER_ID').aggregate({'FG3M_RK': np.mean, 'AST_RK': np.mean,
                                            'BLK_RK': np.mean, 'FGP_RK': np.mean,
                                            'FTM_RK': np.mean, 'PTS_RK': np.mean,
                                            'STL_RK': np.mean, 'REB_RK': np.mean,
                                            'TOV_RK': np.mean, 'TOT': np.mean}).round(1), on='PLAYER_ID')

    rk_cols = ['FGP_RK', 'FTM_RK', 'FG3M_RK', 'REB_RK', 'AST_RK', 'STL_RK',
                'BLK_RK', 'TOV_RK', 'PTS_RK', 'TOT']

    displaycol = ['PLAYER_NAME', 'TEAM_ABBREVIATION', 'GP', 'MIN_PLAYED'] + rk_cols
    print(simdf[displaycol].sort_values('TOT', ascending=False))


if __name__ == '__main__':
    run()
