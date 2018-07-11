from bs4 import BeautifulSoup
import requests
import time
import logging
import re
import unidecode
import collections

#####################################

class ResponseError(Exception):
    pass

#####################################

def wordcount(sentence):
    c = collections.Counter(sentence.split(' '))
    return([*c.values()])

#####################################

def getSentences(url,tag):

    time.sleep(0.5)

    def tryForHtml(url,tries=0,limit=6):

        if tries < limit:
            try:
                r = requests.get(url)
            except requests.exceptions.ConnectionError:
                delay = 1 + (1*tries)
                logging.warning('connection error for %s!'%(url))
                logging.warning('sleeping for ... %i'%(delay))
                time.sleep(delay)
                tries += 1
                html = tryForHtml(url,tries=tries)
            except request.exceptions.HTTPError:
                logging.warning('http-error for %s!'%(url))
                html = ''
            except request.exceptions.Timeout:
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


    print('Retrieving sentences from %s (with %s)'%(url,tag))

    html = tryForHtml(url,limit=6)

    try:
        sentences = parseHtml(html,tag=tag)
    except ResponseError:
        sentences = 'na'

    return(sentences)

#####################################

def parseHtml(html,tag="articleBody"):

    bSp = BeautifulSoup(html,"html.parser")
    body = bSp.find(itemprop=tag)

    def process(sentences):
        sentences = body.text.lower()

        sentences = re.sub(r"('|’)s",' ',sentences)
        sentences = re.sub(r"n('|’)t",' not',sentences)

        sentences = re.sub(r'[0-9]{4}','year',sentences)
        sentences = re.sub(r'[0-9]{1,2}(nd|rd|th)','date',sentences)
        sentences = re.sub(r'\w*\.\w{2,3}',' url ',sentences)
        sentences = re.sub(r'(mr\.|ms\.)',' pronoun ',sentences)

        sentences = re.sub(r'[\n\,-]',' ',sentences)

        sentences = unidecode.unidecode(sentences)
        sentences = re.sub(r'[^a-z \.]',' ',sentences)
        sentences = re.sub(r' +',' ',sentences)
        sentences = sentences.split('.')

        return(sentences)

    def check(sentence):
        valid = len(sentence) > 0
        valid &= len(sentence.split(' ')) > 1
        valid &= all(count < 4 for count in wordcount(sentence))
        return(valid)

    if body is None:
        raise ResponseError('bad tag')
    else:
        sentences = process(body)
        sentences = '\n'.join([sent for sent in sentences if check(sent)])

    return(sentences)

#####################################
