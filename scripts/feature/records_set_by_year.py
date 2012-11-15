import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""SELECT year, sday, high, low, precip from alldata_ia
    WHERE station = 'IA2203' and year > 1878 ORDER by day ASC""")

rhigh = {}
rlow = {}
ravgt = {}
rprecip = {}
import mx.DateTime
sts = mx.DateTime.DateTime(2000,1,1)
ets = mx.DateTime.DateTime(2001,1,1)
interval = mx.DateTime.RelativeDateTime(days=1)
now = sts
while now < ets:
    rhigh[now.strftime("%m%d")] = -99
    rlow[now.strftime("%m%d")] = 99
    ravgt[now.strftime("%m%d")] = -99
    rprecip[now.strftime("%m%d")] = 0
    now += interval
    
import numpy
records = numpy.zeros((2013-1879, 4), 'f')

for row in ccursor:
    if row[2] > rhigh[row[1]]:
        rhigh[row[1]] = row[2]
        records[row[0]-1879,0] += 1
    if (row[2] + row[3])/2.0 > ravgt[row[1]]:
        ravgt[row[1]] = (row[2] + row[3]) / 2.0
        records[row[0]-1879,1] += 1
    if row[3] < rlow[row[1]]:
        rlow[row[1]] = row[3]
        records[row[0]-1879,2] += 1
    if row[4] > rprecip[row[1]]:
        rprecip[row[1]] = row[4]
        records[row[0]-1879,3] += 1
        

for year in range(1879,2013):
    print '%s,%s,%s,%s,%s' % (year, records[year-1879,0],records[year-1879,1],
                           records[year-1879,2], records[year-1879,3])
