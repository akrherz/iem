import iemdb
import numpy
import iemplot
import mx.DateTime
import random
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()

def figureXY(lon, lat):
    """
    Compute the xy index in the grid of a given point
    """
    dx = (iemplot.MW_EAST - iemplot.MW_WEST) / iemplot.MW_NX
    x = int((lon - iemplot.MW_WEST) / dx )
    dy = (iemplot.MW_NORTH - iemplot.MW_SOUTH) / iemplot.MW_NY
    y = int((iemplot.MW_NORTH - lat) / dy )
    return x, y

def compute(ts0):
    """
    Compute the pressure gradient [mb] around a given time
    """
    icursor.execute("""
    SELECT alti, sknt, (case when gust > sknt then gust else sknt end), 
	x(geom) as lon, 
    y(geom) as lat, network, station from current_log
    WHERE valid BETWEEN %s::timestamp - '8 minutes'::interval and %s::timestamp + '8 minutes'::interval
    and alti > 27 and alti < 32 and network in ('AWOS','IA_ASOS','MN_ASOS',
    'SD_ASOS','WI_ASOS','IL_ASOS','MO_ASOS','KS_ASOS','NE_ASOS')
    """, (ts0.strftime("%Y-%m-%d %H:%M"), ts0.strftime("%Y-%m-%d %H:%M")))
    lats = []
    lons = []
    vals = []
    sknts = []
    useit = []
    for row in icursor:
        vals.append( row[0] * 33.86 )
        sknts.append( row[2] )
        lats.append( row[4] + (0.01 * random.random()) )
        lons.append( row[3] + (0.01 * random.random()) )
        useit.append( row[5] in ('IA_ASOS','AWOS') )
    analysis, res = iemplot.grid_midwest(lons, lats, vals)
    
    rsknt = []
    rpres = []
    for i in range(len(lats)):
        if not useit[i]:
            continue
        lat = lats[i]
        lon = lons[i]
        val = vals[i]
        sknt = sknts[i]
        x,y = figureXY(lon, lat)
        #print x, y, analysis[x-3:x+3,y-3:y+3]
        grad = numpy.max( analysis[x-5:x+5,y-5:y+5] ) - numpy.min( analysis[x-5:x+5,y-5:y+5] )
        #print sknt, grad
        rsknt.append( sknt )
        rpres.append( grad )
    return rsknt, rpres

sts = mx.DateTime.DateTime(2010,10,27,6,0)
ets = mx.DateTime.DateTime(2010,10,27,12,45)
interval = mx.DateTime.RelativeDateTime(minutes=15)
now = sts
pres = []
wind = []
peaks = []
while now < ets:
    print now
    s, p = compute( now )
    for a in s:
        wind.append( a )
    for a in p:
        pres.append( a )
    now += interval
    
import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(111)

ax.scatter( pres, wind, color='b', label='Avg Speed')
#ax.scatter( pres, peaks, color='r', label='Peak Gust')
ax.set_xlabel('Surface Pressure Gradient [mb]')
ax.set_ylabel('Iowa Mean Wind Speed [kts]')
ax.set_title('Iowa Mean Wind Speed v. Pressure Gradient\n25 Oct 2010 12 PM - 26 Oct 2010 1 PM')
ax.legend()
ax.grid(True)
fig.savefig('test.png')
#iemplot.makefeature('test')
