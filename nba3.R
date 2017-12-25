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

grid = expand.grid(nrounds = 10, eta = c(.1, 0.01, 0.001), max_depth = c(6, 8, 10), gamma=c(.5,1,1.5), colsample_bytree=1,min_child_weight=1, subsample=1)
ctrl = trainControl(method = "cv", number = 5, verboseIter = TRUE, returnData = FALSE, returnResamp = "all", classProbs = TRUE, summaryFunction = twoClassSummary, allowParallel = TRUE)
m = train(
  x = as.matrix(dtrain[,-ncol(dtrain)]), 
  y = dtrain[,ncol(dtrain)],
  trControl = ctrl, 
  tuneGrid = grid, 
  method = "xgbTree"
)
pred = predict(m, dtest[,-ncol(dtest)])
confusionMatrix(pred, dtest$y)  
