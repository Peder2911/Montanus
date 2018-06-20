
# Various functions for parsing and adapting arguments to different sites

import sys
import logging

def listToDict(list):

    if len(list) == 0:
        return(list)

    if not len(list)%2:
        i = iter(list)
        out = dict(zip(i,i))
    else:
        logging.warning('Dictionary conversion of list dropping one item: %s'%(str(list[-1])))
        list = list[:-1]
        out = listToDict(list)

    return(out)

def adaptQuery(targetSite,arguments,config):

    if 'queryFormat' in config[targetSite].keys():

        if config[targetSite]['queryFormat'] == 'dict':
            arguments = listToDict(arguments)
        elif config[targetSite]['queryFormat'] == 'list':
            pass
        else:
            logging.warning('Bad query format for %s'%(targetSite))
            logging.warning('Handling queries as list...')

    else:
        logging.critical('Query format missing for %s'%(targetSite))
        logging.warning('Handling queries as list...')

    return(arguments)
