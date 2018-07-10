from bs4 import BeautifulSoup
import requests
import time
import logging
import re
import unidecode
import collections

class ResponseError(Exception):
    pass

#####################################

def getSentences(url,tag):

    time.sleep(0.5)

    print('Retrieving sentences from %s (with %s)'%(url,tag))

    try:
        r = requests.get(url)
    except ConnectionError:
        print('ConnectionError!')
        time.sleep(5)
        getSentences(url,tag)
        #TODO some more error handling (bad response)
    else:
        html = r.text

    try:
        sentences = parseHtml(html,tag=tag)
    except ResponseError:
        sentences = ['NA']

    return(sentences)

def wordcount(sentence):
    c = collections.Counter(sentence.split(' '))
    return([*c.values()])

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
        sentences = [sent.strip() for sent in sentences]
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
        sentences = [sent for sent in sentences if check(sent)]

    return(sentences)

#####################################
