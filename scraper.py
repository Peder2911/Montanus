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

from tools import pageTools,argvTools,urlTools

import inspect
import importlib

with open('config.json') as file:
    config = json.loads(file.read())

# Returns a dictionary of URL components, also containing the API key
def gatherComponents(target,config,keys):
    components = config[target]
    components['key'] = keys[target]
    return(components)

#####################################

def getPage(url):
    time.sleep(config['interval'])
    print('Getting %s'%(url))
    print('')
    page = requests.get(url).text
    page = json.loads(page)
    return(page)

#####################################

def scrapePages(targetSite,components,args,config):

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

# This is the external function, that performs a scrape.
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
