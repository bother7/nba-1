'''
nbacom_yearly_stats.py
gets yearly stats from nba.com or file
returns list of player dictionaries
'''

import json
import pprint
import sys

def main():
    players = []

    if len(sys.argv) > 1:

        for year in ['2013', '2014', '2015']:
            base_fn = sys.argv[1]

            with open('{0}{1}.json'.format(base_fn, year), 'r') as infile:
                parsed = json.load(infile)

            results = parsed['resultSets'][0]

            headers = [h.lower() for h in results['headers']]

            for result in results['rowSet']:
                player = dict(zip(headers, result))
                player['season'] = year
                players.append(player)

    else:
        raise ValueError('must specify filename')

    pprint.pprint(players)

if __name__ == '__main__':
    main()
