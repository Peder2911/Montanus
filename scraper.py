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

from tools import pageTools,urlTools,fileTools,dateTimeTools

#####################################

with open('config.json') as file:
    config = json.loads(file.read())

#####################################

def executeQuery(targetSite,arguments,dates=(False,False),boolean="AND"):

    #WARNING this function is impure...
    components = fileTools.readJsonFile('config.json')[targetSite]
    components['key'] = fileTools.readJsonFile('keys.json')[targetSite]
    components['arguments'] = arguments
    components['dates'] = dates
    components['boolean'] = boolean

    #######
    contentIndexer = pageTools.makeIndexer(components['contentPath'])
    hitsIndexer = pageTools.makeIndexer(components['hitsPath'])
    responseChecker = pageTools.makeChecker(components)
    #######

    #######
    if all(dates) is False:
        beginDate = dateTimeTools.getDefaultDate('begin')
        endDate = dateTimeTools.getDefaultDate('end')
        dates = (beginDate,endDate)


    if all(dateTimeTools.checkBaseFormat(date) for date in dates):
        pass
    else:
        print(dates)
        articles = executeQuery(targetSite,arguments,dates=(False,False),boolean=boolean)

#    dates = [*(dateTimeTools.baseformatToDatetime(date) for date in dates)]
    articles = subQuery(components,dates)

    return(articles)

#####################################

def subQuery(components,dates,page=0):
    #TODO recurring code
    #Decorate definition?
    contentIndexer = pageTools.makeIndexer(components['contentPath'])
    responseChecker = pageTools.makeChecker(components)

    url = components['base_url']
    parameters = adaptedParameters(components,page,dates)

    # Scopes with initial dates
    hits,pages = queryScope(url,parameters,components)
    print("Number of hits: %i"%(hits))

    if pages > components['maxPages']:

        print('')
        print('Subdividing query...')

        beginDate,endDate = dates
        #WARNING if there is more than 2000 hits in a year, things get wierd.

        durations = dateTimeTools.dateDurations(beginDate,endDate)

        datesA = beginDateA,endDateA = durations[0]
        datesB = beginDateB,endDateB = durations[1]

        print('')
        print('Requesting: 1st duration')
        articles = subQuery(components,datesA)

        print('')
        print('Requesting: 2nd duration')
        articles += subQuery(components,datesB)


    elif pages != 0:
        articles = []

        pagesToGet = [0]+[x+1 for x in range(pages)]

        for page in pagesToGet:
            parameters['page'] = page
            response = getPage(url,parameters)

            if responseChecker(response):
                articles += contentIndexer(response)
            else:
                pass
                #TODO error bad response

    else:
        #TODO warning no articles
        articles = []

    return(articles)

#####################################

def queryScope(url,parameters,components):
    responseChecker = pageTools.makeChecker(components)
    hitsIndexer = pageTools.makeIndexer(components['hitsPath'])

    print('')
    print('Scoping query...')

    response = getPage(url,parameters)

    if responseChecker(response):
        hits = hitsIndexer(response)
    else:
        logging.critical('Smells bad.')
        hits = 0

    if hits > 0:
        pages = ((hits-1) // 10)
    else:
        pages = 0

    print('')
    print('Hits=%s (pages=%s)'%(hits,pages))

    return(hits,pages)

#####################################

def getPage(url,parameters,json=True):
    time.sleep(config['interval'])
    print('')
    print('Getting %s'%(url))
    for key,param in parameters.items():
        print('%s=%s'%(key,param))

    try:
        page = requests.get(url,params = parameters)
    except ConnectionError:
        logging.warning('ConnectionError, retrying')
        retryPage(url,1,5)

    url = page.url

    if json:
        page = page.json()

    else:
        page = page.text

    print('')
    print(url)

    return(page)

def retryPage(url,parameters,tries,maxTries,json=True):
    if tries < maxTries:
        tries += 1
        time.sleep(1+tries)

        try:
             page = requests.get(url,params = parameters)
        except ConnectionError:
            retryPage(url,parameters,tries,maxTries)

    else:
        logging.critical('page not reachable?')
        page = []

    if json:
        page = page.json()
    else:
        page = page.text

    return(page)

#####################################

def adaptedParameters(components,page,dates):
    parameters = {}

    beginDate,endDate = (urlTools.adaptedDate(date,components) for date in dates)
    queryName,queryString = urlTools.adaptedQuery(components)

    parameters[queryName] = queryString
    parameters[components['beginDateTag']] = beginDate
    parameters[components['endDateTag']] = endDate
    parameters[components['keyTag']] = components['key']

    if page != 0:
        parameters[components['pageTag']] = str(page)

    return(parameters)

#####################################
