"""Overcast 2-D Histogram"""
import datetime

import numpy as np
import numpy.ma as ma
import pandas as pd
import matplotlib.colors as mpcolors
from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['cache'] = 86400
    desc['description'] = """This plot presents a 2-D histogram of overcast
    conditions reported by the automated sensor.  Please note that the yaxis
    uses an irregular spacing.
    """
    desc['arguments'] = [
        dict(type='zstation', name='zstation', default='AMW',
             network='IA_ASOS', label='Select Station:'),
        dict(type='cmap', name='cmap', default='jet', label='Color Ramp:'),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn('asos')
    ctx = get_autoplot_context(fdict, get_description())

    station = ctx['zstation']
    network = ctx['network']

    nt = NetworkTable(network)
    df = read_sql("""
        select extract(doy from valid) as doy,
        greatest(skyl1, skyl2, skyl3, skyl4) as sky from alldata
        WHERE station = %s and
        (skyc1 = 'OVC' or skyc2 = 'OVC' or skyc3 = 'OVC' or skyc4 = 'OVC')
        and valid > '1973-01-01' and (extract(minute from valid) = 0 or
        extract(minute from valid) > 50) and report_type = 2
    """, pgconn, params=(station,), index_col=None)
    if df.empty:
        raise ValueError('Error, no results returned!')

    w = np.arange(1, 366, 7)
    z = np.array([100, 200, 300, 400, 500, 600, 700, 800, 900,
                  1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800,
                  1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700,
                  2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600,
                  3700, 3800, 3900, 4000, 4100, 4200, 4300, 4400, 4500,
                  4600, 4700, 4800, 4900, 5000, 5500, 6000, 6500, 7000,
                  7500, 8000, 8500, 9000, 9500, 10000, 11000, 12000, 13000,
                  14000, 15000, 16000, 17000, 18000, 19000, 20000, 21000,
                  22000, 23000, 24000, 25000, 26000, 27000, 28000, 29000,
                  30000, 31000])

    H, xedges, yedges = np.histogram2d(df['sky'].values, df['doy'].values,
                                       bins=(z, w))
    rows = []
    for i, x in enumerate(xedges[:-1]):
        for j, y in enumerate(yedges[:-1]):
            rows.append(dict(ceiling=x, doy=y, count=H[i, j]))
    resdf = pd.DataFrame(rows)

    H = ma.array(H)
    H.mask = np.where(H < 1, True, False)

    (fig, ax) = plt.subplots(1, 1)

    bounds = np.arange(0, 1.2, 0.1)
    bounds = np.concatenate((bounds, np.arange(1.2, 2.2, 0.2)))
    cmap = plt.get_cmap(ctx['cmap'])
    cmap.set_under('#F9CCCC')
    norm = mpcolors.BoundaryNorm(bounds, cmap.N)

    syear = max([1973, nt.sts[station]['archive_begin'].year])
    years = (datetime.date.today().year - syear) + 1.
    c = ax.imshow(
        H / years, aspect='auto', interpolation='nearest', norm=norm,
        cmap=cmap)
    ax.set_ylim(-0.5, len(z)-0.5)
    idx = [0, 4, 9, 19, 29, 39, 49, 54, 59, 64, 69, 74, 79]
    ax.set_yticks(idx)
    ax.set_yticklabels(z[idx])
    ax.set_title(("%s-%s [%s %s Ceilings Frequency\n"
                  "Level at which Overcast Conditions Reported"
                  ) % (syear, datetime.date.today().year, station,
                       nt.sts[station]['name']))
    ax.set_ylabel("Overcast Level [ft AGL], irregular scale")
    ax.set_xlabel("Week of the Year")
    ax.set_xticks(np.arange(1, 55, 7))
    ax.set_xticklabels(('Jan 1', 'Feb 19', 'Apr 8', 'May 27', 'Jul 15',
                        'Sep 2', 'Oct 21', 'Dec 9'))
    b = fig.colorbar(c)
    b.set_label("Hourly Obs per week per year")
    return fig, resdf


if __name__ == '__main__':
    plotter(dict(network='IA_ASOS', station='AMW'))
