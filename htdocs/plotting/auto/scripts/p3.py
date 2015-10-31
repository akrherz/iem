import psycopg2
import numpy as np
from pyiem import network
import calendar
from pandas.io.sql import read_sql

PDICT = {'max-high': 'Maximum High',
         'avg-high': 'Average High',
         'min-high': 'Minimum High',
         'max-low': 'Maximum Low',
         'avg-low': 'Average Low',
         'min-low': 'Minimum Low',
         'max-precip': 'Maximum Daily Precip',
         'sum-precip': 'Total Precipitation',
         'days-high-above':
         'Days with High Temp Greater Than or Equal To (threshold)',
         'days-lows-above':
         'Days with Low Temp Greater Than or Equal To (threshold)',
         'days-lows-below': 'Days with Low Temp Below (threshold)',
         }


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This plot displays a single month's worth of data
    over all of the years in the period of record.  In most cases, you can
    access the raw data for these plots
    <a href="/climodat/" class="link link-info">here.</a>"""
    d['arguments'] = [
        dict(type='station', name='station', default='IA0000',
             label='Select Station'),
        dict(type='month', name='month', default='7', label='Month'),
        dict(type='select', name='type', default='max-high',
             label='Which metric to plot?', options=PDICT),
        dict(type='text', name='threshold', default='-99',
             label='Threshold (optional, specify when appropriate):'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')

    station = fdict.get('station', 'IA0000')
    month = int(fdict.get('month', 7))
    ptype = fdict.get('type', 'max_high')
    threshold = int(fdict.get('threshold', -99))

    table = "alldata_%s" % (station[:2],)
    nt = network.Table("%sCLIMATE" % (station[:2],))

    df = read_sql("""
    SELECT year,
    max(high) as "max-high",
    min(high) as "min-high",
    avg(high) as "avg-high",
    max(low) as "max-low",
    min(low) as "min-low",
    avg(low) as "avg-low",
    max(precip) as "max-precip",
    sum(precip) as "sum-precip",
    sum(case when high >= %s then 1 else 0 end) as "days-high-above",
    sum(case when low >= %s then 1 else 0 end) as "days-lows-above",
    sum(case when low < %s then 1 else 0 end) as "days-lows-below"
  from """+table+"""
  where station = %s and month = %s
  GROUP by year ORDER by year ASC
    """, pgconn, params=(threshold, threshold, threshold, station, month),
                  index_col='year')

    (fig, ax) = plt.subplots(1, 1)
    data = df[ptype].values
    avgv = df[ptype].mean()

    # Compute 30 year trailing average
    tavg = [None]*30
    for i in range(30, len(data)):
        tavg.append(np.average(data[i-30:i]))

    # End interval is inclusive
    a1981_2010 = df.loc[1981:2010, ptype].mean()

    colorabove = 'tomato'
    colorbelow = 'dodgerblue'
    precision = "%.1f"
    if ptype in ['max-precip', 'sum-precip']:
        colorabove = 'dodgerblue'
        colorbelow = 'tomato'
        precision = "%.2f"
    bars = ax.bar(df.index.values - 0.4, data, fc=colorabove, ec=colorabove)
    for i, bar in enumerate(bars):
        if data[i] < avgv:
            bar.set_facecolor(colorbelow)
            bar.set_edgecolor(colorbelow)
    lbl = "Avg: "+precision % (avgv,)
    ax.axhline(avgv, lw=2, color='k', zorder=2, label=lbl)
    lbl = "1981-2010: "+precision % (a1981_2010,)
    ax.axhline(a1981_2010, lw=2, color='brown', zorder=2, label=lbl)
    ax.plot(df.index.values, tavg, lw=1.5, color='g', zorder=4,
            label='Trailing 30yr')
    ax.plot(df.index.values, tavg, lw=3, color='yellow', zorder=3)
    ax.set_xlim(df.index.min() - 1, df.index.max() + 1)
    if ptype.find('precip') == -1 and ptype.find('days') == -1:
        ax.set_ylim(min(data) - 5, max(data) + 5)

    ax.set_xlabel("Year")
    units = "$^\circ$F"
    if ptype.find('precip') > 0:
        units = "inches"
    elif ptype.find('days') > 0:
        units = "days"
    ax.set_ylabel("%s [%s]" % (PDICT[ptype], units))
    ax.grid(True)
    ax.legend(ncol=3, loc='best', fontsize=10)
    msg = ("[%s] %s %s-%s %s %s"
           ) % (station, nt.sts[station]['name'],
                df.index.min(), df.index.max(),
                calendar.month_name[month], PDICT[ptype])
    if ptype.find("days") == 0:
        msg += " (%s)" % (threshold,)
    tokens = msg.split()
    sz = len(tokens) / 2
    ax.set_title(" ".join(tokens[:sz]) + "\n" + " ".join(tokens[sz:]))

    return fig, df
