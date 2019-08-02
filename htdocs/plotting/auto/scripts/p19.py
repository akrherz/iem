"""histogram"""
import datetime
from collections import OrderedDict

import numpy as np
import pandas as pd
from pandas.io.sql import read_sql
from pyiem import network
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

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
    desc = dict()
    desc['data'] = True
    desc['description'] = """This chart displays a histogram of daily high
    and low temperatures for a station of your choice. If you optionally
    choose to overlay a given year's data and select winter, the year of
    the December is used for the plot. For example, the winter of 2017 is
    Dec 2017 thru Feb 2018.  The plot details the temperature bin with the
    highest frequency."""
    desc['arguments'] = [
        dict(type='station', name='station', default='IA0200',
             label='Select Station:', network='IACLIMATE'),
        dict(type='int', name='binsize', default='10',
             label='Histogram Bin Size:'),
        dict(type='select', name='month', default='all',
             label='Month Limiter', options=MDICT),
        dict(type='year', optional=True, default=datetime.date.today().year,
             label='Optional: Overlay Observations for given year',
             name='year'),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn('coop')
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']
    binsize = ctx['binsize']
    month = ctx['month']
    year = ctx.get('year')
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
    ddf = read_sql("""
        SELECT high, low, year, month from """+table+"""
        WHERE station = %s and year > 1892 and high >= low
        and month in %s
    """, pgconn, params=(station, tuple(months)), index_col=None)
    if ddf.empty:
        raise NoDataFound("No Data Found.")

    bins = np.arange(-40, 121, binsize)

    hist, xedges, yedges = np.histogram2d(ddf['low'], ddf['high'], bins)
    rows = []
    for i, xedge in enumerate(xedges[:-1]):
        for j, yedge in enumerate(yedges[:-1]):
            rows.append(dict(high=yedge, low=xedge, count=hist[i, j]))
    df = pd.DataFrame(rows)
    ab = nt.sts[station]['archive_begin']
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    years = float(
        datetime.datetime.now().year - ab.year
        )
    hist = np.ma.array(hist / years)
    hist.mask = np.where(hist < (1./years), True, False)
    ar = np.argwhere(hist.max() == hist)

    (fig, ax) = plt.subplots(1, 1, figsize=(8, 6))
    res = ax.pcolormesh(xedges, yedges, hist.T)
    fig.colorbar(res, label="Days per Year")
    ax.grid(True)
    ax.set_title(("%s [%s]\n"
                  "Daily High vs Low Temp Histogram (month=%s)"
                  ) % (nt.sts[station]['name'], station, month.upper()))
    ax.set_ylabel(r"High Temperature $^{\circ}\mathrm{F}$")
    ax.set_xlabel(r"Low Temperature $^{\circ}\mathrm{F}$")

    xmax = ar[0][0]
    ymax = ar[0][1]
    ax.text(0.65, 0.15, ("Largest Frequency: %.1f days\n"
                         "High: %.0f-%.0f Low: %.0f-%.0f"
                         ) % (hist[xmax, ymax], yedges[ymax], yedges[ymax+1],
                              xedges[xmax], xedges[xmax+1]),
            ha='center', va='center', transform=ax.transAxes,
            bbox=dict(color='white'))
    ax.axhline(32, linestyle='-', lw=1, color='k')
    ax.text(120, 32, r"32$^\circ$F", va='center', ha='right', color='white',
            bbox=dict(color='k'), fontsize=8)
    ax.axvline(32, linestyle='-', lw=1, color='k')
    ax.text(32, 117, r"32$^\circ$F", va='top', ha='center', color='white',
            bbox=dict(facecolor='k', edgecolor='none'), fontsize=8)
    if year:
        label = str(year)
        if month == 'winter':
            ddf['year'] = ddf[((ddf['month'] == 1) |
                               (ddf['month'] == 2))]['year'] - 1
            label = "Dec %s - Feb %s" % (year, year + 1)
        ddf2 = ddf[ddf['year'] == year]
        ax.scatter(ddf2['low'], ddf2['high'], marker='x', label=label,
                   edgecolor='white', facecolor='red')
        ax.legend()

    return fig, df


if __name__ == '__main__':
    plotter(dict())
