import httplib2
import json
import logging
import os.path
from os.path import expanduser
from pprint import pprint
from time import sleep

# setup
logging.basicConfig(level=logging.DEBUG,
                    format='%(message)s',
                    handlers=[logging.StreamHandler()])
savedir = 'nbaplayers_json_files'
h = httplib2.Http(".cache")

# parse the player list
json_data=open('commonallplayers.json')
data = json.load(json_data)
result_set = data['resultSets'][0]
players = []
for row_set in result_set['rowSet']:
  players.append(dict(zip(result_set['headers'], row_set)))

# now get all of the player pages
base_url = 'http://stats.nba.com/stats/commonplayerinfo?PlayerID='
ids = [p['PERSON_ID'] for p in players]
for id in ids:
  
  # create url
  url = base_url + str(id)
  logging.debug('url is ' + url)
  
  # create filename
  fn = os.path.join(expanduser("~"), savedir, str(id) + '.json')
  logging.debug('filename is ' + fn)
  
  # get the resource
  resp, content = h.request(url, "GET")
  logging.debug('status is ' + str(resp.status))  

  # if request is success, then save resource to file
  if resp.status == 200:   
    try:
      with open(fn, 'w') as outfile:
        outfile.write(content)
        logging.debug('saved player ' + str(id) + ' to ' + fn)  
    except:
      logging.exception('could not save file ' + fn)

  sleep(3)
  logging.debug('sleep for 2 seconds')
