import matplotlib.pyplot as plt
import matplotlib.font_manager 
prop = matplotlib.font_manager.FontProperties(size=8) 
from pyIEM import mesonet
fig = plt.figure(figsize=(8,11))
ax = fig.add_subplot(311)
ax.set_xlim(0,1443)
xticks = []
xticklabels = []
for x in range(0,25,2):
    xticks.append( x * 60 )
    if x == 0 or x == 24:
        lbl = 'Mid'
    elif x == 12:
        lbl = 'Noon'
    else:
        lbl = x % 12
    xticklabels.append(lbl)
ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels)
#ax.set_xlabel("Local Hour of Day [CDT]")
#ax.set_ylabel("Air & Dew Point (dash) Temp [F]", fontsize=9)
ax.set_title("18-20 July 2011 Station Quality Comparison")

import iemdb
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()
acursor2 = ASOS.cursor()

# Extract 100 degree obs
acursor.execute("""
 SELECT distinct date(valid) as d from t2011 WHERE station = 'DSM'
and valid > '2011-07-18' and valid < '2011-07-21' ORDER by d ASC
""")
maxD = 0
colors = ['r','b','green']
diff = 0.0
for row in acursor:
    d = row[0]
    acursor2.execute("""
        SELECT valid, tmpf, p01m, dwpf from t%s WHERE station = 'MIW' and valid BETWEEN
        '%s 00:00' and '%s 23:59'::timestamp + '10 minutes'::interval 
        and tmpf > -50 ORDER by valid ASC
        """ % (d.year, d, d))
    times = []
    tmpf = []
    dwpf = []
    raining = False
    for row2 in acursor2:
        if row2[3] >= maxD and row2[1] >= 100:
            print row2[0], row2[3]
            maxD = row2[3]
        if row2[2] > 0:
            raining = True
        if len(times) > 10 and row2[0].hour == 0:
            times.append( row2[0].hour * 60 + row2[0].minute + 1440)
        else:    
            times.append( row2[0].hour * 60 + row2[0].minute )
        if row2[0].hour == 5:
            tot = row2[3]
        if row2[0].hour == 9:
            tot2 = row2[3]
        tmpf.append( row2[1] )
        dwpf.append( row2[3] )
    diff += tot2 - tot
    #c = '#E8AFAF'
    #if raining:
    #    c = 'b'
    c = colors.pop()
    ax.plot(times, tmpf, c=c, label= d.strftime("%d %B") )
    ax.plot(times, dwpf, linestyle='--', c=c)
ax.text(6*60, 67, "6-10 AM Diff: %.1f$^{\circ}\mathrm{F}$" % ((diff/3.,) ))
ax.text(14*60, 67, "Marshalltown, IA (KMIW ASOS)")
ax.set_ylim(65,100)
ax.grid(True)
ax.legend(loc=2, prop=prop)

#------------------------------------------------------------
ax = fig.add_subplot(312)
ax.set_xlim(0,1443)
xticks = []
xticklabels = []
for x in range(0,25,2):
    xticks.append( x * 60 )
    if x == 0 or x == 24:
        lbl = 'Mid'
    elif x == 12:
        lbl = 'Noon'
    else:
        lbl = x % 12
    xticklabels.append(lbl)
ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels)
ax.set_xlabel("Local Hour of Day [CDT]")
ax.set_ylabel("                               Air & Dew Point (dash) Temperature [F]")


