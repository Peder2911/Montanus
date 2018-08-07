#!/usr/bin/env python
from bs4 import BeautifulSoup
import requests
import time
import re
import unidecode
import collections
#from nltk import sent_tokenize as nltk_sent_tokenize

import sys
import io

class ResponseError(Exception):
    pass

#####################################

'''
This script performs simple non-destructive text cleaning, by substituting
known analogues (ex. ´|‘|’ with '), and translating all characters to unicode.

Outputs newline-separated sentences.
'''

#####################################

def wordcount(sentence):
    c = collections.Counter(sentence.split(' '))
    return([*c.values()])

#####################################

def processText(text):

    def process(text):

        # Abbreviations ?
#        text = re.sub(r"('|’)s",' ',text,flags=re.IGNORECASE)
#        text = re.sub(r"n('|’)t",' not',text,flags=re.IGNORECASE)
#        text = re.sub(r"('|’)d",' would',text,flags=re.IGNORECASE)
#        text = re.sub(r"i('|’)m",'i am',text,flags=re.IGNORECASE)
#        text = re.sub(r"i('|’)ll",'i will',text,flags=re.IGNORECASE)



        # Years and dates should be migrated?
#        text = re.sub(r'\b(19|20)\d{2}\b','year',text,flags=re.IGNORECASE)
#        text = re.sub(r'[0-9]{1,2}(nd|rd|th)','date',text,flags=re.IGNORECASE)

        # URL regex

        # num2words


        # Standardize apostrophes
        standardizationTable = {'‘':'\'','’':'\'','´':'\'','`':'\'',
                                '“':'\"','”':'\"',
                                '–':'-'}
        text = text.translate(standardizationTable)

        # Translate non-unicode chars
        text = unidecode.unidecode(text)

        # Remove existing newlines.
#        text = text.replace('\n',' ')

        # Trim sequential whitespace
        text = re.sub(r'\s\s+',' ',text,flags=re.IGNORECASE)

        # Trim leading and trailing whitespace
        text = text.strip()

        return(text)

    text = process(text)
#    sentences = nltk_sent_tokenize(text)
#    text = '\n'.join(sentences)

    return(text)

#####################################

if __name__ == '__main__':

    try:
        input = sys.stdin.read()
    except UnicodeDecodeError:
        sys.stderr.write('\nInput has wrong encoding: %s'%(sys.stdin.encoding))
        sys.exit(1)

    output = processText(input)

    sys.stdout.write(output)
