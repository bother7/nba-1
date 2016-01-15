get_players = function (fname, sql) {
  players = fread('~/player_gamelog_summary.csv', colClasses=c("chr", "Factor", "Factor", "chr", "Factor", "Factor", "int", "int", "numeric", "numeric", "numeric", "numeric", "numeric", "numeric", "numeric", "numeric", "numeric", "Factor", "numeric", "numeric"), na.strings=c("",NA,"NULL"))
  con <- dbConnect(RMySQL::MySQL())
  players = data.table(dbGetQuery(con, "SELECT * FROM summary_player_gamelogs"))
}

fix_players = function (players) {
  players$wl = as.factor(players$wl)
  players$game_id = as.factor(players$game_id)
  players$pid = as.factor(players$pid)
  players$team = as.factor(players$team)
  players$wl = as.factor(players$wl)
  players$game_date = as.Date(players$game_date, "%Y-%m-%d")
  players$points = as.numeric(players$points)
  players$minutes = as.numeric(players$minutes)
}
