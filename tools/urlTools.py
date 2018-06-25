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

def padNumber(number,zeroes):
    if number < 10 ** zeroes:
        numberString = str(number)
        padding = "0" * (zeroes-(len(numberString)-1))
        number = padding + numberString
    else:
        number = str(number)
    return(number)

def formatDate(date,dateFormat='Y-M-D'):
    # Accepts date as 'YYYY_MM_DD'!

    if re.match('[0-9]{4}_[0-9]{2}_[0-9]{2}',date):
        year,month,day = date.split('_')

        date = dateFormat.replace('Y','{yearFrm}')
        date = date.replace('M','{monthFrm}')
        date = date.replace('D','{dayFrm}')

        date = date.format(yearFrm = year, monthFrm = month, dayFrm = day)
    else:
        logging.warning('Given date in wrong format %s'%(date))

    return(date)

def argsToFq(arguments,components):
    queryKeys = components['queryKeys']
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

    return(fq)

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

def listToFqstring(list):
    str = ''
    first = True
    for entry in list:
        if first:
            str += '"'+ entry +'"'
            first = False
        else:
            str += ' "%s"'%(entry)
    return(str)


def assembleQuery(argumentList,components,boolean):
    # Takes a dictionary with list-values = {field:("value1" "value2")} and a boolean ('AND' / 'OR')
    str = ''

    if 'complexQueryTag' in components.keys():
        format = 'dict'
        queryName = components['complexQueryTag']
    elif 'queryTag' in components.keys():
        format = 'list'
        queryName = components['queryTag']
    else:
        raise ConfigError('%s lacks query tag in config'%(components['siteName']))

    if format == 'dict':
        fqDictionary = argsToFq(argumentList,components)
        queryString = dictToFqstring(fqDictionary,boolean)
    else:
        queryString = listToFqstring(argumentList)

    return(queryName,queryString)


def getDefaultDate(type):

    if type == 'begin':
        date = '1981_01_01'
    elif type == 'end':
        nowYear = str(datetime.datetime.now().year)
        nowMonth = padNumber(datetime.datetime.now().month,1)
        nowDay = padNumber(datetime.datetime.now().day,1)

        date = '%s_%s_%s'%(nowYear,nowMonth,nowDay)
    else:
        date = getDefaultDate('begin')
    return(date)

def handleDate(components,date,type):

    if date is False:
        date = getDefaultDate(type)
    else:
        pass

    format = components['dateFormat']
    formatted = formatDate(date,dateFormat=format)
    return(formatted)

def gatherParameters(arguments,components,boolean="AND",page=0,dates=(False,False)):

    #####################################
    # One Function to bring them all, and in the parameters dictionary bind them
    # Remember that the date needs to be formatted like so : YYYY_MM_DD

    #TODO this arguments stuff is pretty terrible, maybe dont need defaults at this lvl?

    beginDate = handleDate(components,dates[0],'begin')
    endDate = handleDate(components,dates[1],'end')

    parameters = {}

    queryName,queryString = assembleQuery(arguments,components,boolean)
    parameters[queryName] = queryString

    parameters[components['keyTag']] = components['key']

    parameters[components['beginDateTag']] = beginDate
    parameters[components['endDateTag']] = endDate

    if page == 0:
        pass
    else:
        parameters[components['pageTag']] = str(page)

    return(parameters)

if __name__ == '__main__':
    with open('config.json') as file:
        config = json.loads(file.read())

    exComp = config['nyt']
    exComp['key'] = 'AN_API_KEY'
    exArgs = ['glocations.contains','colombia','organizations','Revolutionary Armed Forces of Colombia']

    exComp2 = config['guardian']
    exComp2['key'] = "64cb4929-0b1b-46e5-ae33-8baf895fd078"
    exArgs2 = ['Colombia','FARC']
