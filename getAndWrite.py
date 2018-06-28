#!../bin/python

# Utility script

# Called like this: script.py source boolean(AND/OR) arguments*

# The source needs to be a valid source (see config.json)
# Arguments will either be formatted as dictionary-like arguments (key-value pairs)
# or a list of arguments. This depends on the source.

# TODO Re-implement the suggesto-tron.

import requests

import sys
import time
from collections import deque

import logging
import json

import scraper
import synonymFetcher
from tools import pageTools,fileTools,languageTools,dateTimeTools

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
    boolean = " %s "%(args.popleft())
    arguments = args

    beginDate = '1981_01_01'
    endDate = dateTimeTools.todayAsFormatted()

    response = scraper.executeQuery(source,arguments,dates=(beginDate,endDate),boolean=boolean)

    if len(response) > 0:
        fileTools.writeOutCsv(response,args,source)
        sys.exit(0)
    else:
        logging.warning('Writing no hits')
        sys.exit(1)
