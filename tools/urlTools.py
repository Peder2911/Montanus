#
# Functions for composing URLs.
#

import logging

def parseQueries(components,arguments):
    # Adapts to format required by the target site (from components)
    # returns queries in correct format, separated by booleans.

    logging.debug(components)

    queries = ''

    #TODO add more booleans?
    booleanOperator = ' AND '

    if components['queryFormat'] == 'dict':
        first = True
        for key,value in arguments.items():
            # add boolean if not first
            if first:
                first = False
            else:
                queries += booleanOperator

            queries += '%s:"%s"'%(key,value)

    elif components['queryFormat'] == 'list':
        first = True
        for value in arguments:
            # add boolean if not first
            if first:
                first = False
            else:
                queries += booleanOperator

            queries += '"' + value + '"'


    return(queries)

def parseUrl(targetSite,components,args,page=0):

    #####################################
    # One Function to bring them all, and in the url bind them

    queries = parseQueries(components,args)

    url = components['base_url']
    url += components['keyTag'] + components['key']
    url += components['queryTag'] + queries

    if page == 0:
        pass
    else:
        url += components['pageTag'] + str(page)

    return(url)
