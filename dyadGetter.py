#!../bin/python

# Utility script
# Accepts either one or two CL arguments
# The first needs to be a country
# The second can be an organization

# TODO
# This script also attempts to expand its vocabulary if the initial search gets no hits

import requests

import sys

import logging
import json

import scraper
import jsonTools

location = 'dyads/'
filetype = '.csv'

with open('config.json') as file:
    config = json.loads(file.read())

#####################################

def makeFilename(args,filetype='csv'):
    out = ''
    first = True
    for arg in args:
        if not first:
            out += '_'+arg
        else:
            out += arg
            first = False

    out = out.replace(' ','')

    return(out)

#####################################

if __name__ == '__main__':

    if len(sys.argv) >1:

        if len(sys.argv) >2:
            _,country, organization = sys.argv
            args = {'glocations':country,'organizations':organization}

        else:
            _,country = sys.argv
            args = {'glocations':country}

        response=scraper.scrape(config['base_url'],args)

        if len(response) > 0:
            # Write to file
            outFilename = location + makeFilename(sys.argv[1:]) + filetype
            jsonTools.jsonToCsv(json = response,filename = outFilename)

        else:
            # Disambiguation here?
            pass


    else:
        logging.critical('No arguments given')
        sys.exit(1)
