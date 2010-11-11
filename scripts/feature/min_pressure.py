import iemdb
import numpy
import iemplot
import mx.DateTime
import random
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()

def compute(ts0):
    """
    Compute the pressure gradient [mb] around a given time
    """
    icursor.execute("""
    SELECT alti, valid, station, sknt, (case when gust > sknt then gust else sknt end), 
	x(geom) as lon, 
    y(geom) as lat, network, station from current_log
    WHERE valid BETWEEN %s::timestamp - '8 minutes'::interval and %s::timestamp + '8 minutes'::interval
    and alti > 27 and alti < 32 and network in ('AWOS','IA_ASOS'
    'MO_ASOS','KS_ASOS','NE_ASOS'
     ) ORDER by alti ASC LIMIT 1
    """, (ts0.strftime("%Y-%m-%d %H:%M"), ts0.strftime("%Y-%m-%d %H:%M")))
    lats = []
    lons = []
    vals = []
    sknt = []
    peak = 0
    mxp = 0
    mnp = 19999
    for row in icursor:
        print row[2], row[1], row[0]
        continue
        p = row[0] * 33.86
        if p > mxp:
        	mxp = p
        if p < mnp:
            mnp = p
        vals.append( row[0] * 33.86 )
        sknt.append( row[1] )
        if row[2] > peak and row[5] in ['IA_ASOS','AWOS']:
            peak = row[2]
        lats.append( row[4] + (0.01 * random.random()) )
        lons.append( row[3] - (0.001 * random.random()) )
    #analysis, res = iemplot.grid_midwest(lons, lats, vals)
    #v0 = numpy.min(analysis)
    #v1 = numpy.max(analysis)
    #analysis, res = iemplot.grid_midwest(lons, lats, sknt)
    #s = numpy.average(analysis)
    return mnp

sts = mx.DateTime.DateTime(2010,10,25,12,0)
ets = mx.DateTime.DateTime(2010,10,27,0,15)
interval = mx.DateTime.RelativeDateTime(minutes=15)
now = sts
pmins = []
pmaxs = []
sknt = []
while now < ets:
    pmin = compute( now )
    pmins.append( pmin )
    #pmaxs.append( pmax )
    #sknt.append( s )
    now += interval
    
import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(111)

ax.plot( numpy.arange(len(pmins)), pmins, color='b')
rate = (955. - 981.) / (19.5)
ax.plot( (16,55), (981,955), color='r' , label='%.2f mb/hr Rate' % (rate,))
#ax.plot( numpy.arange(len(pmaxs)), pmaxs, color='b', label='Minimum')
#ax.set_xlabel('Surface Pressure Gradient [mb]')
#ax.set_ylabel('Iowa Mean Wind Speed [kts]')
#ax.set_title('Iowa Mean Wind Speed v. Pressure Gradient\n25 Oct 2010 12 PM - 26 Oct 2010 1 PM')
ax.legend()
ax.set_title("Upper MidWest Minimum Station Altimeter\nMin IEM Captured Ob: KFOZ Bigfork, MN 28.20in PMSL 955.2mb 5:13 PM")
ax.set_xticks( numpy.arange(0,74,12) )
ax.set_xlim(0,len(pmins))
ax.set_ylabel("Pressure Altimeter [mb]")
ax.set_xticklabels( ('Noon\n25 Oct', '6 PM', 'Mid\n26 Oct', '6 AM', 'Noon', '6 PM', 'Mid\n27 Oct') )
ax.grid(True)
fig.savefig('test.ps')
iemplot.makefeature('test')
