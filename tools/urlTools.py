#
# Functions for composing URLs.
#

import logging
import json
import datetime
import re

class ConfigError(Exception):
    pass

class FormatError(Exception):
    pass

#####################################

def adaptedQuery(components):
    # Decision tree to determine which one to choose
    str = ''
    argumentList = components['arguments']

    if 'complexQueryTag' in components.keys():
        format = 'dict'
        queryName = components['complexQueryTag']
    elif 'queryTag' in components.keys():
        format = 'list'
        queryName = components['queryTag']
    else:
        raise ConfigError('%s lacks query tag in config'%(components['siteName']))

    if format == 'dict':
        queryString = argsToFq(components)
    else:
        queryString = listToFqstring(components)

    return(queryName,queryString)

#####################################

def adaptDate(date,dateFormat='Y-M-D'):
    # Accepts date as 'YYYY_MM_DD'!

    if re.match('[0-9]{4}_[0-9]{2}_[0-9]{2}',date):
        year,month,day = date.split('_')

        date = dateFormat.replace('Y','{yearFrm}')
        date = date.replace('M','{monthFrm}')
        date = date.replace('D','{dayFrm}')

        date = date.format(yearFrm = year, monthFrm = month, dayFrm = day)
    else:
        pass
#        logging.warning('Not base format : %s'%(date))

    return(date)

#####################################

def argsToFq(components):
    queryKeys = components['queryKeys']
    arguments = components['arguments']

    fq = {}
    currentArg = ''

    for argument in arguments:

        if argument in queryKeys:
            fq[argument] = []
            currentArg = argument
        elif currentArg in fq.keys():
            fq[currentArg].append(argument)
        else:
            pass

    string=dictToFqstring(fq,components['boolean'])

    return(string)

def dictToFqstring(dict,boolean):
    str = ''

    firstKey = True
    for key in dict:

        if firstKey:
            firstKey = False
        else:
            str += " {bool} ".format(bool = boolean)

        str += '{field}:('.format(field = key)

        firstVal = True
        for value in dict[key]:
            if firstVal:
                firstVal = False
            else:
                str += " "

            str += '"{val}"'.format(val=value)

        str += ")"

    return(str)

def listToFqstring(components):
    args = components['arguments']
    str = ''
    first = True
    for entry in args:
        if first:
            str += entry
            first = False
        else:
            str += ' {bool} {entr}'.format(bool=components['boolean'],entr=entry)
    return(str)

#####################################


def adaptedDate(date,components):
    format = components['dateFormat']
    formatted = adaptDate(date,dateFormat=format)
    return(formatted)
