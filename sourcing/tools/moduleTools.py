
import os

#####################################

def relPath(filePath,fileVar):
    selfPath = os.path.dirname(fileVar)
    relPath = os.path.join(selfPath,filePath)
    return(relPath)

#easter
