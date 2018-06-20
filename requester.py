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

    args = deque(sys.argv[1:])
    source = args.popleft()

    with open('dyads.csv','r') as file:

        header = True

        for row in csv.reader(file):
            if not header:
                subprocess.call(['./dyadGetter.py',source,row[1],row[2]])
                time.sleep(1)
            else:
                # Skip first row
                header = False
