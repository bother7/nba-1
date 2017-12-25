library(caret)

d = read.csv('dset1.csv', header=TRUE)
d$picknum[is.na(d$picknum)] = 61
d$draft_round[is.na(d$draft_round)] = 3
d$y = ifelse(d$dk_points/d$salary*1000 > 5.5, 'y', 'n')
d$y = as.factor(d$y)
d2 = subset(d, select=-c(min, dkmin, dk_points, season, game_id, game_date, pos, game_number, four_in_five, five_in_seven, days_last_game, opp, position_group, back_to_back, three_in_four, nbacom_player_id, player_name, is_home, team_code, team_id))
d2 = d2[complete.cases(d2),]
in_train = createDataPartition(d2$y, p=.7, list=FALSE)
dtrain = d2[in_train,]
dtest = d2[-in_train,]
xtr = train(
  +          x = as.matrix(dtrain[,-ncol(dtrain)]),
  +          y = dtrain[,ncol(dtrain)],
  +          trControl = ctrl,
  +          tuneGrid = grid,
  +          method = "xgbTree"
  +     )