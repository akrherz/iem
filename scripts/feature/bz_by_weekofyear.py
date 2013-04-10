import iemdb
import numpy
import datetime
POSTGIS = iemdb.connect('postgis', bypass=True)
pcursor = POSTGIS.cursor()

pcursor.execute("""
 select d as week, count(*) from (select distinct extract(week from issue) as d, 
 wfo, eventid from warnings where significance = 'W' and phenomena = 'BZ' and 
 substr(ugc,1,2) != 'AK') as foo GROUP by week ORDER by week
""")

def d(v):
    jan1 = datetime.datetime(2001, 1, 1)
    if v < 20:
        newv = jan1 + datetime.timedelta(days=365+(v-1)*7)
    else:
        newv = jan1 + datetime.timedelta(days=(v-1)*7)
    print v, newv
    return newv

weeks = []
data = []
for row in pcursor:
    if row[0] == 53:
        continue
    weeks.append( d(row[0]) )
    data.append( row[1] )

data = numpy.array(data)
    
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
fig = plt.figure()
ax = fig.add_subplot(111)
ax.bar(weeks, data / 8.0, width=7)
ax.grid(True)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
ax.set_title("NWS Blizzard Warnings By Week 1 Nov 2005 - 17 Mar 2013\n(Alaska Excluded)")
ax.set_ylabel("Forecast Office Events per week per year")

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
