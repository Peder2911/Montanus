import os
import sys
import subprocess

import re

import json

from collections import deque

from tools import moduleTools
import webQuery

# import dbTools

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
        fl.warning(e)
        articles = []

    processArticles_py = moduleTools.relPath('responseHandling/processArticles.py',__file__)
    processArticles_py = ['python',processArticles_py,target]

    processArticles_py = subprocess.run(processArticles_py,
                                        input = json.dumps(articles).encode(),
                                        stdout = subprocess.PIPE,
                                        stderr = subprocess.PIPE)
    out = processArticles_py.stdout.decode()
    err = processArticles_py.stderr.decode()

    articles = json.loads(out)
    for error in err.split('\n'):
        if error != '':
            fl.warning(error)
            sys.stderr.write(error)

    for article in articles:
        article['id'] = '_'.join([target]+list(arguments))

    articles = json.dumps(articles) + '\n'
    sys.stdout.write(articles)
