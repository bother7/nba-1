'''
espn-nba-players.py
'''
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import json
import os.path
import pprint
import re
import requests
import requests_cache
import socks
import socket
import time

from EWTScraper import EWTScraper


def player_page(content):

    # <td align="left"><a href="http://espn.go.com/nba/player/_/id/110/kobe-bryant">Kobe Bryant</a>

    players = {}
    soup = BeautifulSoup(content)
    pattern = re.compile('player/_/id/(\d+)/(\w+[^\s]*)', re.IGNORECASE)
    links = soup.findAll('a', href=pattern)

    for link in links:
        match = re.search(pattern, link['href'])

        if match:
            players[match.group(1)] = match.group(2)

        else:
            print 'could not get {0}'.format(link['href'])

    return players

def simscores(player_code):
    s = EWTScraper()
    url = 'http://projects.fivethirtyeight.com/carmelo/{0}.json'.format(player_code)
    content = None
    from_cache = False

    try:
        r = requests.get(url)

        if r.status_code == requests.codes.ok:
            content = r.text
            from_cache = r.from_cache

    except requests.exceptions.RequestException as e:
        print e

    return content, from_cache

def espn_player_ids():

    # this is a list of lists
    all_players = {}

    s = EWTScraper()
    page_numbers = range(1,11)

    for page_number in page_numbers:
        url = 'http://espn.go.com/nba/salaries/_/page/{0}/seasontype/1'.format(page_number)
        content = s.get(url)
        players = player_page(content)
        for id, name in players.items():
            all_players[id] = name

    with open('espn-nba-players.json', 'w') as outfile:
        json.dump(all_players, outfile, indent=4, sort_keys=True)

    return all_players

def fivethirtyeight_nba():

    # get player_ids
    with open('/home/sansbacon/PycharmProjects/untitled/espn-nba-players.json', 'r') as infile:
        espn_players = json.load(infile)

    for player_code in espn_players.values():
        player_code = re.sub('[.\']', '', player_code)
        fn = '/home/sansbacon/538/{0}.json'.format(player_code)

        if os.path.isfile(fn):
            print 'already have {0}'.format(fn)

        else:
            if len(player_code) > 3:
                content, from_cache = simscores(player_code)

                if content:
                    with open(fn, 'w') as outfile:
                        outfile.write(content)
                else:
                    print 'could not get {0}'.format(player_code)

                if from_cache:
                    print 'got url from cache'

                else:
                    time.sleep(2)

            else:
                print 'could not get {0}'.format(player_code)

def main():
    socks.set_default_proxy(socks.SOCKS5, "localhost", 9050)
    t.socket = socks.socksocket
    requests_cache.install_cache('carmelo_cache')
    fivethirtyeight_nba()

if __name__ == '__main__':
    main()