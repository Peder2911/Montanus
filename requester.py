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

if __name__ == '__main__':

    if len(sys.argv) > 1:
        args = deque(sys.argv[1:])

    source = 'nyt'
    skipRows = 1
    # Skip header

    with open('dyads.csv','r') as file:

        for row in csv.reader(file):
            if skipRows>0:
                skipRows-=1
            else:
                call = ['./getAndWrite.py']
                call += [source]
                call += ['glocations',row[1]]
                call += ['organizations',row[2]]

                subprocess.call(call)
                time.sleep(1)
