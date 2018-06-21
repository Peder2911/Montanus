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

import sys

with open('config.json') as file:
    config = json.loads(file.read())

with open('ucdp_conflicts_nonstates_actors.csv') as file:
     reader = csv.reader(file)
     organizations_countries = {}
     for line in reader:
         organizations_countries[line[1]] = line[2]

if __name__ == '__main__':

    if len(sys.argv) > 1:
        args = deque(sys.argv[1:])

    source = 'nyt'
    skipRows = 1
    # Skip header

    for organization,country in organizations_countries.items():

        call = ['./getAndWrite.py']
        call += [source]
        call += ['glocations',country]
        call += ['organizations',organization]

        subprocess.call(call)
        time.sleep(1)
