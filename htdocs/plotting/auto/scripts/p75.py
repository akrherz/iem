import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import psycopg2.extras
import numpy as np
from pyiem import network
import matplotlib.patheffects as PathEffects
import datetime
from scipy import stats
import pandas as pd

PDICT2 = {'winter': 'Winter (Dec, Jan, Feb)',
          'spring': 'Spring (Mar, Apr, May)',
          'summer': 'Summer (Jun, Jul, Aug)',
          'fall': 'Fall (Sep, Oct, Nov)',
          'all': 'Entire Year'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """Simple plot of seasonal/yearly precipitation totals.
    """
    d['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station'),
        dict(type='select', name='season', default='winter',
             label='Select Season:', options=PDICT2),
        dict(type="year", name="year", default=1893,
             label="Start Year of Plot"),
    ]
    return d


def plotter(fdict):
    """ Go """
    COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'IA0000')
    season = fdict.get('season', 'winter')
    _ = PDICT2[season]
    startyear = int(fdict.get('year', 1893))

    table = "alldata_%s" % (station[:2],)
    nt = network.Table("%sCLIMATE" % (station[:2],))

    ccursor.execute("""
      SELECT extract(year from day + '%s month'::interval) as yr,
      sum(case when month in (12, 1, 2)
      then precip else 0 end) as winter,
      sum(case when month in (3, 4, 5)
      then precip else 0 end) as spring,
      sum(case when month in (6, 7, 8)
      then precip else 0 end) as summer,
      sum(case when month in (9, 10, 11)
      then precip else 0 end) as fall,
      sum(precip) as all
      from """ + table + """ WHERE station = %s GROUP by yr ORDER by yr ASC
    """, (1 if season != 'all' else 0, station))

    thisyear = datetime.datetime.now().year
    rows = []
    for row in ccursor:
        if row['yr'] == thisyear or row['yr'] < startyear:
            continue
        rows.append(dict(year=int(row['yr']), data=float(row[season])))
    df = pd.DataFrame(rows)

    data = np.array(df['data'])
    years = np.array(df['year'])

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
    ax.text(0.01, 0.99, "Avg: %.2f, slope: %.2f inch/century, R$^2$=%.2f" % (
            avgv, h_slope * 100., r_value ** 2),
            transform=ax.transAxes, va='top', bbox=dict(color='white'))
    ax.set_xlabel("Year")
    ax.set_xlim(min(years)-1, max(years)+1)
    ax.set_ylim(0, max(data) + max(data)/10.)
    ax.set_ylabel("Precipitation [inches]")
    ax.grid(True)
    msg = ("[%s] %s %.0f-%.0f Precipitation [%s] "
           ) % (station, nt.sts[station]['name'],
                min(years), max(years),  PDICT2[season])
    tokens = msg.split()
    sz = len(tokens) / 2
    ax.set_title(" ".join(tokens[:sz]) + "\n" + " ".join(tokens[sz:]))
    ax.legend(ncol=1)

    return fig, df
