# Functions for "flattening" a JSON file, and writing it to a CSV file.

import csv

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
