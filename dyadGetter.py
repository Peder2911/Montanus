#!../bin/python

# Utility script
# Called like this: script.py source arguments*
# The source needs to be a valid source (see config.json)
# Arguments will either be formatted as dictionary-like arguments (key-value pairs)
# or a list of arguments. This depends on the source.

# TODO
# Re-implement the suggesto-tron.

import requests

import sys
import time
from collections import deque

import logging
import json

import scraper
import synonymFetcher
from tools import pageTools,fileTools

location = 'dyads/'
filetype = '.csv'

#####################################

with open('config.json') as file:
    config = json.loads(file.read())

with open('keys.json') as file:
    apiKeys = json.loads(file.read())

#####################################

if __name__ == '__main__':

    args = deque(sys.argv[1:])
    source = args.popleft()
    args = args

    response = scraper.directedScrape(source,args,config,apiKeys)

    if len(response) > 0:
        fileTools.writeResponse(response,args,source)
    else:
        logging.warning('Writing no hits')


'''
if __name__ == '__vain__':

    if len(sys.argv) >1:

        args = ['Mozambique','Renamo']

        response=scraper.scrapePages(config['nyt_base_url'],args)

        if len(response) > 0:
            # Write to file
            outFilename = location + makeFilename(sys.argv[1:]) + filetype
            jsonTools.jsonToCsv(json = response,filename = outFilename)

        else:
            wikiTitles = synonymFetcher.getWikiTitles(organization)
            # Flip it to pop top results first
            wikiTitles = [*reversed(wikiTitles)]
            print(len(wikiTitles))

            while len(response) == 0 and len(wikiTitles) != 0:
                organization = wikiTitles.pop()
                args['organizations'] = organization
                print('Trying %s'%(organization))

                response = scraper.scrapePages(config['nyt_base_url'],args)
                time.sleep(config['interval'])

                if len(response) > 0:
                    outFilename = location + makeFilename(sys.argv[1:]) + filetype
                    jsonTools.jsonToCsv(json = response,filename = outFilename)

    else:
        logging.critical('No arguments given')
        sys.exit(1)
'''
