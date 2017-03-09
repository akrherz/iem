import psycopg2.extras
import numpy as np
from pyiem import network
import datetime
from collections import OrderedDict
import pandas as pd
from pyiem.util import get_autoplot_context

# Use OrderedDict to keep webform select in this same order!
MDICT = OrderedDict([('all', 'No Month/Season Limit'),
                    ('spring', 'Spring (MAM)'),
                     ('fall', 'Fall (SON)'),
                     ('winter', 'Winter (DJF)'),
                     ('summer', 'Summer (JJA)'),
                     ('jan', 'January'),
                     ('feb', 'February'),
                     ('mar', 'March'),
                     ('apr', 'April'),
                     ('may', 'May'),
                     ('jun', 'June'),
                     ('jul', 'July'),
                     ('aug', 'August'),
                     ('sep', 'September'),
                     ('oct', 'October'),
                     ('nov', 'November'),
                     ('dec', 'December')])


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This chart displays a histogram of daily high
    and low temperatures for a station of your choice."""
    d['arguments'] = [
        dict(type='station', name='station', default='IA0200',
             label='Select Station:', network='IACLIMATE'),
        dict(type='int', name='binsize', default='10',
             label='Histogram Bin Size:'),
        dict(type='select', name='month', default='all',
             label='Month Limiter', options=MDICT),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']
    binsize = ctx['binsize']
    month = ctx['month']
    table = "alldata_%s" % (station[:2],)
    nt = network.Table("%sCLIMATE" % (station[:2],))
    if month == 'all':
        months = range(1, 13)
    elif month == 'fall':
        months = [9, 10, 11]
    elif month == 'winter':
        months = [12, 1, 2]
    elif month == 'spring':
        months = [3, 4, 5]
    elif month == 'summer':
        months = [6, 7, 8]
    else:
        ts = datetime.datetime.strptime("2000-"+month+"-01", '%Y-%b-%d')
        # make sure it is length two for the trick below in SQL
        months = [ts.month, 999]
    ccursor.execute("""
    SELECT high, low from """+table+"""
      WHERE station = %s and year > 1892 and high >= low
      and month in %s
    """, (station, tuple(months)))
    highs = []
    lows = []
    for row in ccursor:
        highs.append(row[0])
        lows.append(row[1])

    bins = np.arange(-20, 121, binsize)

    H, xedges, yedges = np.histogram2d(lows, highs, bins)
    rows = []
    for i, x in enumerate(xedges[:-1]):
        for j, y in enumerate(yedges[:-1]):
            rows.append(dict(high=y, low=x, count=H[i, j]))
    df = pd.DataFrame(rows)
    years = float(
        datetime.datetime.now().year - nt.sts[station]['archive_begin'].year
        )
    H = np.ma.array(H / years)
    H.mask = np.where(H < (1./years), True, False)
    ar = np.argwhere(H.max() == H)

    (fig, ax) = plt.subplots(1, 1, figsize=(8, 6))
    res = ax.pcolormesh(xedges, yedges, H.transpose())
    fig.colorbar(res, label="Days per Year")
    ax.grid(True)
    ax.set_title(("%s [%s]\n"
                  "Daily High vs Low Temp Histogram (month=%s)"
                  ) % (nt.sts[station]['name'], station, month.upper()))
    ax.set_ylabel("High Temperature $^{\circ}\mathrm{F}$")
    ax.set_xlabel("Low Temperature $^{\circ}\mathrm{F}$")

    x = ar[0][0]
    y = ar[0][1]
    ax.text(0.65, 0.15, ("Largest Frequency: %.1f days\n"
                         "High: %.0f-%.0f Low: %.0f-%.0f"
                         ) % (H[x, y], yedges[y], yedges[y+1],
                              xedges[x], xedges[x+1]),
            ha='center', va='center', transform=ax.transAxes,
            bbox=dict(color='white'))
    ax.axhline(32, linestyle='-', lw=1, color='k')
    ax.text(120, 32, "32$^\circ$F", va='center', ha='right', color='white',
            bbox=dict(color='k'), fontsize=8)
    ax.axvline(32, linestyle='-', lw=1, color='k')
    ax.text(32, 120, "32$^\circ$F", va='top', ha='center', color='white',
            bbox=dict(facecolor='k', edgecolor='none'), fontsize=8)

    return fig, df

if __name__ == '__main__':
    plotter(dict())
