import psycopg2.extras
import numpy as np
from pyiem import network
import pandas as pd


PDICT = {'max-high': 'Maximum High',
         'avg-high': 'Average High',
         'min-high': 'Minimum High',
         'max-low': 'Maximum Low',
         'avg-low': 'Average Low',
         'min-low': 'Minimum Low',
         'max-precip': 'Maximum Daily Precip',
         'sum-precip': 'Total Precipitation',
         'avg-precip': 'Daily Average Precipitation',
         'avg-precip2': 'Daily Average Precipitation (on wet days)',
         'days-precip': 'Days with Precipitation Above (threshold)',
         'days-high-above':
         'Days with High Temp Greater Than or Equal To (threshold)',
         'days-lows-above':
         'Days with Low Temp Greater Than or Equal To (threshold)',
         'days-lows-below': 'Days with Low Temp Below (threshold)',
         }


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['description'] = """This plot displays a metric for each year.
    In most cases, you can access the raw data for these plots
    <a href="/climodat/" class="link link-info">here.</a>"""
    d['data'] = True
    d['arguments'] = [
        dict(type='station', name='station', default='IA0000',
             label='Select Station'),
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
    COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'IA0000')
    ptype = fdict.get('type', 'max_high')
    threshold = int(fdict.get('threshold', -99))

    table = "alldata_%s" % (station[:2],)
    nt = network.Table("%sCLIMATE" % (station[:2],))

    ccursor.execute("""
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
    sum(case when low < %s then 1 else 0 end) as "days-lows-below",
    avg(precip) as "avg-precip",
    avg(case when precip >= 0.01 then precip else null end) as "avg-precip2",
    sum(case when precip >= %s then 1 else 0 end) as "days-precip"
  from """+table+"""
  where station = %s
  GROUP by year ORDER by year ASC
    """, (threshold, threshold, threshold, threshold, station))

    years = []
    data = []
    for row in ccursor:
        years.append(row['year'])
        data.append(float(row[ptype]))
    df = pd.DataFrame(dict(year=pd.Series(years),
                           data=pd.Series(data)))
    data = np.array(data)

    (fig, ax) = plt.subplots(1, 1)
    avgv = np.average(data)

    # Compute 30 year trailing average
    tavg = [None]*30
    for i in range(30, len(data)):
        tavg.append(np.average(data[i-30:i]))

    a1981_2010 = np.average(data[years.index(1981):years.index(2011)])

    colorabove = 'tomato'
    colorbelow = 'dodgerblue'
    precision = "%.1f"
    if ptype in ['max-precip', 'sum-precip', 'avg-precip', 'avg-precip2',
                 'days-precip']:
        colorabove = 'dodgerblue'
        colorbelow = 'tomato'
        precision = "%.2f"
    bars = ax.bar(np.array(years) - 0.4, data, fc=colorabove, ec=colorabove)
    for i, bar in enumerate(bars):
        if data[i] < avgv:
            bar.set_facecolor(colorbelow)
            bar.set_edgecolor(colorbelow)
    lbl = "Avg: "+precision % (avgv,)
    ax.axhline(avgv, lw=2, color='k', zorder=2, label=lbl)
    lbl = "1981-2010: "+precision % (a1981_2010,)
    ax.axhline(a1981_2010, lw=2, color='brown', zorder=2, label=lbl)
    ax.plot(years, tavg, lw=1.5, color='g', zorder=4, label='Trailing 30yr')
    ax.plot(years, tavg, lw=3, color='yellow', zorder=3)
    ax.set_xlim(years[0] - 1, years[-1] + 1)
    if ptype.find('precip') == -1 and ptype.find('days') == -1:
        ax.set_ylim(min(data) - 5, max(data) + 5)

    ax.set_xlabel("Year")
    units = "$^\circ$F"
    if ptype.find('days') > 0:
        units = "days"
    elif ptype.find('precip') > 0:
        units = "inches"
    ax.set_ylabel("%s [%s]" % (PDICT[ptype], units))
    ax.grid(True)
    ax.legend(ncol=3, loc='best', fontsize=10)
    msg = ("[%s] %s %s-%s %s"
           ) % (station, nt.sts[station]['name'],
                min(years), max(years), PDICT[ptype])
    if ptype.find("days") == 0:
        msg += " (%s)" % (threshold,)
    tokens = msg.split()
    sz = len(tokens) / 2
    ax.set_title(" ".join(tokens[:sz]) + "\n" + " ".join(tokens[sz:]))

    return fig, df
