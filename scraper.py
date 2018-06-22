#! ../bin/python

# Functions for scraping articles from NYT.
# Could easily be repurposed.
# Gets info from config.json

import requests

import json

import sys
import time
from collections import deque

import logging

from tools import pageTools,argvTools,urlTools,fileTools,dateTimeTools

#####################################

with open('config.json') as file:
    config = json.loads(file.read())

#####################################

def getPage(url):
    time.sleep(config['interval'])
    print('Getting %s'%(url))
    print('')

    try:
        page = requests.get(url).text
    except ConnectionError:
        retryPage(url,1,5)

    page = json.loads(page)
    return(page)

def retryPage(url,tries,maxTries):
    if tries < maxTries:
        tries += 1
        time.sleep(1+tries)

        try:
             page = requests.get(url).text
        except ConnectionError:
            retryPage(url,tries,maxTries)

    else:
        logging.critical('page not reachable?')
        page = []

    return(page)

#####################################

def querySniff(url,components):
    responseChecker = pageTools.makeChecker(components)
    hitsIndexer = pageTools.makeIndexer(components['hitsPath'])
    print('Sniffing...')
    response = getPage(url)

    if responseChecker(response):
        hits = hitsIndexer(response)
    else:
        logging.critical('Smells bad.')
        hits = 0

    if hits > 0:
        pages = ((hits-1) // 10)+1
    else:
        pages = 0

    return(hits,pages)

def executeQuery(targetSite,arguments,beginDate=False,endDate=False):

    components = fileTools.readJsonFile('config.json')[targetSite]
    components['key'] = fileTools.readJsonFile('keys.json')[targetSite]

    contentIndexer = pageTools.makeIndexer(components['contentPath'])
    hitsIndexer = pageTools.makeIndexer(components['hitsPath'])
    responseChecker = pageTools.makeChecker(components)

#    url = urlTools.parseUrl(arguments,components,0,beginDate,endDate)

#    hits,pages = querySniff(url,components)

    articles = subQuery(arguments,components,beginDate,endDate)

    return(articles)

def subQuery(arguments,components,beginDate,endDate):
    contentIndexer = pageTools.makeIndexer(components['contentPath'])
    responseChecker = pageTools.makeChecker(components)

    url = urlTools.parseUrl(arguments,components,0,beginDate,endDate)

    hits,pages = querySniff(url,components)
    print("Number of hits: %i"%(hits))

    if pages > components['maxPages']:
        beginYear,_,_ = dateTimeTools.splitFormatted(beginDate,asInt=True)
        endYear,_,_ = dateTimeTools.splitFormatted(endDate,asInt=True)

        #WARNING if there is more than 2000 hits in a year, things get wierd.
        durations = dateTimeTools.getDurations(beginYear,endYear)
        print(durations)

        beginDateA,endDateA = durations[0]
        beginDateB,endDateB = durations[1]

        print('Query split')

        print('Requesting: 1st duration')
        print(durations[0])
        articles = subQuery(arguments,components,beginDateA,endDateA)

        print('Requesting: 2nd duration')
        print(durations[1])
        articles += subQuery(arguments,components,beginDateB,endDateB)

    elif pages != 0:
        articles = []

        pagesToGet = [0]+[x+1 for x in range(pages)]

        for page in pagesToGet:
            url = urlTools.parseUrl(arguments,components,page,beginDate,endDate)
            response = getPage(url)

            if responseChecker(response):
                articles += contentIndexer(response)
            else:
                pass
                #TODO error.
    else:
        #TODO warning.
        articles = []

    return(articles)

#####################################
