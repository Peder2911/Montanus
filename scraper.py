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

# Returns a dictionary of URL components, also containing the API key
# TODO Should maybe be somewhere else?

def gatherComponents(target,config,keys):
    components = config[target]
    components['key'] = keys[target]
    return(components)

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

        pagesToGet = [x+1 for x in range(pages)]

        for page in pagesToGet:
            url = urlTools.parseUrl(arguments,components,page,beginDate,endDate)
            response = getPage(url)

            if responseChecker(response):
                articles += contentIndexer(response)
            else:
                pass
                #TODO error.
    else:
        print('C')
        #TODO warning.
        articles = []

    return(articles)

#####################################

# Only actually needs targetSite and config, since these can give components
# Only actually really needs target and args? (could read config in function)
def scrapePages(targetSite,components,args,config,breaks = 0):

    contentIndexer = pageTools.makeIndexer(targetSite,'contentPath',config)
    hitsIndexer = pageTools.makeIndexer(targetSite,'hitsPath',config)
    responseChecker = pageTools.makeChecker(targetSite,config)

    firstUrl = urlTools.parseUrl(targetSite,components,args)
    print('\nProbing: %s'%(firstUrl))
    firstPage = requests.get(firstUrl)
    firstPage = json.loads(firstPage.text)

    if responseChecker(firstPage):
        hits = hitsIndexer(firstPage)
        pagesToGet = (hits-1) // 10
    else:
        # TODO better warning? (handled in pageTools?)
        logging.warning('Exit 1 (see log)')
        sys.exit(1)

    if pagesToGet > 200:
        breaks = (hits // 2000) + 1
        scrapePages(targetSite,components,args,config,breaks = breaks)


        # TODO time-range pageination
        logging.warning('Too many pages to get, getting 200 pages')
        pagesToGet = 200

    #####################################

    if hits > 0:
        print('Number of hits: %s'%(hits))

        print('Getting %i more pages' %(pagesToGet))
        print('')

        articles = contentIndexer(firstPage)

        for pageNumber in range(pagesToGet):
            page = getPage(urlTools.parseUrl(targetSite,components,args,pageNumber+1))

            if responseChecker(page):
                articles += contentIndexer(page)

        return(articles)

    else:
        logging.warning('%s yielded no hits'%(str(args)))
        return([])

#####################################

# This is the external function, that performs scraping.
# Arguments are always given in list format!

def directedScrape(targetSite,arguments,config,apiKeys):

    # _
    # Additional handling of arguments..
    # _

    # Adapting the query
    queryArguments = argvTools.adaptQuery(targetSite,arguments,config)
    urlComponents = gatherComponents(targetSite,config,apiKeys)

    response=scrapePages(targetSite,urlComponents,queryArguments,config)

    return(response)

#####################################

if __name__ == '__main__':

    with open('config.json') as file:
        config = json.loads(file.read())

    with open('keys.json') as file:
        apiKeys = json.loads(file.read())
