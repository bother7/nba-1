# What is nba?

It is a python library to scrape, parse, and analyze nba stats and daily fantasy information.

# Roadmap


# Scrapers

ESPNNBAScraper
FantasyLabsNBAScraper
NBAComScraper
PinnacleBAScraper
RotoGuruNBAScraper

# Parsers

ESPNNBAParser
FantasyLabsNBAParser
NBAComParser
NBAStufferParser
PinnacleBAParser
RotoGuruNBAParser

# Database

NBAComDb
MBAMongo
NBAStufferDB

# Utility Classes

NBAGames
NBANameMatcher
NBASeasons
NBATeamNames

# Scripts

dfs-player-summary
espn-nba-players
nbacom-bootstrap
nbacom_fetch_boxscores
nbacom_fetch_yearly_playerstats
nbacomplayerfetch
nbacom_yearly_gamelogs
nbacom_yearly_stats
nba_daily_teamstats
nba_list_games
nbastuffer-script
nba-team-report
nba_team_stats
nba_upcoming_games
rotoguru-nba

# Keeping the database up-to-date

## Daily Updates

### cs_player_gamelogs

Use agent.current_season_player_gamelogs(season)
Incremental updates to cs_player_gamelogs table

### cs_team_gamelogs

Use agent.current_season_team_gamelogs(season)
Incremental updates to cs_team_gamelogs table

### cs_playerstats

TODO: routine to combine base & advanced measures

TODO: decision about stat_date vs. game_date columns, maybe call it as_of??

### cs_playerstats

TODO: routine to combine base & advanced measures

TODO: decision about stat_date vs. game_date columns, maybe call it as_of??

### fantasylabs_models

TODO: automate updates

### salaries

TODO: This can be from multiple different sources, should update daily regardless of source

## Yearly Database Updates

### cs_games

### cs_teamgames

### games

### playerstats

### teamgames

### teamstats

