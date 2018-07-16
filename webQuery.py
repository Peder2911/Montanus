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

from tools import pageTools,urlTools,fileTools,dateTimeTools,moduleTools

class QueryError(Exception):
    pass

#####################################

with open(moduleTools.relPath('configFiles/sourceProfiles.json',__file__)) as file:
    config = json.load(file)

with open(moduleTools.relPath('configFiles/keys.json',__file__)) as file:
    keys = json.load(file)

#####################################

import logging
from logging.config import dictConfig
import yaml

loggingPath = moduleTools.relPath('configFiles/logging.yaml',__file__)
with open(loggingPath) as file:
    logConf = yaml.load(file)
    logConf['handlers']['file']['filename'] = moduleTools.relPath('logs/webQuery.log',__file__)
dictConfig(logConf)

fl = logging.getLogger('base_file')

#####################################

def executeQuery(targetSite,arguments,dates=(False,False),boolean="AND"):

    qS = ' '.join(arguments)
    fl.info('%s @ %s'%(qS,targetSite))

    #WARNING this function is impure...

    components = config[targetSite]
    components['key'] = keys[targetSite]

    components['arguments'] = arguments
    components['dates'] = dates
    components['boolean'] = boolean

    #######
    contentIndexer = pageTools.makeIndexer(components['contentPath'])
    hitsIndexer = pageTools.makeIndexer(components['hitsPath'])
    responseChecker = pageTools.makeChecker(components,fl)
    #######

    # Sub def. dates
    if all(dates) is False:
        beginDate = dateTimeTools.getDefaultDate('begin')
        endDate = dateTimeTools.getDefaultDate('end')
        dates = (beginDate,endDate)


    # Remove bad dates...
    if all(dateTimeTools.checkBaseFormat(date) for date in dates):
        pass
    else:
        articles = executeQuery(targetSite,arguments,dates=(False,False),boolean=boolean)

    # Prep over
    articles = subQuery(components,dates)

    return(articles)

#####################################

def subQuery(components,dates,page=0):
    #TODO recurring code
    #Decorate definition?
    contentIndexer = pageTools.makeIndexer(components['contentPath'])
    responseChecker = pageTools.makeChecker(components,fl)

    url = components['base_url']
    parameters = adaptedParameters(components,page,dates)

    # Scopes with initial dates
    hits,pages = queryScope(url,parameters,components)

    if pages > components['maxPages']:

#        print('')
#        print('Subdividing query...')

        beginDate,endDate = dates
        #WARNING if there is more than 2000 hits in a year, things get wierd.

        durations = dateTimeTools.dateDurations(beginDate,endDate)

        datesA = beginDateA,endDateA = durations[0]
        datesB = beginDateB,endDateB = durations[1]

#        print('')
#        print('Requesting: 1st duration')
        articles = subQuery(components,datesA)

#        print('')
#        print('Requesting: 2nd duration')
        articles += subQuery(components,datesB)


    elif pages != 0:
        articles = []

        #TODO Why get zero-eth page?
        pagesToGet = [0]+[x+1 for x in range(pages)]

        for page in pagesToGet:
            parameters['page'] = page
            response = getPage(url,parameters)

            if responseChecker(response):
                articles += contentIndexer(response)
            else:
                fl.warning('Response not good.')

    else:
        fl.warning('No articles...')
        articles = []

    return(articles)

#####################################

def queryScope(url,parameters,components):
    responseChecker = pageTools.makeChecker(components,fl)
    hitsIndexer = pageTools.makeIndexer(components['hitsPath'])

#    print('')
#    print('Scoping query...')

    response,rUrl = getPage(url,parameters,returnUrl=True)
    fl.info('scoping @ %s'%(rUrl))

    if responseChecker(response):
        hits = hitsIndexer(response)
    else:
        fl.warning('Response not good.')

    if hits > 0:
        pages = ((hits-1) // 10)+1
    else:
        pages = 0

    fl.info('Hits=%s (pages=%s)'%(hits,pages))

    return(hits,pages)

#####################################

def getPage(url,parameters,json=True,returnUrl=False):
    time.sleep(config['interval'])
#    print('')
#    print('Getting %s'%(url))
#    for key,param in parameters.items():
#        print('%s=%s'%(key,param))

    try:
        page = requests.get(url,params = parameters)
    except requests.exceptions.ConnectionError:
        fl.warning('ConnectionError, retrying!')
        retryPage(url,1,5)
#        logging.warning('ConnectionError, retrying')

    url = page.url

    if json:
        page = page.json()

    else:
        page = page.text

#    print('')
#    print(url)

    if returnUrl:
        return(page,url)
    else:
        return(page)

def retryPage(url,parameters,tries,maxTries,json=True):
    if tries < maxTries:
        tries += 1
        time.sleep(1+tries)

        try:
            page = requests.get(url,params = parameters)
        except requests.exceptions.ConnectionError:
            fl.warning('Try %i failed! Retrying...'%(tries))
            retryPage(url,parameters,tries,maxTries)
    else:
        fl.critical('Not able to reach %s'%(url))
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
