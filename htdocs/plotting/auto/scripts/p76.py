"""Seasonal averages of Humudity"""
import datetime
from collections import OrderedDict

import numpy as np
from scipy import stats
import pandas as pd
from pyiem import meteorology
from pyiem.network import Table as NetworkTable
from pyiem.datatypes import temperature, mixingratio, pressure
from pyiem.util import get_autoplot_context, get_dbconn

MDICT = OrderedDict([
         ('all', 'No Month/Time Limit'),
         ('spring', 'Spring (MAM)'),
         ('spring2', 'Spring (AMJ)'),
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
    desc['description'] = """Simple plot of yearly average dew points by year,
    season, or month.
    This calculation was done by computing the mixing ratio, then averaging
    the mixing ratios by year, and then converting that average to a dew point.
    This was done due to the non-linear nature of dew point when expressed in
    units of temperature.
    """
    desc['arguments'] = [
        dict(type='zstation', name='station', default='DSM',
             label='Select Station', network='IA_ASOS'),
        dict(type='select', name='season', default='winter',
             label='Select Time Period:', options=MDICT),
        dict(type="year", name="year", default=1893,
             label="Start Year of Plot"),
    ]
    return desc


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = get_dbconn('asos')
    cursor = pgconn.cursor()
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']
    network = ctx['network']
    season = ctx['season']
    _ = MDICT[season]
    startyear = ctx['year']

    nt = NetworkTable(network)

    today = datetime.datetime.now()
    lastyear = today.year
    deltadays = 0
    if season == 'all':
        months = range(1, 13)
    elif season == 'spring':
        months = [3, 4, 5]
        if today.month > 5:
            lastyear += 1
    elif season == 'spring2':
        months = [4, 5, 6]
        if today.month > 6:
            lastyear += 1
    elif season == 'fall':
        months = [9, 10, 11]
        if today.month > 11:
            lastyear += 1
    elif season == 'summer':
        months = [6, 7, 8]
        if today.month > 8:
            lastyear += 1
    elif season == 'winter':
        deltadays = 31
        months = [12, 1, 2]
        if today.month > 2:
            lastyear += 1
    else:
        ts = datetime.datetime.strptime("2000-"+season+"-01", '%Y-%b-%d')
        # make sure it is length two for the trick below in SQL
        months = [ts.month, 999]
        lastyear += 1

    cursor.execute("""
      SELECT valid, dwpf from alldata where station = %s and dwpf > -90 and
      dwpf < 100 and extract(month from valid) in %s
    """, (station,  tuple(months)))

    rows = []
    for row in cursor:
        if (row[0].month not in months or row[0].year < startyear or
                row[0].year >= lastyear):
            continue
        yr = (row[0] + datetime.timedelta(days=deltadays)).year
        mxr = meteorology.mixing_ratio(temperature(row[1], 'F')).value('KG/KG')
        rows.append(dict(year=yr, r=mxr))
    df = pd.DataFrame(rows)
    group = df.groupby('year')
    df = group.aggregate(np.average)

    def to_dwpf(val):
        """Unsure why I am doing this, like this"""
        return meteorology.dewpoint_from_pq(pressure(1000, 'MB'),
                                            mixingratio(val, 'KG/KG')
                                            ).value('F')
    df['r'] = df['r'].apply(to_dwpf)
    data = np.array(df['r'])
    years = np.array(df.index.astype('i'))

    (fig, ax) = plt.subplots(1, 1, figsize=(8, 6))
    avgv = np.average(data)

    colorabove = 'seagreen'
    colorbelow = 'lightsalmon'
    cols = ax.bar(years, data, fc=colorabove, ec=colorabove, align='center')
    for i, col in enumerate(cols):
        if data[i] < avgv:
            col.set_facecolor(colorbelow)
            col.set_edgecolor(colorbelow)
    ax.axhline(avgv, lw=2, color='k', zorder=2, label='Average')
    h_slope, intercept, r_value, _, _ = stats.linregress(years, data)
    ax.plot(years, h_slope * np.array(years) + intercept, '--',
            lw=2, color='k', label='Trend')
    ax.text(0.01, 0.98, "Avg: %.1f, slope: %.2f F/century, R$^2$=%.2f" % (
            avgv, h_slope * 100., r_value ** 2),
            transform=ax.transAxes, va='top', bbox=dict(color='white'))
    ax.set_xlabel("Year")
    # ax.set_xlim(min(years)-1, max(years)+1)
    ax.set_ylim(min(data)-5, max(data) + max(data)/10.)
    ax.set_ylabel("Average Dew Point [F]")
    ax.grid(True)
    msg = ("[%s] %s %.0f-%.0f Average Dew Point [%s] "
           ) % (station, nt.sts[station]['name'],
                min(years), max(years),  MDICT[season])
    tokens = msg.split()
    sz = len(tokens) / 2
    ax.set_title(" ".join(tokens[:sz]) + "\n" + " ".join(tokens[sz:]))
    ax.legend(ncol=1, loc=1)

    return fig, df


if __name__ == '__main__':
    plotter(dict())
