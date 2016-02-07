from __future__ import division
import logging
import pprint

import pandas as pd

from nba.parsers.fantasy_labs import FantasyLabsNBAParser
from nba.scrapers.fantasy_labs import FantasyLabsNBAScraper
from nba.agents.agent import NBAAgent


class FantasyLabsNBAAgent(NBAAgent):
    '''
    Performs script-like tasks using rotoguru scraper and parser
    Intended to replace standalone scripts so can use common API and tools

    Examples:
        a = FantasyLabsNBAAgent()

    '''

    def __init__(self, **kwargs):
        logging.getLogger(__name__).addHandler(logging.NullHandler())

        self.scraper = FantasyLabsNBAScraper()
        self.parser = FantasyLabsNBAParser()

        # see http://stackoverflow.com/questions/8134444
        NBAAgent.__init__(self, **kwargs)

    def today_models(self, **kwargs):
        model = self.scraper.model()
        players = self.parser.model(model, 'dk')
        savecols = [u'Player_Name', u'TeamName', u'FirstPosition', u'MinutesProj', u'Salary', u'AvgPts', u'Floor', u'Ceiling']
        getcols = ['name', 'position', 'salary', 'projection']
        filtered = [{k.lower():v for k,v in p.items() if k in savecols} for p in players]

        for f in filtered:
            ceiling = f.get('ceiling', None)
            floor = f.get('floor', None)
            avgpts = f.get('avgpts', None)

            if not ceiling >= 0: ceiling = 0
            if not floor >= 0: floor = 0
            if not avgpts >= 0: avgpts = 0

            f['projection'] = (ceiling * .75) + (floor * .1) + (avgpts * .15)
            f['name'] = f['player_name'].replace("'","").strip()
            f['position'] = f['firstposition']

            if not f.get('projection', None):
                f['projection'] = 0

        frame = pd.DataFrame(filtered)
        players = frame.loc[:,getcols].sort_values('projection', ascending=False)
        players.to_csv('players-upside.csv', index=False)

        frame['projection'] = frame.get('ceiling', 0) * .1 + frame.get('floor', 0) * .1 + frame.get('avgpts', 0) * .8
        players = frame.loc[:,getcols].sort_values('projection', ascending=False)
        players.to_csv('players-floor.csv', index=False)

if __name__ == '__main__':
    pass
