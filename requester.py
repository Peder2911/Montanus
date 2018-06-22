#!../bin/python
# Currently deprecated?

# The script currently expects row1 and row2 to be translated into
# glocations:"row1" AND organizations:"row2". This does currently not work.
# But it should be an easy fix.

import subprocess
import csv
import time
import json
from collections import deque

from tools import languageTools

import sys
import logging

with open('config.json') as file:
    config = json.loads(file.read())

with open('ucdp_conflicts_nonstates_actors.csv',encoding = 'utf-8') as file:
     reader = csv.reader(file)
     organizations_countries = {}
     for line in reader:
         organizations_countries[line[1]] = line[2]

#####################################

def makeDyadCall(source,country,organization):
    call = ['./getAndWrite.py']
    call += ['nyt']
    call += ['glocations',country]
    call += ['headline',organization]

    return(call)

#####################################

if __name__ == '__main__':

    if len(sys.argv) > 1:
        args = deque(sys.argv[1:])

    source = 'nyt'
    skipRows = 100
    # Skip header

    for organization,country in organizations_countries.items():

        if skipRows == 0:

#            call = ['./getAndWrite.py']
#            call += [source]
#            call += ['glocations',country]
#            call += ['organizations',organization]

            call = makeDyadCall(source,country,organization)

            time.sleep(1)
            res = subprocess.call(call)

            if res != 0:
                organizationSynonyms = deque(languageTools.synonyms(organization))
                print('Got %i synonyms'%(len(organizationSynonyms)))

                while len(organizationSynonyms) != 0 and res != 0:
                    organization = organizationSynonyms.popleft()
                    print('trying %s'%(organization))
                    call = makeDyadCall(source,country,organization)

                    time.sleep(1)
                    res = subprocess.call(call)




        else:
            logging.debug('skipping row no %i'%(skipRows))
            skipRows -= 1
