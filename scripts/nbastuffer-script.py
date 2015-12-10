'''
Usage:
    python nbastuffer-script.py --dir <dir> --pattern <pattern>

    optional arguments:
        -h, --help  show this help message and exit

    Example:
        python nbastuffer-script.py --dir /home/sansbacon/workspace/nba-data/nbastuffer/xlsx --pattern csv

'''

import argparse
import csv
import glob
import logging
import os
import pprint
import random

from NBAGames import NBAGames
from NBAStufferDB import NBAStufferDB
from NBAStufferParser import NBAStufferParser

if __name__ == '__main__':

    logging.basicConfig(level=logging.ERROR)
    game_pairs_ = []

    # options
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', help='Directory to glob', required=True)
    parser.add_argument('--pattern', help='File extension to search for', required=True)
    args = vars(parser.parse_args())
    dirname = args.get('dir', None)
    pattern = args.get('pattern', None)

    # games
    nbag = NBAGames()
    games = {g.get('gamecode', None): g for g in nbag.games() if g.get('gamecode', None)}
    nbaparser = NBAStufferParser(nbadotcom_games=games)

    # main loop
    if dirname and pattern and os.path.exists(dirname):
        for fn in sorted(glob.glob('{0}/*.{1}'.format(dirname, pattern)), reverse=True):
            with open(fn, 'r') as infile:
                reader = csv.reader(infile)
                rows = [row for row in reader]
                headers = nbaparser.headers(rows[0])
                game_pairs_ += nbaparser.game_pairs(rows, headers)

    # now add to database
    db = NBAStufferDB()
    db.insert_games(game_pairs_)


