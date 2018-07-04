
# Functions that do things with returned data

from collections import deque
import logging
import sys

# Indexes through multiple indices
# Also returns true (result) or false, making it a handy function to check the
# path BUT REMEMBER : 0 == False (possible result), so use if multiIndex is False!!!

def multiIndex(dictionary,indexList):
    indexDeque = deque(indexList)

    while len(indexDeque) > 0:
        index = indexDeque.popleft()

        if index in dictionary.keys():
            dictionary=dictionary[index]
        else:
            logging.debug('Tried %s in %s, no such key'%(index,dictionary.keys()))
            return(False)

    return(dictionary)

# Multiindex decorator that returns a function adapted to target site.

def makeIndexer(path):
#    path = config[target][pathType]

    def indexer(response):

        if multiIndex(response,path) is not False:
            result = multiIndex(response,path)
        else:
            logging.warning('bad %s for %s'%(pathType,target))
            result = []

        return(result)

    return(indexer)

# Sniffing function for determining if a response is healthy or not.
# Also adapted to target site.

def makeChecker(components):

#    components = config[target]

    messagePath = components['messagePath']
    statusPath = components['statusPath']
    errorPath = components['errorPath']

    goodStatus = components['goodStatus']
    errorStatus = components['errorStatus']


    def responseChecker(response):

        if multiIndex(response,statusPath):
            status = multiIndex(response,statusPath)

            if status == goodStatus:
                return(True)

            elif status == errorStatus and multiIndex(response,errorPath):
                error = multiIndex(response,errorPath)
                logging.critical('Request returned error!')
                logging.critical(error)
                return(False)

            else:
                logging.warning('Bad status = %s'%(status))
                return(False)

        elif multiIndex(response,messagePath) is not False:
            message = multiIndex(response,messagePath)

            logging.warning(message)
            return(False)


        else:
            logging.critical('Wierd response! (no status or message)')
            logging.critical(response.keys())
            return(False)

    return(responseChecker)
