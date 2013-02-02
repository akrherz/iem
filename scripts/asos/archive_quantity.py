""" Create a simple prinout of observation quanity in the database """
import datetime
now = datetime.datetime.utcnow()
import numpy
counts = numpy.zeros((120,12))

import iemdb
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

import sys
stid = sys.argv[1]

acursor.execute("""SELECT extract(year from valid) as yr,
 extract(month from valid) as mo, count(*) from alldata WHERE
 station = %s GROUP by yr, mo ORDER by yr ASC, mo ASC""", (stid,))

for row in acursor:
    counts[int(row[0]-1900),int(row[1]-1)] = row[2]
    

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
    
    print "%s %4i %4i %4i %4i %4i %4i %4i %4i %4i %4i %4i %4i" % (year,
                counts[i,0],counts[i,1],counts[i,2],counts[i,3],
                counts[i,4],counts[i,5],counts[i,6],counts[i,7],
                counts[i,8],counts[i,9],counts[i,10],counts[i,11])
