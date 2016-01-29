import datetime
import pymongo
from pymongo import MongoClient

class NBAMongo:

  def __init__(self, db):
    self.db = db

  ####################################################################
  # games collection - CRUD
  # each game document has GAME_DATE, GAME_ID, HOME_TEAM_ID, VISITOR_TEAM_ID, SEASON, GAMECODE (and other info)
  def add_games(self,documents,collection_name='games'):
    collection = self.db[collection_name]
    ids = []
    for doc in documents:
      # easier to use game date - don't need timezone info
      doc['GAME_DATE_EST'] = self._formatted_game_date(doc)
      id = collection.insert(doc)
      ids.append(id)
    return ids

  def get_games(self,**kwargs):

    # default collection name is 'games'
    if 'collection_name' in kwargs:
      collection_name = kwargs['collection_name']
    else:
      collection_name = 'games'

    # can also do by date range - will build that later
    # have building block from NBAComScraper.bootstrap

    collection = self.db[collection_name]
    return list(collection.find())

  '''
  standings collection
  each standing document describes a team and its record:
  has TEAM_ID, SEASON_ID, STANDINGSDATE, CONFERENCE, TEAM, G, W, L, W_PCT, HOME_RECORD, ROAD_RECORD
  '''

  def add_standings(self,documents,collection_name='standings'):
    collection = self.db[collection_name]
    ids = []

    for doc in documents:
      # change to mm-dd-yyyy format by replacing /
      doc['STANDINGSDATE'].replace("/", "-")
      id = collection.insert(doc)
      ids.append(id)

    return ids

  def get_standings(self,**kwargs):

    # default collection name is 'games'
    if 'collection_name' in kwargs:
      collection_name = kwargs['collection_name']
    else:
      collection_name = 'standings'

    # can also do by date range - will build that later
    # have building block from NBAComScraper.bootstrap

    collection = self.db[collection_name]
    return list(collection.find())


  '''
  boxscores collections
  each player_boxscore document has GAME_ID, TEAM_ID, TEAM_ABBREVIATION, PLAYER_ID, PLAYER_NAME, and then stats such as MIN, PTS, etc.
  each team_boxscore document has GAME_ID, TEAM_ID, TEAM_ABBREVIATION, TEAM_CITY, and then stats such as MIN, PTS, etc.
  '''

  def add_player_boxscores(self,documents,collection_name='player_boxscores'):
    collection = self.db[collection_name]
    ids = []

    for doc in documents:
      # change to mm-dd-yyyy format by replacing /
      id = collection.insert(doc)
      ids.append(id)

    return ids

  def get_player_boxscores(self,**kwargs):

    # default collection name is 'games'
    if 'collection_name' in kwargs:
      collection_name = kwargs['collection_name']
    else:
      collection_name = 'player_boxscores'

    # can also do by date range - will build that later
    # have building block from NBAComScraper.bootstrap

    collection = self.db[collection_name]
    return list(collection.find())

  def add_team_boxscores(self,documents,collection_name='team_boxscores'):
    collection = self.db[collection_name]
    ids = []

    for doc in documents:
      # change to mm-dd-yyyy format by replacing /
      id = collection.insert(doc)
      ids.append(id)

    return ids

  def get_team_boxscores(self,**kwargs):

    # default collection name is 'games'
    if 'collection_name' in kwargs:
      collection_name = kwargs['collection_name']
    else:
      collection_name = 'team_boxscores'

    # can also do by date range - will build that later
    # have building block from NBAComScraper.bootstrap

    collection = self.db[collection_name]
    return list(collection.find())

  '''
  player_stats collection
  each player_stat document has STATDATE, GAME_ID, TEAM_ID, TEAM_ABBREVIATION, PLAYER_ID, PLAYER_NAME, and then stats such as MIN, PTS, etc.
  '''

  def add_playerstats(self,documents,collection_name='playerstats'):
    collection = self.db[collection_name]
    ids = []

    for doc in documents:
      # change to mm-dd-yyyy format by replacing /
      id = collection.insert(doc)
      ids.append(id)

    return ids

  def get_playerstats(self,**kwargs):

    # default collection name is 'games'
    if 'collection_name' in kwargs:
      collection_name = kwargs['collection_name']
    else:
      collection_name = 'playerstats'

    # can also do by date range - will build that later
    # have building block from NBAComScraper.bootstrap

    collection = self.db[collection_name]
    return list(collection.find())

  '''
  players collection
  each player document has PLAYERDATE, PLAYER_ID, PLAYER_NAME, etc.
  '''
  def add_players(self,documents,collection_name='players'):
    collection = self.db[collection_name]
    return [collection.insert(doc) for doc in documents]

  def get_players(self,**kwargs):

    # default collection name is 'games'
    if 'collection_name' in kwargs:
      collection_name = kwargs['collection_name']
    else:
      collection_name = 'players'

    # can also do by date range - will build that later
    # have building block from NBAComScraper.bootstrap

    collection = self.db[collection_name]
    return list(collection.find())

  '''
    scoreboards collection
    each scoreboard document has . . .
  '''
  def add_scoreboards(self,documents,collection_name='scoreboards'):
    collection = self.db[collection_name]
    if type(documents) is not list:
      ids = collection.insert(documents)
    else:
      ids = [collection.insert(doc) for doc in documents]

    return ids

  def get_scoreboards(self,**kwargs):

    # default collection name is 'games'
    if 'collection_name' in kwargs:
      collection_name = kwargs['collection_name']
    else:
      collection_name = 'scoreboards'

    # can also do by date range - will build that later
    # have building block from NBAComScraper.bootstrap

    collection = self.db[collection_name]
    return list(collection.find())

  '''
    player_gamelogs collection
    each player_gamelog document has STATDATE, GAME_ID, TEAM_ID, TEAM_ABBREVIATION, PLAYER_ID, PLAYER_NAME, and then stats such as MIN, PTS, etc.
  '''

  def add_player_gamelogs(self,documents,collection_name='player_gamelogs'):
    return self.db[collection_name].insert(documents)

  def get_player_gamelogs(self,**kwargs):

    # default collection name is 'games'
    if 'collection_name' in kwargs:
      collection_name = kwargs['collection_name']
    else:
      collection_name = 'player_gamelogs'

    # can also do by date range - will build that later
    # have building block from NBAComScraper.bootstrap

    return list(self.db[collection_name].find())

  '''
    team_gamelogs collection
    each team_gamelog document has GAME_ID, TEAM_ID, TEAM_ABBREVIATION and then stats such as MIN, PTS, etc.
  '''

  def add_team_gamelogs(self,documents,collection_name='team_gamelogs'):
    return self.db[collection_name].insert(documents)

  def get_team_gamelogs(self,**kwargs):

    # default collection name is 'games'
    if 'collection_name' in kwargs:
      collection_name = kwargs['collection_name']
    else:
      collection_name = 'team_gamelogs'

    # can also do by date range - will build that later
    # have building block from NBAComScraper.bootstrap

    return list(self.db[collection_name].find())

  '''
    start private methods
  '''

  def _formatted_game_date(self, game):
    '''
      takes a game, which is a dictionary including GAMECODE key
      returns a date formatted in mm-dd-yyyy format (12-25-2012)
    '''
    gc = game['GAMECODE']
    gd, teams = gc.split("/")
    return datetime.datetime.strptime(gd,'%Y%m%d').strftime('%m-%d-%Y')

if __name__ == "__main__":
  pass
