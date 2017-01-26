from __future__ import print_function
import time

from nba.scrapers.nbacom import NBAComScraper
from nba.parsers.nbacom import NBAComParser
from nba.db.nbacom import NBAComPg

s = NBAComScraper(cache_name='nbacom-players')
p = NBAComParser()
db = NBAComPg(username='postgres', password='cft091146', database='nba')
wanted = ['PERSON_ID', 'DRAFT_YEAR', 'DRAFT_NUMBER', 'DRAFT_ROUND'] 

with open('/home/sansbacon/fixed-ids.txt', 'r') as infile:
	fixed = [int(l.strip()) for l in infile.readlines()]

min_season = 2000
max_season = 2009

# step one: get a list of ids to update
q = """SELECT * FROM stats.draft_ids where season >= {} AND season <= {}"""

# step two: iterate through list
sqlstr = """UPDATE stats.players SET draft_year={0}, draft_number={1}, draft_round={2} WHERE nbacom_player_id={3};"""

with open('/home/sansbacon/player-update.sql', 'w') as outfile:         
	for pid in db.select_dict(q.format(min_season, max_season)):
		if pid.get('pid') in fixed:
			continue
		pl = p.player_info(s.player_info(pid.get('pid'), '2016-17'))
		pi = {k.lower(): v for k,v in pl.items() if k in wanted}
		time.sleep(.5)
		
		if pi.get('draft_year', None) == 'Undrafted' or pi.get('draft_year', None) == None:
			print('skipped player - nothing to update')
			continue
		else:
			print(sqlstr.format(pi.get('draft_year'), pi.get('draft_number'),
							pi.get('draft_round'), pi.get('person_id')), file=outfile)
			print(sqlstr.format(pi.get('draft_year'), pi.get('draft_number'),
							pi.get('draft_round'), pi.get('person_id')))

		fixed.append(pi.get('person_id'))

with open('/home/sansbacon/fixed-ids.txt', 'aw') as outfile:
	try:
		print('\n'.join([str(f) for f in fixed]), file=outfile)
	except:
		print(fixed)
