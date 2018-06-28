#!../bin/python

import subprocess
import sys

import json

import scraper
#from tools import fileTools

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

meta = 'nyt,aJsonStream\n'

jsonString = json.dumps(docs)

toR = meta + jsonString + '\n'

process = subprocess.run(['./analysis/testJson.r'],input=toR.encode())
