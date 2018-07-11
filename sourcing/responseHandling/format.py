import json
import os
import logging
import re
import pandas as pd

from . import getAndParse

from collections import deque

#####################################
'''
This code changes data scraped from multiple sources into a standardized format
that is suitable for analysis.

The data is read and written as JSON.

The standard format is like this:

keys = ('date','headline','body','source')

### ''date'' is the publication date

### ''headline'' is the headline, not processed

### ''body'' is a string of newline-separated sentences

### ''source'' is a url.

### ''id'' is added to the article when it is appended to the database.

'''
#####################################

def recursiveIndex(dict,keys):
    keys = deque(keys)
    out = dict
    while keys:
        out = out[keys.popleft()]
    return(out)

#####################################

def generalizeFormat(jsonArticle,source):

    path = os.path.join(os.path.dirname(__file__),'data/profiles.json')
    with open(path) as file:
        profile = json.load(file)[source]

    out = {}
    keys = ('date','headline','body','source')

    if profile['request?']:

        try:
            url = recursiveIndex(jsonArticle,profile['source'])
        except KeyError:
            logging.warning('Not able to get body, no URL in article file')
            body = 'na'

        tags = profile['scrapeTags']
        body = tryTagsForText(url,tags)

        jsonArticle['body'] = body

    for key in keys:
        try:
            out[key] = recursiveIndex(jsonArticle,profile[key])
        except KeyError:
            logging.warning('%s not in article'%(key))
            out[key] = 'NA'

    return(out)

#####################################

def tryTagsForText(url,tags):
    body = 'na'

    while body == 'na' and tags != []:
        currTag = tags.pop()
        body = getAndParse.getSentences(url,tag=currTag)

    if body == 'na':
        pass #TODO replace default?

    return(body)
