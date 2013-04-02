""" Create a simple prinout of observation quanity in the database """
import datetime
now = datetime.datetime.utcnow()
import numpy
counts = numpy.zeros((120,12))
mslp = numpy.zeros((120,12))
metar = numpy.zeros((120,12))

import iemdb
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

import sys
stid = sys.argv[1]

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

acursor.execute("""SELECT extract(year from valid) as yr,
 extract(month from valid) as mo, count(*),
 sum(case when mslp is null or mslp < 1 then 1 else 0 end),
 sum(case when metar is null or metar = '' then 1 else 0 end)
 from alldata WHERE
 station = %s GROUP by yr, mo ORDER by yr ASC, mo ASC""", (stid,))

for row in acursor:
    counts[int(row[0]-1900),int(row[1]-1)] = row[2]
    mslp[int(row[0]-1900),int(row[1]-1)] = row[3]
    metar[int(row[0]-1900),int(row[1]-1)] = row[4]
    

def d(hits, total):
    if total == 0:
        return " N/A"
    val = hits / float(total)
    c1 = bcolors.ENDC
    if val > 0.5:
        c1 = bcolors.FAIL
    return "%s%.2f%s" % (c1, val, bcolors.ENDC)

print 'Observation Count For %s' % (stid,)
print 'YEAR  JAN  FEB  MAR  APR  MAY  JUN  JUL  AUG  SEP  OCT  NOV  DEC'
output = False
for i in range(120):
    year = 1900 + i
    if year > now.year:
        continue
    if not output and numpy.max(counts[i,:]) == 0:
        continue
    output = True
    
    if len(sys.argv) < 3:
        print "%s %4i %4i %4i %4i %4i %4i %4i %4i %4i %4i %4i %4i" % (year,
                counts[i,0],counts[i,1],counts[i,2],counts[i,3],
                counts[i,4],counts[i,5],counts[i,6],counts[i,7],
                counts[i,8],counts[i,9],counts[i,10],counts[i,11])
    else:
        if sys.argv[2] == 'metar':
            data = metar
        else:
            data = mslp
        print "%s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s" % (year,
                d(data[i,0], counts[i,0]),
                d(data[i,1], counts[i,1]),
                d(data[i,2], counts[i,2]),
                d(data[i,3], counts[i,3]),
                d(data[i,4], counts[i,4]),
                d(data[i,5], counts[i,5]),
                d(data[i,6], counts[i,6]),
                d(data[i,7], counts[i,7]),
                d(data[i,8], counts[i,8]),
                d(data[i,9], counts[i,9]),
                d(data[i,10], counts[i,10]),
                d(data[i,11], counts[i,11]))
