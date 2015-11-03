import psycopg2
import numpy as np
from pyiem import network
import datetime
from scipy import stats
from pandas.io.sql import read_sql

PDICT = {'above': 'At or Above Threshold',
         'below': 'Below Threshold'}
PDICT2 = {'winter': 'Winter (Dec, Jan, Feb)',
          'spring': 'Spring (Mar, Apr, May)',
          'summer': 'Summer (Jun, Jul, Aug)',
          'fall': 'Fall (Sep, Oct, Nov)',
          'all': 'Entire Year'}
PDICT3 = {'high': 'High Temperature',
          'low': 'Low Temperature',
          'precip': 'Precipitation'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """The number of days for a given season that are
    either above or below some temperature threshold."""
    d['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station'),
        dict(type='select', name='season', default='winter',
             label='Select Season:', options=PDICT2),
        dict(type='select', name='dir', default='below',
             label='Threshold Direction:', options=PDICT),
        dict(type='select', name='var', default='low',
             label='Which Daily Variable:', options=PDICT3),
        dict(type='text', name='threshold', default=0,
             label='Temperature (F) or Precip (in) Threshold:'),
        dict(type="year", name="year", default=1893,
             label="Start Year of Plot"),

    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')

    station = fdict.get('station', 'IA0000')
    season = fdict.get('season', 'winter')
    _ = PDICT2[season]
    direction = fdict.get('dir', 'below')
    _ = PDICT[direction]
    varname = fdict.get('var', 'low')
    _ = PDICT3[varname]
    threshold = float(fdict.get('threshold', 0))
    startyear = int(fdict.get('year', 1893))

    table = "alldata_%s" % (station[:2],)
    nt = network.Table("%sCLIMATE" % (station[:2],))

    b = "%s %s %s" % (varname, ">=" if direction == 'above' else '<',
                      threshold)

    df = read_sql("""
      SELECT extract(year from day + '%s month'::interval) as yr,
      sum(case when month in (12, 1, 2) and """ + b + """
      then 1 else 0 end) as winter,
      sum(case when month in (3, 4, 5) and """ + b + """
      then 1 else 0 end) as spring,
      sum(case when month in (6, 7, 8) and """ + b + """
      then 1 else 0 end) as summer,
      sum(case when month in (9, 10, 11) and """ + b + """
      then 1 else 0 end) as fall,
      sum(case when """ + b + """ then 1 else 0 end) as all
      from """ + table + """ WHERE station = %s and year >= %s
      GROUP by yr ORDER by yr ASC
    """, pgconn, params=(1 if season != 'all' else 0, station, startyear),
                  index_col='yr')

    (fig, ax) = plt.subplots(1, 1)
    avgv = df[season].mean()

    colorabove = 'r'
    colorbelow = 'b'
    if direction == 'below':
        colorabove = 'b'
        colorbelow = 'r'
    bars = ax.bar(df.index.values - 0.4, df[season], fc=colorabove,
                  ec=colorabove)
    for i, bar in enumerate(bars):
        if df[season].values[i] < avgv:
            bar.set_facecolor(colorbelow)
            bar.set_edgecolor(colorbelow)
    ax.axhline(avgv, lw=2, color='k', zorder=2, label='Average')
    h_slope, intercept, r_value, _, _ = stats.linregress(df.index.values,
                                                         df[season])
    ax.plot(df.index.values, h_slope * df.index.values + intercept, '--',
            lw=2, color='k', label='Trend')
    ax.text(0.01, 0.99, "Avg: %.1f, slope: %.2f days/century, R$^2$=%.2f" % (
            avgv, h_slope * 100., r_value ** 2),
            transform=ax.transAxes, va='top', bbox=dict(color='white'))
    ax.set_xlabel("Year")
    ax.set_xlim(df.index.min() - 1, df.index.max() + 1)
    ax.set_ylim(0, max([df[season].max() + df[season].max() / 7., 3]))
    ax.set_ylabel("Number of Days")
    ax.grid(True)
    msg = ("[%s] %s %.0f-%.0f Number of Days [%s] "
           "with %s %s %g%s"
           ) % (station, nt.sts[station]['name'],
                df.index.min(), df.index.max(),  PDICT2[season],
                PDICT3[varname], PDICT[direction],
                threshold, "$^\circ$F" if varname != 'precip' else 'inch')
    tokens = msg.split()
    sz = len(tokens) / 2
    ax.set_title(" ".join(tokens[:sz]) + "\n" + " ".join(tokens[sz:]))
    ax.legend(ncol=1)

    return fig, df
