# xbgcv2.R
# looking at xgboost model to classify NBA x5

require(plyr)

require(RPostgreSQL)
require(dplyr)
require(caret)
library(corrplot)
library(ggplot2)
library(xgboost)
library(doMC);
registerDoMC(cores = 4)


nbadb <- function() {
  drv <- dbDriver("PostgreSQL")
  con <- dbConnect(drv, dbname = "nbadb", user='nbadb', password='cft0911')
  q = "SELECT * FROM tm2"         
  dbGetQuery(con, q)
}


pp <- function(sal=3000, dk=10, min=10, old=FALSE) {
  # filter out NA
  # remove useless players
  d = nbadb()
  d = d[complete.cases(d),]
  d %>% filter(salary >= sal, dkema25 > dk, minema25 > min)
}


setupClassify <- function(sal=3500, dk=10, min=10, old=FALSE, y='x5') {
  d = pp(sal, dk, min, old)
  d = subset(d, select = -c(min, dk_points, back_to_back, three_in_four))  
  if (y == 'x5') {
    y = d$x5
    d = subset(d, select = -c(x5, x6))
    d$y = y
  } else if (y == 'x6') {
    y = d$x6
    d = subset(d, select = -c(x5, x6))
    d$y = as.factor(y)     
  }
  d
}


xgb_train <- function(dtrain, tc, tg) {
    train(
      x = as.matrix(dtrain[,-ncol(dtrain)]),
      y = as.factor(dtrain[,ncol(dtrain)]),
      trControl = tc,
      tuneGrid = tg,
      method = "xgbTree"
    )
}


xgb_grid <- function() {
    expand.grid(
      nrounds = 10,
      eta = c(.1, 0.01, 0.001),
      max_depth = c(6, 8, 10),
      gamma=c(.5,1,1.5), colsample_bytree=1, 
      min_child_weight=1, subsample=1
    )
}


xgb_trcontrol <- function() {
    trainControl(
      method = "cv",
      number = 5,
      verboseIter = TRUE,
      returnData = FALSE,
      returnResamp = "all",                                                  
      classProbs = TRUE,                                                           
      summaryFunction = twoClassSummary,
      allowParallel = TRUE
    )
}


xgbcv <- function(dtrain, seed=13) {
    set.seed(seed)
    xgb_train(dtrain, xgb_trcontrol(), xgb_grid())
}


xgb_plot <- function(xgbt) {
  ggplot(xgbt$results, aes(x = as.factor(eta), y = max_depth, size = ROC, color = ROC)) + 
    geom_point() + 
    theme_bw() + 
    scale_size_continuous(guide = "none")
}


bin.salaries <- function(position, v) {
   rep(position, v[position])
}


lmsal1 <- function(d, seed=13) {
  # Create model with default paramters
  # based on http://machinelearningmastery.com/tune-machine-learning-algorithms-in-r/
  in_train = createDataPartition(d$salary, p=.75, list=FALSE)
  dtrain = d[in_train,]
  dtest = d[-in_train,]
  Xtrain = subset(dtrain, select=-c(salary))
  ytrain = subset(dtrain, select=c(salary))
  Xtest = subset(dtest, select=-c(salary))
  ytest = subset(dtest, select=c(salary))
  control <- trainControl(method="repeatedcv", number=10, repeats=3)  
  set.seed(seed)
  m = train(salary ~ ., data=d, method="lm", trControl=control)
  m
}

# d$salbin = as.factor(unlist(sapply(positions, myfun, h$counts), recursive=TRUE))

