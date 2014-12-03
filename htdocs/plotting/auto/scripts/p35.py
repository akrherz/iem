import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import psycopg2.extras
import numpy as np
from pyiem import network
import datetime
import calendar
from pyiem.network import Table as NetworkTable


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['cache'] = 86400
    d['arguments'] = [
        dict(type='zstation', name='zstation', default='DSM', label='Select Station:'),
        dict(type='text', name='hours', default=24,
             label='Hours:'),
    ]
    return d

def plotter( fdict ):
    """ Go """
    ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')
    cursor = ASOS.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('zstation', 'AMW')
    network = fdict.get('network', 'IA_ASOS')
    hours = int(fdict.get('hours', 24))

    nt = NetworkTable(network)

    cursor.execute("""
    WITH one as (select valid, tmpf from alldata where
    station = %s and tmpf is not null and tmpf > -50),
    two as (SELECT valid + '%s hours'::interval as v, tmpf from alldata
    where station = %s and tmpf is not null and tmpf > -50)
    
    SELECT extract(week from one.valid), two.tmpf - one.tmpf from one JOIN two
    on (one.valid = two.v)
    """, (station, hours, station))
    weeks = []
    deltas = []
    for row in cursor:
        weeks.append( row[0] )
        deltas.append( row[1] )

    sts = datetime.datetime(2012,1,1)
    xticks = []
    for i in range(1,13):
        ts = sts.replace(month=i)
        xticks.append(int(ts.strftime("%j")))


    bins = np.arange(-79, 80, 2)
        
    H, xedges, yedges = np.histogram2d(weeks, deltas, [range(0,54), bins])
    years = float( 
        datetime.datetime.now().year - nt.sts[station]['archive_begin'].year
        )
    H = np.ma.array(H / years)
    H.mask = np.where(H < (1./years), True, False)
        
    (fig, ax) = plt.subplots(1,1)
    res = ax.pcolormesh((xedges -1) * 7, yedges, H.transpose())
    fig.colorbar( res, label="Hours per Week per Year")
    ax.grid(True)
    ax.set_title("%s [%s]\nHistogram of %s Hour Temperature Change" % (
                nt.sts[station]['name'], station, hours))
    ax.set_ylabel("Temperature Change $^{\circ}\mathrm{F}$")
    
    ax.set_xticks(xticks)
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlim(0,366)

    rng = max([max(deltas),0-min(deltas)])
    ax.set_ylim(0-rng-4,rng+4)
        
    return fig
