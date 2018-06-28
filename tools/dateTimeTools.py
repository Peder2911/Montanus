
from datetime import datetime,timedelta
import numpy
import pandas as pd
import re
from collections import deque

class ConfigError(Exception):
    pass

class FormatError(Exception):
    pass

class DateError(Exception):
    pass

#####################################

baseFormat = 'YYYY_MM_DD'

#####################################

def padNumber(number,digits):
    zeroes = digits - 1
    if number < 10 ** zeroes:
        numberString = str(number)
        padding = "0" * (zeroes-(len(numberString)-1))
        number = padding + numberString
    else:
        number = str(number)
    return(number)

#####################################

def datetimeToBaseformat(datetime):
    dt = datetime
    year,month,day = dt.year,padNumber(dt.month,2),padNumber(dt.day,2)
    base = "%s_%s_%s"%(year,month,day)
    return(base)

def baseformatToDatetime(dateStr):
    year,month,day = splitFormatted(dateStr,asInt=True)
    dt = datetime(year,month,day)
    return(dt)

def splitFormatted(date,asInt = False):
    out = year,month,day = date.split('_')
    if asInt:
        out = (int(entry) for entry in out)
    return(out)

def todayAsFormatted():
    now = datetime.now()
    year = now.year
    month = padNumber(now.month,2)
    day = padNumber(now.day,2)

    formatted = "{year}_{month}_{day}".format(year=year,month=month,day=day)
    return(formatted)

def checkBaseFormat(dateString):
    hasMatched = re.match('[0-9]{4}_[0-9]{2}_[0-9]{2}',dateString)
    hasMatched = hasMatched and len(dateString) == 10
    if hasMatched:
        return(True)
    else:
        return(False)

#####################################

def getDefaultDate(type):

    if type == 'begin':
        date = '1981_01_01'
    elif type == 'end':
        nowYear = str(datetime.now().year)
        nowMonth = padNumber(datetime.now().month,2)
        nowDay = padNumber(datetime.now().day,2)

        date = '%s_%s_%s'%(nowYear,nowMonth,nowDay)
    else:
        date = getDefaultDate('begin')
    return(date)

#####################################

def transformDuration(duration):
    duration = [datetimeToBaseformat(datetime)for datetime in duration]
    return(duration)

def checkDuration(duration):
    if baseformatToDatetime(duration[0]) > baseformatToDatetime(duration[1]):
        raise DateError('Bad diff %s'%(duration))
    else:
        pass

#####################################

def datePercentiles(start,end,breaks=2):
    out = [start]

    daterange = pd.date_range(start,end)

    rangeLength = len(daterange)

    basePercentileIndex = rangeLength / 100
    basePercentile = 100 / breaks

    percentile = basePercentile

    while percentile < 100:
        percentileIndex = int(basePercentileIndex * percentile)
        out += [daterange[percentileIndex]]
        percentile += basePercentile

    out += [end]

    return(out)

def dateDurations(start,end,breaks=2):
    # Accepts year (min,max) as number
    start,end=(baseformatToDatetime(date) for date in (start,end))

    percentiles = datePercentiles(start,end,breaks)

    out = []
    duration = []

    for index,percentile in enumerate(percentiles):

        if index == 0:
            #1st
            duration = [start]

        elif index+1 == len(percentiles):
            #last
            duration += [end]

        else:
            duration.append(percentile-timedelta(days=1))
            out.append(transformDuration(duration))
            duration = [percentile]

        if len(duration) > 1:
            out.append(transformDuration(duration))

    [checkDuration(dur) for dur in out]

    return(out)
