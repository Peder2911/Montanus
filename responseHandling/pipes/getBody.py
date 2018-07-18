
#####################################

import requests as rq
from bs4 import BeautifulSoup as bs

import re
import os
import json

import sys

#####################################

path = os.path.join(os.path.dirname(__file__),'../data/profiles.json')
with open(path) as file:
    profile = json.load(file)

errors = ''

#####################################

def matchList(pattern,list):
    if list == [None]:
        list = ['None']
    matches = any([re.search(pattern,entry) for entry in list])
    return(matches)

#####################################

def getArticleBody(url,source):

    html = tryForHtml(url,limit=6)

    soup = bs(html,'html.parser')
    prof = profile[source]['bodyCandidates']
    prof.reverse()

    text = ''

    while text == '':
        tag = prof.pop()
        text = tryTag(soup,**tag)
        if len(prof) == 0 and text == '':
            text = 'none'

    return(text)

#####################################

def tryTag(soup,type,attr,regex):

    divs = soup.find_all(type)
    attrs = [div.get_attribute_list(attr) for div in divs]
    matches = [matchList(r'%s'%(regex),att) for att in attrs]
    matchIndices = [i for i,e in enumerate(matches) if e]

    tgtTags = []
    for index in matchIndices:
        tgtTags.append(divs[index])

    text = '\n'.join([tag.get_text() for tag in tgtTags])
    text = checkText(text)
    return(text)

def checkText(text):
    #TODO more elaborate candidate screening
    if text == 'garble':
        text = ''
    return(text)

#####################################

def tryForHtml(url,tries=0,limit=6):

    if tries < limit:
        try:
            r = rq.get(url)
        except rq.exceptions.ConnectionError:
            delay = 1 + (1*tries)
            logging.warning('connection error for %s!'%(url))
            logging.warning('sleeping for ... %i'%(delay))
            time.sleep(delay)
            tries += 1
            html = tryForHtml(url,tries=tries)

        except rq.exceptions.HTTPError:
            logging.warning('http-error for %s!'%(url))
            html = ''

        except rq.exceptions.Timeout:
            logging.warning('%s timed out!'%(url))
            html = ''

        except:
            logging.warning('some other exception...')
            html = ''
        else:
            html = r.text
    else:
        html = ''

    return(html)

#####################################

if __name__ == '__main__':

    source = sys.argv[1]
    url = sys.argv[2]

    body = getArticleBody(url,source)

    sys.stdout.write(body)
    sys.stderr.write(errors)
