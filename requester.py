#!../bin/python
# This script runs the dyadGetter script, reading its requests from the dyads.csv-file.

import subprocess
import csv
import time
import json

with open('config.json') as file:
    config = json.loads(file.read())

with open('dyads.csv','r') as file:

    header = True

    for row in csv.reader(file):
        if not header:
            subprocess.call(['./dyadGetter.py',row[1],row[2]])
            time.sleep(1)
        else:
            # Skip first row
            header = False
