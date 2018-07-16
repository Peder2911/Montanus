import json
import os
import logging
import re
import pandas as pd
import subprocess
import sys

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
    scriptPath = relPath(script,__file__)
    script_py = ['python',scriptPath]
    p = subprocess.run(script_py,input=text.encode(),
                       stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out = p.stdout.decode()
    err = p.stderr.decode()
    return(out,err)

#####################################

def relPath(filePath,fileVar):
    selfPath = os.path.dirname(fileVar)
    relPath = os.path.join(selfPath,filePath)
    return(relPath)

#####################################

def generalizeFormat(article,source,clean=True,tokenize=False):
    err = ''

    path = relPath('./data/profiles.json',__file__)
    with open(path) as file:
        profile = json.load(file)[source]

    out = {}
    keys = ('date','headline','source')

    if profile['request?']:
        url = recursiveIndex(article,profile['source'])

        getBody_py = relPath('./pipes/getBody.py',__file__)
        call = ['python',getBody_py,source,url]
        p = subprocess.run(call,stdout=subprocess.PIPE)
        body = p.stdout.decode()

    else:
        body = recursiveIndex(article,profile['body'])

    if clean:
        body,err_t = pipeText(body,'./pipes/textCleaning.py')
        err += err_t
    else:
        pass

    if tokenize:
        body,err_t = pipeText(body,'./pipes/tokenization.py')
        err += err_t
    else:
        pass

    out['body'] = body

    for key in keys:
        try:
            out[key] = recursiveIndex(article,profile[key])
        except KeyError:
#            logging.warning('%s not in article'%(key))
            err += '%s not in article'%(key)
            out[key] = 'NA'

    return(out,err)

#####################################

if __name__ == '__main__':
    articles = json.load(sys.stdin)
    source = sys.argv[1]

    genArticles = []
    err = ''

    for art in articles:
        out, err_t = generalizeFormat(art,source)
        genArticles.append(out)
        err += err_t + '\n'

    sys.stderr.write(err)
    sys.stdout.write(json.dumps(genArticles))
