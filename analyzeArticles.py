#!../bin/python

import subprocess
import sys

import json
import csv

from sourcing import webQuery
from sourcing.responseHandling import standardization as stdization

from io import StringIO

#####################################

with open('config.json') as configFile:
    config = configFile.read()
    config = json.loads(config)

with open('keys.json') as keyFile:
    keys = keyFile.read()
    keys = json.loads(keys)

#####################################

testTarget = 'guardian'
testArguments = ['hedmark']

#####################################
try:
    with open('testTemp/.json') as file:
        docs = json.load(file)
except FileNotFoundError:
    pages = webQuery.executeQuery(testTarget,testArguments)

    docs = pages
    docs = [stdization.generalizeFormat(doc,source=testTarget) for doc in docs]

    try:
        with open('testTemp/.json','w') as file:
            json.dump(docs,file)
    except FileNotFoundError:
        logging.debug('no tempfile written')

jsonString = json.dumps(docs)

toR = jsonString + '\n'

process = subprocess.run(['./analysis/bayesPredict.r'],input=toR.encode())

#TODO add support for arguments
