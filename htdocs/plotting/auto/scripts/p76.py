import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import psycopg2
import numpy as np
from pyiem.network import Table as NetworkTable
import matplotlib.patheffects as PathEffects
import datetime
from scipy import stats
import pandas as pd
from pyiem import meteorology
from pyiem.datatypes import temperature, mixingratio, pressure

PDICT2 = {'winter': 'Winter (Dec, Jan, Feb)',
          'spring': 'Spring (Mar, Apr, May)',
          'summer': 'Summer (Jun, Jul, Aug)',
          'fall': 'Fall (Sep, Oct, Nov)',
          'all': 'Entire Year'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """Simple plot of seasonal or yearly average dew points.
    This calculation was done by computing the mixing ratio, then averaging
    the mixing ratios by year, and then converting that average to a dew point.
    This was done due to the non-linear nature of dew point.
    """
    d['arguments'] = [
        dict(type='zstation', name='station', default='DSM',
             label='Select Station'),
        dict(type='select', name='season', default='winter',
             label='Select Season:', options=PDICT2),
        dict(type="year", name="year", default=1893,
             label="Start Year of Plot"),
    ]
    return d


def plotter(fdict):
    """ Go """
    pgconn = psycopg2.connect(database='asos', host='iemdb', user='nobody')
    cursor = pgconn.cursor()

    station = fdict.get('station', 'DSM')
    network = fdict.get('network', 'IA_ASOS')
    season = fdict.get('season', 'winter')
    _ = PDICT2[season]
    startyear = int(fdict.get('year', 1893))

    nt = NetworkTable(network)

    cursor.execute("""
      SELECT valid, dwpf from alldata where station = %s and dwpf > -90 and
      dwpf < 100
    """, (station, ))

    months = range(1, 13)
    today = datetime.datetime.now()
    lastyear = today.year
    if season == 'spring':
        months = [3, 4, 5]
        if today.month > 5:
            lastyear += 1
    if season == 'fall':
        months = [9, 10, 11]
        if today.month > 11:
            lastyear += 1
    if season == 'summer':
        months = [6, 7, 8]
        if today.month > 8:
            lastyear += 1
    if season == 'winter':
        months = [12, 1, 2]
        if today.month > 2:
            lastyear += 1

    rows = []
    for row in cursor:
        if (row[0].month not in months or row[0].year < startyear or
                row[0].year >= lastyear):
            continue
        yr = (row[0] + datetime.timedelta(days=31)).year
        r = meteorology.mixing_ratio(temperature(row[1], 'F')).value('KG/KG')
        rows.append(dict(year=yr, r=r))
    df = pd.DataFrame(rows)
    group = df.groupby('year')
    df = group.aggregate(np.average)

    def to_dwpf(val):
        return meteorology.dewpoint_from_pq(pressure(1000, 'MB'),
                                            mixingratio(val, 'KG/KG')
                                            ).value('F')
    df['r'] = df['r'].apply(to_dwpf)
    data = np.array(df['r'])
    years = np.array(df.index.astype('i'))

    (fig, ax) = plt.subplots(1, 1)
    avgv = np.average(data)

    colorabove = 'seagreen'
    colorbelow = 'lightsalmon'
    bars = ax.bar(years - 0.4, data, fc=colorabove, ec=colorabove)
    for i, bar in enumerate(bars):
        if data[i] < avgv:
            bar.set_facecolor(colorbelow)
            bar.set_edgecolor(colorbelow)
    ax.axhline(avgv, lw=2, color='k', zorder=2, label='Average')
    h_slope, intercept, r_value, _, _ = stats.linregress(years, data)
    ax.plot(years, h_slope * np.array(years) + intercept, '--',
            lw=2, color='k', label='Trend')
    ax.text(0.01, 0.99, "Avg: %.1f, slope: %.2f F/century, R$^2$=%.2f" % (
            avgv, h_slope * 100., r_value ** 2),
            transform=ax.transAxes, va='top', bbox=dict(color='white'))
    ax.set_xlabel("Year")
    ax.set_xlim(min(years)-1, max(years)+1)
    ax.set_ylim(min(data)-5, max(data) + max(data)/10.)
    ax.set_ylabel("Average Dew Point [F]")
    ax.grid(True)
    msg = ("[%s] %s %.0f-%.0f Average Dew Point [%s] "
           ) % (station, nt.sts[station]['name'],
                min(years), max(years),  PDICT2[season])
    tokens = msg.split()
    sz = len(tokens) / 2
    ax.set_title(" ".join(tokens[:sz]) + "\n" + " ".join(tokens[sz:]))
    ax.legend(ncol=1)

    return fig, df