# Extract 100 degree obs
acursor.execute("""
 SELECT distinct date(valid) as d from t2011 WHERE station = 'DSM'
and valid > '2011-07-18' and valid < '2011-07-21' ORDER by d ASC
""")
maxD = 0
diff = 0.0
colors = ['r','b','green']
for row in acursor:
    d = row[0]
    acursor2.execute("""
        SELECT valid, tmpf, p01m, dwpf from t%s WHERE station = 'TNU' and valid BETWEEN
        '%s 00:00' and '%s 23:59'::timestamp + '10 minutes'::interval 
        and tmpf > -50 ORDER by valid ASC
        """ % (d.year, d, d))
    times = []
    tmpf = []
    dwpf = []
    raining = False
    for row2 in acursor2:
        if row2[3] >= maxD and row2[1] >= 100:
            print row2[0], row2[3]
            maxD = row2[3]
        if row2[2] > 0:
            raining = True
        if len(times) > 10 and row2[0].hour == 0:
            times.append( row2[0].hour * 60 + row2[0].minute + 1440)
        else:    
            times.append( row2[0].hour * 60 + row2[0].minute )
        if row2[0].hour == 5:
            tot = row2[3]
        if row2[0].hour == 9:
            tot2 = row2[3]
        tmpf.append( row2[1] )
        dwpf.append( row2[3] )
    diff += tot2 - tot

    #c = '#E8AFAF'
    #if raining:
    #    c = 'b'
    c = colors.pop()
    ax.plot(times, tmpf, c=c, label= d.strftime("%d %B") )
    ax.plot(times, dwpf, linestyle='--', c=c)
ax.plot( [6*60, 10*60, 10*60, 6*60,6*60], [69,75,84,77,69] , c='black')
ax.text(6*60, 66, "6-10 AM Diff: %.1f$^{\circ}\mathrm{F}$" % ((diff/3.,) ))

ax.text(14*60, 66, "Newton, IA (KTNU AWOS)")
ax.grid(True)
ax.legend(loc=2, prop=prop)


#------------------------------------------------------------
ax = fig.add_subplot(313)
ax.set_xlim(0,1443)
ax2 = ax.twinx()
xticks = []
xticklabels = []
for x in range(0,25,2):
    xticks.append( x * 60 )
    if x == 0 or x == 24:
        lbl = 'Mid'
    elif x == 12:
        lbl = 'Noon'
    else:
        lbl = x % 12
    xticklabels.append(lbl)
ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels)
ax.set_xlabel("19 July 2011 [CDT]")
ax.set_ylabel("Relative Humidity [%]")
ax2.set_ylabel("Visibility (dash) [mile]")

colors = ['r','b','green']

for station in ['TNU','MIW']:
    acursor2.execute("""
        SELECT valid, tmpf, p01m, dwpf, vsby from t%s WHERE station = '%s' and valid BETWEEN
        '2011-07-19 00:00' and '2011-07-19 23:59'::timestamp + '10 minutes'::interval 
        and tmpf > -50 ORDER by valid ASC
        """ % (d.year, station))
    times = []
    relh = []
    vsby = []
    raining = False
    for row2 in acursor2:
        if row2[3] >= maxD and row2[1] >= 100:
            print row2[0], row2[3]
            maxD = row2[3]
        if row2[2] > 0:
            raining = True
        if len(times) > 10 and row2[0].hour == 0:
            times.append( row2[0].hour * 60 + row2[0].minute + 1440)
        else:    
            times.append( row2[0].hour * 60 + row2[0].minute )
        if row2[0].hour in [5,9]:
            print row2
        relh.append( mesonet.relh(row2[1], row2[3] ) )
        vsby.append( row2[4] )

    #c = '#E8AFAF'
    #if raining:
    #    c = 'b'
    c = colors.pop()
    ax.plot(times, relh, c=c, label= station )
    ax2.plot(times, vsby, linestyle='--', c=c)
#ax.plot( [6*60, 10*60, 10*60, 6*60,6*60], [69,75,84,77,69] , c='black')
#ax.text(6*60, 66, "6-10 AM Diff: %.1f$^{\circ}\mathrm{F}$" % ((diff/3.,) ))
#
#ax.text(14*60, 66, "Newton, IA (KTNU AWOS)")


ax.grid(True)
ax.legend()



import iemplot
fig.savefig('test.ps')

#iemplot.makefeature('test')
