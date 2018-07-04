import json
import os
import logging
import re
import pandas as pd

from . import scrapeText

from collections import deque

#####################################
'''
This code changes data scraped from multiple sources into a standardized format
that is suitable for analysis.

The data is read and written as JSON.
'''
#####################################

def recursiveIndex(dict,keys):
    keys = deque(keys)
    out = dict
    while keys:
        out = out[keys.popleft()]
    return(out)

#####################################

def tryTagsForText(url,tags):
    text = ''

    while text == '' and tags != []:
        currTag = tags.pop()
        text = scrapeText.getSentences(url,tag=currTag)

    if text == '':
        text = 'none'
    return(text)

def generalizeFormat(jsonArticle,source = 'nyt'):

    path = os.path.join(os.path.dirname(__file__),'data/website_profiles/responseStructure.json')
    with open(path) as file:
        profile = json.load(file)[source]

    out = {}
    keys = ('date','headline','body','source')

    if profile['request?']:

        try:
            url = recursiveIndex(jsonArticle,profile['source'])
        except KeyError:
            logging.warning('Not able to get text, no URL in article file')
            text = []

        tags = profile['scrapeTags']
        text = tryTagsForText(url,tags)
        jsonArticle['body'] = text

    for key in keys:
        try:
            out[key] = recursiveIndex(jsonArticle,profile[key])
        except KeyError:
            logging.warning('%s not in article'%(key))
            out[key] = ''

    return(out)
