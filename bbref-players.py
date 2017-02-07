<tr>
<th class="left " data-append-csv="bytzumi01" data-stat="player" scope="row"><a href="/players/b/bytzumi01.html">Michael Bytzura</a></th>
<td class="right " data-stat="year_min">1947</td>
<td class="right " data-stat="year_max">1947</td>
<td class="center " data-stat="pos">F</td>
<td class="right " csk="73.0" data-stat="height">6-1</td>
<td class="right " data-stat="weight">170</td>
<td class="left " csk="19220618" data-stat="birth_date"><a href="/friv/birthdays.cgi?month=6&amp;day=18">June 18, 1922</a></td>
<td class="left " data-stat="college_name"><a href="/friv/colleges.cgi?college=longisland">Long Island University</a></td>
</tr>

<tr data-row="0">
<th scope="row" class="left " data-append-csv="babbch01" data-stat="player">
<strong><a href="/players/b/babbch01.html">Chris Babb</a></strong></th>
<td class="right " data-stat="year_min">2014</td><td class="right " data-stat="year_max">2014</td>
<td class="center " data-stat="pos">G</td>
<td class="right " data-stat="height" csk="77.0">6-5</td>
<td class="right " data-stat="weight">225</td>
<td class="left " data-stat="birth_date" csk="19900214"><a href="/friv/birthdays.cgi?month=2&amp;day=14">February 14, 1990</a></td>
<td class="left " data-stat="college_name"><a href="/friv/colleges.cgi?college=iowast">Iowa State University</a></td></tr>

import logging
import random
import string
import time

from bs4 import BeautifulSoup
from ewt.scraper import EWTScraper

s = EWTScraper(cache_name='bbref-players')
base_url = 'http://www.basketball-reference.com/players/{}/'

players = []
for l in string.ascii_lowercase:
	try:
		content = s.get(base_url.format(l))
	except:
		continue
		
	soup = BeautifulSoup(content, 'lxml')
	t = soup.find('table', {'id': 'players'})
	tb = t.find('tbody')
	for tr in tb.find_all('tr'):
		vals = {td['data-stat']: td.text for td in tr.find_all('td')}

		th = tr.find('th')
		if th.find('strong'):
			vals['active'] = True
		else:
			vals['active'] = False

		if th.find('a'):
			a = th.find('a')
			vals['player_name'] = a.text
			vals['player_url'] = a['href']        

		players.append(vals)
	
print random.sample(players, 10)
