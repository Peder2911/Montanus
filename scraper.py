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

from tools import pageTools,argvTools

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

def parseQueries(components,arguments):

    logging.debug(components)

    queries = ''

    #TODO add more booleans
#    if components['booleanInQuery']:
#        booleanOperator = ' AND '
#    else:
#        booleanOperator = ' '

    booleanOperator = ' AND '

    if components['queryFormat'] == 'dict':

        first = True
        for key,value in arguments.items():

            # add boolean if not first
            if first:
                first = False
            else:
                queries += booleanOperator

            queries += '%s:"%s"'%(key,value)

    elif components['queryFormat'] == 'list':

        first = True
        for value in arguments:

            # add boolean if not first
            if first:
                first = False
            else:
                queries += booleanOperator

            queries += '"' + value + '"'


    return(queries)

def parseUrl(targetSite,components,args,page=0):

    #TODO Guardian starts at page 1, 0 is blank
    # this is the same in NYT, so page 0 should always be blank.

    queries = parseQueries(components,args)

    url = components['base_url']
    url += components['keyTag'] + components['key']
    url += components['queryTag'] + queries

    if page == 0:
        pass
    else:
        url += components['pageTag'] + str(page)

    return(url)

def getPage(url):
    time.sleep(config['interval'])
    print('Getting %s'%(url))
    print('')
    page = requests.get(url).text
    page = json.loads(page)
    return(page)


def scrapePages(targetSite,components,args,config):

    # Make tools based on target
    contentIndexer = pageTools.makeIndexer(targetSite,'contentPath',config)
    hitsIndexer = pageTools.makeIndexer(targetSite,'hitsPath',config)
    responseChecker = pageTools.makeChecker(targetSite,config)

    firstUrl = parseUrl(targetSite,components,args)
    print('\nProbing: %s'%(firstUrl))
    firstPage = requests.get(firstUrl)
    firstPage = json.loads(firstPage.text)

    logging.debug('Returned %s'%(firstPage['response'].keys()))
    if 'message' in firstPage['response'].keys():
        print(firstPage['response']['message'])

    #####################################

    if responseChecker(firstPage):
        hits = hitsIndexer(firstPage)
        pagesToGet = (hits-1) // 10
    else:
        # TODO better warning
        logging.warning('No hits')

    #####################################

    if pagesToGet > 200:
        logging.warning('Too many pages to get, getting 200 pages')
        pagesToGet = 200

    if hits > 0:
        print('Number of hits: %s'%(hits))

        print('Getting %i more pages' %(pagesToGet))
        print('')

        articles = contentIndexer(firstPage)

        for pageNumber in range(pagesToGet):
            page = getPage(parseUrl(targetSite,components,args,pageNumber+1))

            if responseChecker(page):
                articles += contentIndexer(page)

        return(articles)

    else:
        logging.warning('%s yielded no hits'%(str(args)))
        return([])

# This function performs a scrape
# But it expects arguments to be fully formatted?
# Arguments are always given in list format!

def directedScrape(targetSite,arguments,config,apiKeys):

    # Additional handling of arguments..

    # Adapting the query
    queryArguments = argvTools.adaptQuery(targetSite,arguments,config)
    urlComponents = gatherComponents(targetSite,config,apiKeys)

    response=scrapePages(targetSite,urlComponents,queryArguments,config)

    return(response)


#####################################
# As terminal util COUNTRY ORGANIZATION

if __name__ == '__main__':
    logging.getLogger().setLevel('WARNING')

    #####################################

    with open('config.json') as file:
        config = json.loads(file.read())

    with open('keys.json') as file:
        apiKeys = json.loads(file.read())

    #####################################

    '''    arguments = deque(sys.argv[1:])

        if arguments[0] in config['options']:
            command = arguments.popleft()

            if command == '-t' or '--tgt' or '--target':
                logging.debug('changing targetSite')
                targetSite = arguments.popleft()

        else:
            targetSite = config['defaultTarget']'''

    #####################################

    '''    urlComponents = gatherComponents(targetSite,config,apiKeys)

        contentIndexer = pageTools.makeIndexer(targetSite,'contentPath',config)
        hitsIndexer = pageTools.makeIndexer(targetSite,'hitsPath',config)
        responseChecker = pageTools.makeChecker(targetSite,config)

        if len(arguments) > 0:

            if urlComponents['queryFormat'] == 'dict':
                if len(arguments) > 1:
                    arguments = myUtil.listToDict(arguments)
                else:
                    logging.critical('%s requires more than one argument (key:value)')
                    sys.exit(1)

            elif urlComponents['queryFormat'] == 'list':
                pass

            else:
                logging.critical('Unknown or missing query format for %s'%(targetSite))

            logging.debug('using %s'%(str(arguments)))

            logging.info('This script only prints the response, use dyadGetter.py to scrape')
    #        response=scrapePages(urlComponents,arguments)

        else:
            logging.critical('No arguments given')
            sys.exit(1)'''
