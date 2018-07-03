#!../bin/python

import subprocess
import sys

import json

import scraper
#from tools import fileTools
from responseHandling import standardization as stdization

from io import StringIO

#####################################

with open('config.json') as configFile:
    config = configFile.read()
    config = json.loads(config)

with open('keys.json') as keyFile:
    keys = keyFile.read()
    keys = json.loads(keys)

#####################################

testTarget = 'nyt'
testArguments = ['glocations.contains','mozambique','organizations','renamo']

#####################################

#pages = scraper.executeQuery(testTarget,testArguments)

with open('testCases/nyt/ok.json') as file:
    toWrite = json.loads(file.read())

docs = toWrite['response']['docs']
docs = [stdization.generalizeFormat(doc) for doc in docs]

jsonString = json.dumps(docs)

toR = jsonString + '\n'

process = subprocess.run(['./analysis/bayesPredict.r'],input=toR.encode())
