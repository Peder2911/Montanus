from bs4 import BeautifulSoup
import requests
import time
import re
import unidecode
import collections

import sys

class ResponseError(Exception):
    pass

#####################################

def wordcount(sentence):
    c = collections.Counter(sentence.split(' '))
    return([*c.values()])

#####################################

def processText(text):
    err = ''

    def process(text):

        text = text.lower()

        text = re.sub(r"('|’)s",' ',text)
        text = re.sub(r"n('|’)t",' not',text)

        text = re.sub(r'[0-9]{4}','year',text)
        text = re.sub(r'[0-9]{1,2}(nd|rd|th)','date',text)
        text = re.sub(r'\w*\.\w{2,3}',' url ',text)
        text = re.sub(r'(mr\.|ms\.)',' pronoun ',text)
        text = re.sub(r'(inc\.)','abbreviation',text)

        text = re.sub(r'[\n\,-]',' ',text)

        text = unidecode.unidecode(text)
        text = re.sub(r'[^a-z \.\!\?]',' ',text)
        text = re.sub(r' +',' ',text)

        return(text)

    def check(sentence):

        #TODO implement logging
        valid = len(sentence) > 0
        valid &= len(sentence.split(' ')) > 1
        valid &= all(count < 8 for count in wordcount(sentence))
        if not valid:
            sys.stderr.write('Pruning sentence %s\n'%(sentence))
        return(valid)

    text = process(text)
    sentences = re.split(r'(\.|\?|\!)',text)
    text = '\n'.join([sent.strip() for sent in sentences if check(sent)])

    return(text)

#####################################

if __name__ == '__main__':
    input = sys.stdin.read()

    output = processText(input)

    sys.stdout.write(output)
