import datetime
events = [
    [0, "?", datetime.datetime(2013,2,21)],
    [0.27, 6.8, datetime.datetime(2013,1,30)],
    [0.37, 4.5, datetime.datetime(2012,2,4)],
    [0.59, 7.1, datetime.datetime(2011,1,10)],
    [0.28, 6.4, datetime.datetime(2010,1,25)],
    [0.97, 15.5, datetime.datetime(2009,12,8)],
    [0.27, 7.6, datetime.datetime(2009,2,13)],
          ]
import numpy as np
import numpy.ma as npma
import iemdb
MOS = iemdb.connect('mos', bypass=True)
mcursor = MOS.cursor()
import pytz
import matplotlib.pyplot as plt
(fig, ax) = plt.subplots(1,1)
ys = 1.0
ylabels = []
for (precip,snow, sts) in events:
    sts = sts.replace(tzinfo=pytz.timezone("UTC"))
    mcursor.execute("""
    select runtime, sum(precip) from model_gridpoint_%s 
    where station = 'KDSM' and model = 'GFS' and 
    ftime BETWEEN '%s 00:00+00' and '%s 00:00+00' and
    runtime < '%s 00:00+00' GROUP by runtime ORDER by runtime
    """ % (sts.year, sts.strftime("%Y-%m-%d"),
           (sts + datetime.timedelta(days=2)).strftime("%Y-%m-%d"),
           sts.strftime("%Y-%m-%d")))
    x = []
    y = []
    bottom = []
    for row in mcursor:
        delta = (sts - row[0]).days * 86400 + (sts - row[0]).seconds
        delta = delta /  (6*3600.0)
        if row[1] is not None:
            x.append( 0 - delta )
            y.append( row[1] / 25.4 )
            bottom.append( ys )
        print delta, row[0], row[1], precip
    x.append( 0 )
    y.append( precip )
    bottom.append( ys )
    x = np.array( x)
    y = npma.array( y) / (npma.max(y) * 1.1)
    bottom = np.array( bottom )
    bars = ax.bar(x-0.4, y, bottom=bottom)
    bars[-1].set_facecolor('r')
    ylabels.append(" %s\n%s in" % (sts.strftime("%-d %b %Y"), snow))
    
    ys += 1
    
for i in range(-13,1):
    ax.text(i, 1.2, '?', ha='center')
    
ax.grid(True)
ax.set_ylim(1,8)
ax.set_xticks(np.arange(-28,1,4))
ax.set_xticklabels([7,6,5,4,3,2,1,'Event'])
ax.set_xlim(-28.5,0.5)
ax.set_yticklabels( ylabels , va='bottom')
ax.set_title("GFS Model Precipitation Forecast for Des Moines\nSuccessive forecasts made prior to recent snowfall events")
ax.set_xlabel("Days prior to event, bars normalized for each event")
fig.tight_layout()
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
