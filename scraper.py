#! ../bin/python

# Functions for scraping articles from NYT.
# Could easily be repurposed.
# Gets info from config.json

import requests

import json

import sys
import time

import logging

#####################################

with open('config.json') as file:
    config = json.loads(file.read())

with open('key.txt') as file:
    apiKey = file.read().strip()

#####################################

def parseUrl(base,args,page):
    url = base + '?api-key=%s'%(apiKey)
    url += '&fq='
    first = True

    for key,value in args.items():

        if not first:
            url += ' AND '
        else:
            first = False

        url += '%s:"%s"'%(key,value)


    url += '&page=%s'%(page)

    return(url)

def getPage(url):
    time.sleep(config['interval'])
    print('Getting %s'%(url))
    page = requests.get(url).text
    page = json.loads(page)
    return(page)


def scrape(base,args):

    firstUrl = parseUrl(base,args,0)
    print('\nProbing: %s'%(firstUrl))
    firstHit = requests.get(firstUrl)
    firstHit = json.loads(firstHit.text)

    if 'message' in firstHit.keys():
        logging.critical(firstHit['message'])
        sys.exit(1)

    hits = firstHit['response']['meta']['hits']
    pagesToGet = (hits-1)//10

    if hits > 0:
        print('Number of hits: %s'%(hits))

        print('Getting %i more pages' %(pagesToGet))

        articles = firstHit['response']['docs']

        for pageNumber in range(pagesToGet):
            page = getPage(parseUrl(base,args,pageNumber+1))
            articles += page['response']['docs']

        return(articles)

    else:
        logging.warning('%s and %s yielded no hits'%(args['glocations'],args['organizations']))
        return([])



#####################################
# As terminal util COUNTRY ORGANIZATION

if __name__ == '__main__':

    if len(sys.argv) >1:

        if len(sys.argv) >2:
            _,country, organization = sys.argv
            args = {'glocations':country,'organizations':organization}
        else:
            _,country = sys.argv
            args = {'glocations':country}

        response=scrape(config['nyt_base_url'],args)
        print(response)

    else:
        logging.critical('No arguments given')
        sys.exit(1)
