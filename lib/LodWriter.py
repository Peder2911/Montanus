# A class for writing lod-formatted data (list of dictionaries) into a csv-file.
# The keys in the dictionary determine the columns.

import csv

class LodWriter():

    def __init__(self,lodData,fileobj):
        self.lodData = lodData
        self.fileobj = fileobj

    def write(self):
        writer = csv.writer(self.fileobj)
        
        colnames = [*self.lodData[0].keys()]
        
        writer.writerow(colnames)

        for line in self.lodData:
            row = []
            for colname in colnames:
                row.append(line[colname])
            writer.writerow(row)
                    
                


