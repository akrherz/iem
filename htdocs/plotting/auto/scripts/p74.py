import psycopg2.extras
import numpy as np
from pyiem import network
import datetime
from scipy import stats
import pandas as pd

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
    COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)

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

    ccursor.execute("""
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
      from """ + table + """ WHERE station = %s GROUP by yr ORDER by yr ASC
    """, (1 if season != 'all' else 0, station))

    thisyear = datetime.datetime.now().year
    rows = []
    for row in ccursor:
        if row['yr'] == thisyear or row['yr'] < startyear:
            continue
        rows.append(dict(year=int(row['yr']), data=int(row[season])))
    df = pd.DataFrame(rows)

    (fig, ax) = plt.subplots(1, 1)
    avgv = np.average(df['data'])

    colorabove = 'r'
    colorbelow = 'b'
    if direction == 'below':
        colorabove = 'b'
        colorbelow = 'r'
    bars = ax.bar(df['year'] - 0.4, df['data'], fc=colorabove, ec=colorabove)
    for i, bar in enumerate(bars):
        if df['data'][i] < avgv:
            bar.set_facecolor(colorbelow)
            bar.set_edgecolor(colorbelow)
    ax.axhline(avgv, lw=2, color='k', zorder=2, label='Average')
    h_slope, intercept, r_value, _, _ = stats.linregress(df['year'],
                                                         df['data'])
    ax.plot(df['year'], h_slope * np.array(df['year']) + intercept, '--',
            lw=2, color='k', label='Trend')
    ax.text(0.01, 0.99, "Avg: %.1f, slope: %.2f days/century, R$^2$=%.2f" % (
            avgv, h_slope * 100., r_value ** 2),
            transform=ax.transAxes, va='top', bbox=dict(color='white'))
    ax.set_xlabel("Year")
    ax.set_xlim(min(df['year'])-1, max(df['year'])+1)
    ax.set_ylim(0, max([max(df['data']) + max(df['data'])/7., 3]))
    ax.set_ylabel("Number of Days")
    ax.grid(True)
    msg = ("[%s] %s %.0f-%.0f Number of Days [%s] "
           "with %s %s %g%s"
           ) % (station, nt.sts[station]['name'],
                min(df['year']), max(df['year']),  PDICT2[season],
                PDICT3[varname], PDICT[direction],
                threshold, "$^\circ$F" if varname != 'precip' else 'inch')
    tokens = msg.split()
    sz = len(tokens) / 2
    ax.set_title(" ".join(tokens[:sz]) + "\n" + " ".join(tokens[sz:]))
    ax.legend(ncol=1)

    return fig, df
