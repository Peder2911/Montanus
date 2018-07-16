
import csv
import json
import sys
from io import StringIO

#####################################

def makeFilename(args,source,filetype='csv'):
    out = source+'_'
    first = True

    for arg in args:
        if not first:
            out += '_'+arg
        else:
            out += arg
            first = False

    # Remove whitespace
    out = out.replace(' ','')
    return(out)

def readJsonFile(file):
    with open(file) as targetFile:
        jsonFile = json.loads(targetFile.read())
    return(jsonFile)

#####################################

def writeOutCsv(response,args,source):
    location = 'dyads/'
    filetype = '.csv'

    filename = makeFilename(args,source)

    outFilename = location + filename + filetype

    with open(outFilename,'w') as file:
        articlesToCsvfile(response,file)

def articlesToCsvfile(articles,file):
    #TODO export the json properly!
    #(do JSON dumps)...
    writer = csv.writer(file)

    colNames = articles[0].keys()
    writer.writerow(colNames)


    for entry in articles:
        row = []

        for col in colNames:

            if col in entry.keys():
                #JSON needs to be handled here.
                row.append(entry[col])
            else:
                row.append('NA')

        writer.writerow(row)

#####################################
