
import datetime
import numpy

#####################################

def padNumber(number,zeroes):
    if number < 10 ** zeroes:
        numberString = str(number)
        padding = "0" * (zeroes-(len(numberString)-1))
        number = padding + numberString
    else:
        number = str(number)
    return(number)

#####################################

def getPercentiles(min,max,breaks = 2):

    out = [min]

    years = range(min,max+1)
    basePercentile = 100 / breaks
    percentile = basePercentile

    while percentile < 100:
        out += [int(numpy.percentile(years,percentile))]
        percentile += basePercentile

    out += [max]

    return(out)

def getDurations(min,max,breaks = 2):
    # Accepts year (min,max) as number

    yrStart = "_01_01"
    yrEnd = "_12_31"

    percentiles = getPercentiles(min,max,breaks)
    out = []
    duration = []

    for index,percentile in enumerate(percentiles):

        if index == 0:
            #1st
            duration = [str(percentile)+yrStart]

        elif index+1 == len(percentiles):
            #last
            duration += [str(percentile)+yrEnd]

        else:
            duration.append(str(percentile-1)+yrEnd)
            out.append(duration)
            duration = [str(percentile)+yrStart]

        if len(duration) > 1:
            out.append(duration)

    return(out)

def splitFormatted(date,asInt = False):
    out = year,month,day = date.split('_')
    if asInt:
        out = (int(entry) for entry in out)
    return(out)

def formatDate(date,dateFormat='Y-M-D'):
    # Accepts date as 'YYYY_MM_DD'!
    year,month,day = splitFormatted(date)

    date = dateFormat.replace('Y','{yearFrm}')
    date = date.replace('M','{monthFrm}')
    date = date.replace('D','{dayFrm}')

    date = date.format(yearFrm = year, monthFrm = month, dayFrm = day)
    return(date)

def todayAsFormatted():
    now = datetime.datetime.now()
    year = now.year
    month = padNumber(now.month,1)
    day = padNumber(now.day,1)

    formatted = "{year}_{month}_{day}".format(year=year,month=month,day=day)
    return(formatted)
