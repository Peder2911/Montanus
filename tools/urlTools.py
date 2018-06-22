#
# Functions for composing URLs.
#

import logging
import datetime

#####################################

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
    year,month,day = date.split('_')

    date = dateFormat.replace('Y','{yearFrm}')
    date = date.replace('M','{monthFrm}')
    date = date.replace('D','{dayFrm}')

    date = date.format(yearFrm = year, monthFrm = month, dayFrm = day)
    return(date)

#####################################

def adaptQuery(arguments,format='list',):

    if format == 'dict':
        arguments = listToDict(arguments)
    elif format == 'list':
        pass
    else:
        logging.warning('Bad query format "%s"'%(format))
        logging.warning('Handling queries as list...')

    return(arguments)

def parseQueries(components,arguments):
    # Adapts to format required by the target site (from components)
    # returns queries in correct format, separated by booleans.

    logging.debug(components)

    queryFormat = components['queryFormat']

    queries = ''

    arguments = adaptQuery(arguments,format = queryFormat)

    #TODO add more booleans?
    booleanOperator = ' AND '

    if queryFormat == 'dict':
        first = True
        for key,value in arguments.items():
            # add boolean if not first
            if first:
                first = False
            else:
                queries += booleanOperator

            queries += '%s:"%s"'%(key,value)

    elif queryFormat == 'list':
        first = True
        for value in arguments:
            # add boolean if not first
            if first:
                first = False
            else:
                queries += booleanOperator

            queries += '"' + value + '"'

    else:
        logging.critical('bad query format')


    return(queries)

#####################################

def parseUrl(arguments,components,page=0,beginDate=False,endDate=False):

    # datetime as YYYY_MM_DD

    #####################################
    # One Function to bring them all, and in the url bind them

    if beginDate:
        beginDate = str(beginDate)
    else:
        beginDate = '1980_01_01'

    if endDate:
        endDate = str(endDate)
    else:
        nowYear = str(datetime.datetime.now().year)
        nowMonth = padNumber(datetime.datetime.now().month,1)
        nowDay = padNumber(datetime.datetime.now().day,1)

        endDate = '%s_%s_%s'%(nowYear,nowMonth,nowDay)

    dtForm = components['dateFormat']
    beginDate = formatDate(beginDate,dtForm)
    endDate = formatDate(endDate,dtForm)

#        endDate = formatDate(nowYear,nowMonth,nowDay)

    queries = parseQueries(components,arguments)

    url = components['base_url']
    url += components['keyTag'] + components['key']
    url += components['queryTag'] + queries

    if page > 0:
        url += components['pageTag'] + str(page)
    else:
        pass

    url += components['beginDateTag'] + beginDate
    url += components['endDateTag'] + endDate

    return(url)
