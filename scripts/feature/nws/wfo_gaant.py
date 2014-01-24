import psycopg2
import datetime
from pyiem.nws import vtec
DBCONN = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
cursor = DBCONN.cursor()

sts = []
ets = []
cursor.execute("""
 SELECT phenomena, significance, eventid, min(issue) as minissue, max(expire) from
 warnings_2014 WHERE wfo = 'DMX' GROUP by phenomena, significance, eventid
 ORDER by minissue ASC
""")

events = []
labels = []
types = []
for row in cursor:
    events.append( (row[3], row[4]) )
    labels.append("%s %s" % (vtec._phenDict[row[0]], 
                              vtec._sigDict[row[1]]))
    types.append("%s.%s" % (row[0], row[1]))

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pytz

(fig, ax) = plt.subplots()

colors = {'BZ.W': '#FF4500', 'WC.Y': '#AFEEEE', 'WW.Y': '#7B68EE',
          'WC.W': '#B0C4DE', 'WC.A': '#5F9EA0', 'ZR.Y': '#DA70D6',
          'FG.Y': '#708090', 'WI.Y': '#D2B48C', 'HW.W': '#DAA520',
          'HW.A': '#B8860B'}

used = []

def get_label(i):
    if types[i] in used:
        return ''
    used.append( types[i] )
    return "%s (%s)" % (labels[i], types[i])

for i, e in enumerate(events):
    secs = abs((e[1]-e[0]).days * 86400.0 + (e[1]-e[0]).seconds)
    ax.barh(i+0.5, secs / 86400.0, left=e[0],
            fc=colors.get(types[i], 'k'),
            ec=colors.get(types[i], 'k'), label=get_label(i))
    print e[1], labels[i], secs
    if e[0].day > 16:
        ax.text(e[0], i+0.5, labels[i].replace("Weather", "Wx"), 
            color=colors.get(types[i], 'k'), ha='right')
    else:
        ax.text(e[0] + datetime.timedelta(seconds=secs), i+0.5, labels[i].replace("Weather", "Wx"), 
            color=colors.get(types[i], 'k'), ha='left')
    
ax.set_ylabel("Sequential Product Number")
ax.set_title("1-23 Jan 2014 NWS Des Moines issued Watch/Warning/Advisories")
ax.legend(loc=2, fontsize=10)
ax.set_ylim(0.4, len(events)+1)
ax.xaxis.set_minor_locator(
                               mdates.DayLocator(interval=1,
                                                 tz=pytz.timezone("America/Chicago"))
                               )
ax.xaxis.set_major_locator(
                               mdates.DayLocator(interval=3,
                                                 tz=pytz.timezone("America/Chicago"))
                               )
ax.xaxis.set_major_formatter(mdates.DateFormatter('%-d %b',
                                                  tz=pytz.timezone("America/Chicago")))

ax.grid(True)

psts = datetime.datetime(2013,12,31,19)
psts = psts.replace(tzinfo=pytz.timezone("America/Chicago"))
pets = datetime.datetime(2014,1,24)
pets = pets.replace(tzinfo=pytz.timezone("America/Chicago"))
ax.set_xlim(psts, pets)
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
