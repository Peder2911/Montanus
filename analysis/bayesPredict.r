#!/usr/local/bin/rscript

# libs --------------------------------------------------------------------


library(jsonlite)
library(stringr)
library(magrittr)
library(dplyr)
library(tm)
library(e1071)


# functions ---------------------------------------------------------------

checkTransposition <- function(df){
  if(ncol(df) == 1){
    n <- rownames(df)

    df <- df%>%
      t()%>%
      as.data.frame(stringsAsFactors=FALSE)

    colnames(df) <- n
    rownames(df) <- NULL
    df <- charsToFactors(df)
  }
  df
}

occurrenceToBinary <- function(df){
  df <- df%>%
    apply(2,function(x) x<-ifelse(as.logical(x),'yes','no'))%>%
    as.data.frame(stringsAsFactors=FALSE)%>%
    checkTransposition()

  df
}

adaptDf <- function(df,columns){
  inBoth <- names(df)[names(df) %in% columns]
  df <- df[inBoth]

  toAdd <- columns[!columns%in%inBoth]
  df[,toAdd] <- 0

  df <- df %>%
    checkTransposition()

  df
}

binaryToFactors <- function(x){
  x <- ifelse(x > 0,'yes','no')
  x <- factor(x,levels=c('no','yes'))
}

applyToColumns <- function(df,func){
  ls <- as.list(df)
  ls <- lapply(ls,func)
  df <- as.data.frame(ls)
  df
}

analyzeArticle <- function(article){
  sentences <- str_split(article['body'],"\\.")%>%
    unlist()
  sentences <- sentences[str_length(sentences) > 0]

  newDf <- sentences%>%
    VectorSource()%>%
    VCorpus()%>%
    tm_map(removeWords,stopwords())%>%
    tm_map(removeNumbers)%>%
    tm_map(removePunctuation)%>%
    tm_map(stemDocument)%>%
    DocumentTermMatrix()%>%
    as.matrix()%>%
    as.data.frame(stringsAsFactors=FALSE)%>%
    adaptDf(ft)%>%
    applyToColumns(binaryToFactors)

  pred <- predict(m,newDf,type='raw')
  catPred <- sapply(pred[,2],function(x)ifelse(x>0.5,1,0))
  factPred <- sapply(catPred,function(x){
    x <- ifelse(x==1,'yes','no')
    x <- factor(x,levels=c('no','yes'))
  })

  out <- list(
    source = article['source'],
    date = article['date'],
    headline = article['headline'],
    sentCount = length(sentences),
    maxProb = max(pred[,2]),
    meanProb = mean(pred[,2]),
    posClass = sum(catPred),
    pstPosClass = sum(catPred) / length(sentences)
  )
  out
}

runAnalysis <- function(articles){
  data <- apply(articles,1,analyzeArticle)%>%
    bind_rows()
  data
}

# imports ----------------------------------------------------------------

path <- substr(commandArgs()[4],10,nchar(commandArgs()[4]))%>%
  str_split('/')%>%
  unlist()
path <- paste(path[-length(path)],collapse='/')

modPath <- paste(path,'models/bayes1.rds',sep='/')
print(modPath)
load(modPath)

articles <- readLines('stdin')%>%
  fromJSON()

out <- runAnalysis(articles)

# Out ----------------------------------------------------------------

now <- format(Sys.time(),'_%Y_%m_%d_%X')
filePath <- paste('classifiedData/articles',now,'.csv',sep='')

write.csv(out,file=paste(path,filePath,sep='/'))
