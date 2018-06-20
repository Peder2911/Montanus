
from collections import deque
import logging
import sys

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

def makeIndexer(target,pathType,config):
    path = config[target][pathType]

    def indexer(response):

        if multiIndex(response,path) is not False:
            result = multiIndex(response,path)
        else:
            logging.warning('bad %s for %s'%(pathType,target))
            result = []

        return(result)

    return(indexer)

def makeChecker(target,config):
    #TODO might need to redo...

    goodPath = config[target]['contentPath']

    messagePath = config[target]['messagePath']

    useMessage = 'okMessage' in config[target]

    if useMessage:
        okMessage = config[target]['okMessage']
    else:
        pass

    def responseChecker(response):
        # Check path "if path is valid"

        if multiIndex(response,messagePath) is not False:
            message = multiIndex(response,messagePath)

            if useMessage:
                if message == okMessage:
                    logging.debug('got OK message')
                    return(True)
                else:
                    logging.warning(message)
                    return(False)
            else:
                # All messages are bad news
                logging.warning(message)
                return(False)
        else:
            return(True)

    return(responseChecker)
