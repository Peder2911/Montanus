import json
import os
import logging
import re
import pandas as pd
import subprocess
import sys

try:
    from . import getBody
except ImportError:
    import getBody

from collections import deque


#####################################

def errReport(message):
    print(message,file=sys.stderr)
    sys.stderr.flush()

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
    p = subprocess.run(script_py,
                       stdout = subprocess.PIPE,
                       input=text.encode())
    out = p.stdout.decode()
    return(out)

#####################################

def relPath(filePath,fileVar):
    selfPath = os.path.dirname(fileVar)
    relPath = os.path.join(selfPath,filePath)
    return(relPath)

#####################################

def generalize(article,source):

    proPath = relPath('./data/profiles.json',__file__)

    with open(proPath) as file:
        profile = json.load(file)[source]

    out = {}
    keys = ('date','headline','source')

    if profile['request?']:
        body = getBody.request(article,source,profile)
    else:
        body = recursiveIndex(article,profile['body'])

#    if clean:
#        body = pipeText(body,'./pipes/textCleaning.py')
#    else:
#        pass
#
#    if tokenize:
#        body = pipeText(body,'./pipes/tokenization.py')
#    else:
#        pass
    
    out['body'] = body.replace('\n',' ')

    for key in keys:
        try:
            field = recursiveIndex(article,profile[key])
            field = field.replace('\n',' ')
            out[key] = field 

        except KeyError:
#            logging.warning('%s not in article'%(key))
            out[key] = 'NA'

    return(out)

#####################################
'''
if __name__ == '__main__':
    sys.stdin.flush()
    articles = json.load(sys.stdin)
    source = sys.argv[1]

    genArticles = []

    for n,art in enumerate(articles):
        out = generalizeFormat(art,source)
        genArticles.append(out)

    sys.stdout.write(json.dumps(genArticles))
'''
