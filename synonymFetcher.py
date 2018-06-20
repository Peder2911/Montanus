# Not tested with current implementation

import requests
import json
import sys

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

if __name__ == '__main__':
    termRequest = sys.argv[1]
    titles = getWikiTitles(termRequest)
