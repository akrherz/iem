import iemdb
import mx.DateTime
mesosite = iemdb.connect('mesosite', bypass=True)
mcursor = mesosite.cursor()
coop = iemdb.connect('coop', bypass=True)
ccursor = coop.cursor()

el = []
jday27 = []
jday32 = []
mcursor.execute("SELECT extract(year from monthdate) as yr, avg(anom_34) from elnino where extract(month from monthdate) = 8 GROUP by yr ORDER by yr ASC")
for row in mcursor:
    el.append( row[1] )
    
ccursor.execute("SELECT min(extract(doy from day)) as j, year from alldata where stationid = 'ia0200' and month > 6 and low < 27 and year > 1949 GROUP by year ORDER by year ASC")
for row in ccursor:
    jday27.append( row[0] )

ccursor.execute("SELECT min(extract(doy from day)) as j, year from alldata where stationid = 'ia0200' and month > 6 and low < 32 and year > 1949 GROUP by year ORDER by year ASC")
for row in ccursor:
    jday32.append( row[0] )

import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)

ax.scatter( jday27, el, color='b', label="Sub 27")
ax.scatter( jday32, el, color='r', label="Sub 32")
ax.grid(True)
ax.legend()
ax.set_title("Ames First Fall Freezing Temperature + El Nino 3.4 Index [1950-2010]")
ax.set_ylabel("August El Nino 3.4 Index")
ax.set_xlabel("Day of Year")
sts = mx.DateTime.DateTime(2000,9,1)
ets = mx.DateTime.DateTime(2000,12,15)
interval = mx.DateTime.RelativeDateTime(days=1)
now = sts
xticks = []
xticklabels = []
while now < ets:
    if now.day in (1,15):
        xticks.append( int(now.strftime("%j")))
        xticklabels.append( now.strftime("%b %-d"))
    now += interval
ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels)

fig.savefig('test.png')