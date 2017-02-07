import logging
import re
import time

from bs4 import BeautifulSoup
from fuzzywuzzy import process

from ewt.scraper import EWTScraper
from nba.db.nbacom import NBAComPg

s = EWTScraper(cache_name='espn-nba')
db = NBAComPg(username='postgres', password='cft091146', database='nba')

teams_page = 'http://www.espn.com/nba/teams'
ep = []
et = {}

tpcontent = s.get(teams_page)
soup = BeautifulSoup(tpcontent, 'lxml')

for teama in soup.find_all('a', {'href': re.compile(r'/nba/teams/roster')}):
	roster_url = 'http://espn.go.com' + teama['href']
	team_code = roster_url.split('=')[-1]
	et[team_code] = {'url': roster_url, 'name': teama.text} 

	content = s.get(roster_url)
	tsoup = BeautifulSoup(content, 'lxml')
	
	for tr in tsoup.find_all('tr', {'class': re.compile(r'player-\d+')}):
	
		# get player name and id
		espn_player_id, espn_player_url = (None, None)
		links = [td.find('a') for td in tr.find_all('td') if td.find('a')]
		if links:
			url = links[0]['href']
			if url:
				espn_player_url = url
				match = re.search(r'/id/(\d+)/(\w+-\w+)', url)
				if match:                            
					espn_player_id = match.group(1)

		# 0 jersey, 1 name, 2 position, 3 age, 4 height, 5 weight, 6 college, 7 salary
		headers = ['jersey', 'espn_player_name', 'espn_position', 'age', 'height', 'weight', 'college', 'nba_salary']
		tds = [td.text for td in tr.find_all('td')]
		player = dict(zip(headers, tds))
		player['espn_player_url'] = espn_player_url
		player['espn_player_id'] = espn_player_id
		ep.append(player)
	
choices = [p.get('espn_player_name') for p in ep]
espn_players = {p.get('espn_player_name'):p for p in ep}
q = 'select * from stats.posnull'
uq = """UPDATE stats.players2 SET primary_position = '{}' WHERE nbacom_player_id = {};"""
for p in db.select_dict(q):
    match, perc = process.extractOne(p.get('display_first_last'), choices)
    if perc >= 90:
		pos = espn_players.get(match).get('espn_position')
		pid = p.get('nbacom_player_id')
		print uq.format(pos, int(pid))
        
