import ephem
import datetime
import pytz
import iemdb
import numpy
import matplotlib.patheffects as PathEffects

COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""SELECT valid, high from climate71 where
 station = 'IA8706' """)
climate51 = {}
for row in ccursor:
    lts = row[0]
    climate51[ "%02i%02i" % (  lts.month, lts.day)] = row[1]

ccursor.execute("""SELECT day, high from alldata_ia where
 station = 'IA8706' and month in (2,3,4)""")
data = {}
for row in ccursor:
    lts = row[0]
    data[ "%s%02i%02i" % ( lts.year, lts.month, lts.day)] = row[1]
data['20130328'] = 48
data['20130329'] = 100

years = []
start = []
end = []
for yr in range(1900,2014):
    d1 = ephem.next_equinox(str(yr))
    ts = datetime.datetime.strptime(str(d1), '%Y/%m/%d %H:%M:%S')
    ts = ts.replace(tzinfo=pytz.timezone("UTC"))
    lts = ts.astimezone( pytz.timezone("America/Chicago"))
    
    if (data["%s%02i%02i" % ( lts.year, lts.month, lts.day)] >
        climate51["%02i%02i" % (  lts.month, lts.day)]):
        continue
    years.append( yr )
    lts2 = lts
    print yr,
    print lts,
    while (data["%s%02i%02i" % ( lts2.year, lts2.month, lts2.day)] <
        climate51["%02i%02i" % (  lts2.month, lts2.day)]):
        lts2 -= datetime.timedelta(days=1)
    start.append( int((lts2 + datetime.timedelta(days=1)).strftime("%j")) )
    
    print lts2,
    lts2 = lts
    while (data["%s%02i%02i" % ( lts2.year, lts2.month, lts2.day)] <
        climate51["%02i%02i" % (  lts2.month, lts2.day)]):
        lts2 += datetime.timedelta(days=1)
    end.append( int((lts2).strftime("%j")) )
    print lts2

start = numpy.array(start)
end = numpy.array(end)
years = numpy.array(years)
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1, sharex=True)

bars = ax.bar( years-0.4, end-start, bottom=start, ec='b', fc='b')
bars[-1].set_facecolor('r')
bars[-1].set_edgecolor('r')
for i, yr in enumerate(years):
    if end[i] - start[i] > 15:
        ax.text(yr, end[i], "%s" % (yr,), ha='center', va='bottom',
                rotation=90)

ax.grid(True)
ax.set_xlim(1899.5, 2014.5)
ax.set_yticks([46, 53,60,67,74,81, 88, 95, 102,109])
ax.set_yticklabels(['14 Feb', '21 Feb', '1 Mar', '8 Mar', '15 Mar', '22 Mar', '29 Mar','5 Apr',
                    '12 Apr', '19 Apr'])

ax.set_title("1900-2013 Waterloo Streak of High Temp below Average\nwhen day of spring equinox below average as well")
ax.set_ylabel("Period of Streak")
ax.set_xlabel("*2013 (red) Streak in-progress, should end 29 March")

ax.grid(True)

fig.savefig('test.png')
