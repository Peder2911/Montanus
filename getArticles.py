# Commenting can never redeem bad code
# but it helps...

import os
import sys

mypath = os.path.dirname(os.path.abspath(__file__))
sys.path.append(mypath)

import subprocess
import re
import json
import io

from collections import deque

from tools import moduleTools
from responseHandling import rHandling

from lib import LodWriter

import webQuery


def errReport(message):
    # Worst function i ever wrote
    print(message,file=sys.stderr)
    sys.stderr.flush()

class QueryError(Exception):
    pass

#####################################

import logging
from logging.config import dictConfig
import yaml # Why bother...

####################################
# The doghouse

loggingPath = moduleTools.relPath('configFiles/logging.yaml',__file__)

with open(loggingPath) as file:
    logConf = yaml.load(file)
    logConf['handlers']['file']['filename'] = moduleTools.relPath('logs/getArticles.log',__file__)

dictConfig(logConf)

fl = logging.getLogger('base_file')

# The doghouse
####################################

cl = logging.getLogger('console')

##########################################################################

if __name__ == '__main__':

    if '--dfi' in sys.argv:
        from dfitools import RedisFile
        # DFI compatible    
        
        config = json.load(sys.stdin) 
        
        target = config['target site'].lower()
        startdate = config ['startdate']
        enddate = config['enddate']
        boolean = 'AND'
        arguments = ['glocations.contains',config['location']]

        rconf = config['redis']
        outFile = RedisFile.RedisFile(listkey = rconf['listkey'],
                                      host = rconf['hostname'],
                                      port = rconf['port'],
                                      db = rconf['db'])
    else:
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

        outFile = sys.stdout

# Arguments are still really shady, need to fix
# Articles are grabbed here.
    try:
        articles = webQuery.executeQuery(
                    target, arguments, boolean=boolean, dates=(startdate,enddate))
    except QueryError as e:
        sys.stderr.write(e)
        articles = []

    genArticles = []

# "Generalize", meaning to grab fulltext.
# This "errReport" really grinds my gears

    for n,article in enumerate(articles):
        errReport('(%i of %i)'%(n+1,len(articles)))
        genArticles.append(rHandling.generalize(article,target))

    for article in genArticles:
        article.update({'id':'_'.join([target]+list(arguments)+[startdate,enddate])})

    fauxfile = io.StringIO()
    Writer = LodWriter.LodWriter(genArticles,fauxfile)
    Writer.write()
    data = fauxfile.getvalue()

    outFile.write(data)
