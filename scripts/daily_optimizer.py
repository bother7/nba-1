#!/usr/bin/env python
# gets model, returns optimized lineups

import logging
import os
import sys

import browsercookie
from configparser import ConfigParser

from nba.agents.fantasylabs import FantasyLabsNBAAgent
from nba.dates import today
from nba.pipelines.fantasylabs import *
from pydfs_lineup_optimizer import *


def main():

    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    config = ConfigParser()
    configfn = os.path.join(os.path.expanduser('~'), '.pgcred')
    config.read(configfn)

    cn = 'fl-agent-{}'.format(today())
    fla = FantasyLabsNBAAgent(db=None, cache_name=cn, cookies=browsercookie.firefox())
    models = fla.one_model(today(fmt='fl'), 'phan')

    optimizer = LineupOptimizer(settings.DraftKingsBasketballSettings)
    optimizer._players = fl_to_pydfs(models, weights=[.1,.6,.3])
    for lineup in optimizer.optimize(n=5):
        print lineup


if __name__ == '__main__':
    main()