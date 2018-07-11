import json
import os
import logging
import re
import pandas as pd
import subprocess

try:
    from . import getAndParse
except (ModuleNotFoundError,ImportError):
    import getAndParse

try:
    from .util import moduleTools
except (ModuleNotFoundError,ImportError):
    from util import moduleTools

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

def pipeText(text,script):
    scriptPath = moduleTools.relPath(script,__file__)
    call = ['python',scriptPath]
    p = subprocess.run(call,input=text.encode(),stdout=subprocess.PIPE)
    return(p.stdout.decode())

#####################################

def generalizeFormat(article,source,clean=True,tokenize=False):

    path = moduleTools.relPath('./data/profiles.json',__file__)
    with open(path) as file:
        profile = json.load(file)[source]

    out = {}
    keys = ('date','headline','source')

    if profile['request?']:
        url = recursiveIndex(article,profile['source'])

        getBody_py = moduleTools.relPath('./util/getBody.py',__file__)
        call = ['python',getBody_py,source,url]
        p = subprocess.run(call,stdout=subprocess.PIPE)
        body = p.stdout.decode()

    else:
        body = recursiveIndex(article,profile['body'])

    if clean:
        body = pipeText(body,'./util/textCleaning.py')
    else:
        pass

    if tokenize:
        body = pipeText(body,'./util/tokenization.py')
    else:
        pass

    out['body'] = body

    for key in keys:
        try:
            out[key] = recursiveIndex(article,profile[key])
        except KeyError:
            logging.warning('%s not in article'%(key))
            out[key] = 'NA'

    return(out)

#####################################
