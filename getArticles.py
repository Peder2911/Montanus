import os
import sys
import subprocess

import re

import json

from collections import deque

from tools import moduleTools
from responseHandling import rHandling

import webQuery

# import dbTools

#####################################

def errReport(message):
    print(message,file=sys.stderr)
    sys.stderr.flush()

class QueryError(Exception):
    pass

#####################################

import logging
from logging.config import dictConfig
import yaml

loggingPath = moduleTools.relPath('configFiles/logging.yaml',__file__)

with open(loggingPath) as file:
    logConf = yaml.load(file)
    logConf['handlers']['file']['filename'] = moduleTools.relPath('logs/getArticles.log',__file__)

dictConfig(logConf)

fl = logging.getLogger('base_file')

##########################################################################

if __name__ == '__main__':

    # defaults
    startYr = '1989_01_01'
    endYr = '2018_01_01'

    arguments = deque(sys.argv[1:])

    try:
        target = arguments.popleft()

        if re.match(r'[0-9][0-9][0-9][0-9]',arguments[0]):
            startYr = arguments.popleft() + '_01_01'
        if re.match(r'[0-9][0-9][0-9][0-9]',arguments[0]):
            endYr = arguments.popleft() + '_12_31'

        if arguments[0] in ['AND','OR']:
            boolean = arguments.popleft()
        else:
            boolean = 'AND'

        cache = False

    except IndexError:
        cache = True

    try:
        articles = webQuery.executeQuery(
                    target, arguments, boolean=boolean, dates=(startYr,endYr))
    except QueryError as e:
        sys.stderr.write(e)
        articles = []

#    with open('testResources/preGen.json','w') as file:
#        json.dump(articles,file)

    genArticles = []
    for n,article in enumerate(articles):
        errReport('(%i of %i)'%(n+1,len(articles)))
        genArticles.append(rHandling.generalize(article,target))
    for article in genArticles:
        article.update({'id':'_'.join([target]+list(arguments)+[startYr,endYr])})

    articles = json.dumps(genArticles)

#    with open('testResources/getArticles.json','w') as file:
#        file.write(articles)

    print(articles,file = sys.stdout, flush = True)
    sys.exit(0)
