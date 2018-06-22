
import csv
import json

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

def writeResponse(response,args,source):
    location = 'dyads/'
    filetype = '.csv'

    filename = makeFilename(args,source)

    outFilename = location + filename + filetype

    jsonToCsv(response,outFilename)

def getColNames(json):
    return(json[0].keys())

def jsonToCsv(json,filename):
    print('writing to %s'%(filename))
    with open(filename,'w') as file:
        writer = csv.writer(file)

        colNames = getColNames(json)
        writer.writerow(colNames)


        for entry in json:
            row = []

            for col in colNames:

                if col in entry.keys():
                    row.append(entry[col])
                else:
                    row.append('NA')

            writer.writerow(row)

def readJsonFile(file):
    with open(file) as targetFile:
        jsonFile = json.loads(targetFile.read())
    return(jsonFile)
