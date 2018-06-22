# Not tested with current implementation

import requests
import json
import sys
import csv

with open('config.json') as file:
    config = json.loads(file.read())

def getWikiPages(term):
    baseUrl = config['wiki_base_url']+term+'&srlimit='+config['wiki_default_limit']
    response = json.loads(requests.get(baseUrl).text)
    return(response['query']['search'])

def getWikiTitles(term):
    result = getWikiPages(term)
    titles = []
    for page in result:
        titles.append(page['title'])
    return(titles)

def readSynonymFile(file):

    dictionary = {}

    with open(file,encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)

        for line in reader:
            dictionary[line[1]] = line[2]

    return(dictionary)

def synonyms(word,type = 'organization'):

        if type == 'organization':
            dictionaryFile = readSynonymFile('data/ucdp_actornames.csv')

        try:
            synonyms = [dictionaryFile[word]]
        except KeyError:
            synonyms = getWikiTitles(word)
            #TODO handle errors...

        return(synonyms)
