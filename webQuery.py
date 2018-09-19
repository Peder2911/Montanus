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

def errPrint(message):
    print(message,file = sys.stderr,flush = True)

#####################################

with open(moduleTools.relPath('configFiles/sourceProfiles.json',__file__)) as file:
    config = json.load(file)

with open(moduleTools.relPath('configFiles/keys.json',__file__)) as file:
    keys = json.load(file)

#####################################
# Again with this logging stuff...

import logging
from logging.config import dictConfig
import yaml

loggingPath = moduleTools.relPath('configFiles/logging.yaml',__file__)
with open(loggingPath) as file:
    logConf = yaml.load(file)
    logConf['handlers']['file']['filename'] = moduleTools.relPath('logs/webQuery.log',__file__)
dictConfig(logConf)

fl = logging.getLogger('base_file')

# Logging doghouse
#####################################

cl = logging.getLogger('console')

def executeQuery(targetSite,arguments,dates=(False,False),boolean="AND"):

    # This "components" stuff might point towards the fact that
    # this stuff should done in a class?

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

    # If bad or no dates, substitutes default dates
    if all(dates) is False:
        beginDate = dateTimeTools.getDefaultDate('begin')
        endDate = dateTimeTools.getDefaultDate('end')
        dates = (beginDate,endDate)
        cl.debug('dates substituted by defaults')

    # Remove bad dates...
    if all(dateTimeTools.checkBaseFormat(date) for date in dates):
        pass
    else:
        articles = executeQuery(targetSite,arguments,dates=(False,False),boolean=boolean)
        cl.debug('date format not recognized!')

    # This is where the magic happens
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
                errPrint('Response not good.')

    else:
        errPrint('No articles...')
        articles = []

    return(articles)

#####################################

def queryScope(url,parameters,components):
    responseChecker = pageTools.makeChecker(components,fl)
    hitsIndexer = pageTools.makeIndexer(components['hitsPath'])

#    print('')
#    print('Scoping query...')

    response,rUrl = getPage(url,parameters,returnUrl=True)
    errPrint('scoping @ %s'%(rUrl))

    if responseChecker(response):
        hits = hitsIndexer(response)
    else:
        errPrint('Response not good.')
        hits = 0

    if hits > 0:
        pages = ((hits-1) // 10)+1
    else:
        pages = 0

    errPrint('Hits=%s (pages=%s)'%(hits,pages))
    errPrint('est time: %i sec @ %g sec interval'%(pages*config['interval'],config['interval']))

    return(hits,pages)

#####################################

def getPage(url,parameters,json=True,returnUrl=False,**kwargs):
    time.sleep(config['interval'])

    try:
        page = requests.get(url,params = parameters,**kwargs)

    except requests.exceptions.ConnectionError:
        errPrint('ConnectionError, retrying!')
        page = retryPage(url,parameters,1,5)
    else:
        errPrint('\nGot %s'%(page.url))
        page = page.json()



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
            errPrint('Try %i failed! Retrying...'%(tries))
            retryPage(url,parameters,tries,maxTries)
        else:
            page = page.json()
    else:
        errPrint('Not able to reach %s'%(url))
        fl.warning('Unable to reach %s'%(url))
        page = []

    return(page)

#####################################
# Ergh...

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

# erghhhh...
#####################################
