import iemdb
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

maxP = []
maxD = []
maxT = []
maxV = []
maxH = []
minP = []
minT = []
minD = []
minV = []
minH = []

for yr in range(1950,2011):
    v = None
    acursor.execute("""
    select valid, alti, tmpf, extract(doy from valid), sknt,
    extract(hour from valid + '10 minutes'::interval) from t%s 
    where station = 'DSM' and tmpf > -50 and alti > 0 ORDER by alti DESC LIMIT 10
    """ % (yr,))
    for row in acursor:
        if v is None:
            v = row[1]
        if row[1] == v:
            maxP.append( row[1] )
            maxD.append( row[3] )
            maxT.append( row[2] )
            maxV.append( row[4] )
            maxH.append( row[5] )
    v = None
    acursor.execute("""
    select valid, alti, tmpf, extract(doy from valid), sknt,
    extract(hour from valid + '10 minutes'::interval) from t%s 
    where station = 'DSM' and tmpf > -50 and alti > 28.5 ORDER by alti ASC LIMIT 10
    """ % (yr,))
    for row in acursor:
        if v is None:
            v = row[1]
        if v < 28.5:
            print yr, row
        if row[1] == v:
            minP.append( row[1] )
            minD.append( row[3] )
            minT.append( row[2] )
            minV.append( row[4] )
            minH.append( row[5] )
import numpy     
import matplotlib.pyplot as plt
fig = plt.figure(figsize=(6,11))
ax = fig.add_subplot(411)
ax.set_title("Des Moines Yearly Max & Min Altimeter\n[1950-2010] Temp, Wind and Date on ob of Max/Min")

ax.scatter( numpy.array(maxD), numpy.array(maxT), facecolor='b', label='Max')
ax.scatter( numpy.array(minD), numpy.array(minT), facecolor='r', label='Min' )
ax.set_xlim(0,366)
ax.set_ylabel("Air Temperature $^{\circ}\mathrm{F}$")
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.grid(True)
ax.legend(loc=8)

ax = fig.add_subplot(412)
ax.scatter( numpy.array(maxP), numpy.array(maxT), facecolor='b', label='Max')
ax.scatter( numpy.array(minP), numpy.array(minT), facecolor='r', label='Min' )
ax.set_ylabel("Air Temperature $^{\circ}\mathrm{F}$")
ax.grid(True)

ax = fig.add_subplot(413)
ax.scatter( numpy.array(maxP), numpy.array(maxV), facecolor='b', label='Max')
ax.scatter( numpy.array(minP), numpy.array(minV), facecolor='r', label='Min' )
ax.set_ylabel("Wind Speed [knots]")
ax.grid(True)

ax = fig.add_subplot(414)
ax.scatter( numpy.array(maxP), numpy.array(maxH), facecolor='b', label='Max')
ax.scatter( numpy.array(minP), numpy.array(minH), facecolor='r', label='Min' )
ax.set_ylabel("Local Hour of Day")
ax.set_xlabel("Altimeter [inch]")
ax.grid(True)
ax.set_ylim(0,24)
ax.set_yticks( (0,6,12,18))
ax.set_yticklabels( ('Mid', '6 AM', 'Noon', '6 PM'))

fig.savefig('test.ps')
#import iemplot
#iemplot.makefeature('test')    