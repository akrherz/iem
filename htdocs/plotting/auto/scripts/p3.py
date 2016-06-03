import psycopg2
import numpy as np
from pyiem import network
import calendar
import datetime
from pandas.io.sql import read_sql
from collections import OrderedDict

PDICT = OrderedDict([
         ('max-high', 'Maximum High'),
         ('avg-high', 'Average High'),
         ('min-high', 'Minimum High'),
         ('max-low', 'Maximum Low'),
         ('avg-low', 'Average Low'),
         ('min-low', 'Minimum Low'),
         ('avg-temp', 'Average Temp'),
         ('max-precip', 'Maximum Daily Precip'),
         ('sum-precip', 'Total Precipitation'),
         ('days-high-above',
          'Days with High Temp Greater Than or Equal To (threshold)'),
         ('days-high-below', 'Days with High Temp Below (threshold)'),
         ('days-high-above-avg',
          'Days with High Temp Greater Than or Equal To Average'),
         ('days-lows-above',
          'Days with Low Temp Greater Than or Equal To (threshold)'),
         ('days-lows-below', 'Days with Low Temp Below (threshold)'),
         ('days-lows-below-avg', 'Days with Low Temp Below Average')
         ])

MDICT = OrderedDict([
         ('spring', 'Spring (MAM)'),
         ('fall', 'Fall (SON)'),
         ('winter', 'Winter (DJF)'),
         ('summer', 'Summer (JJA)'),
         ('1', 'January'),
         ('2', 'February'),
         ('3', 'March'),
         ('4', 'April'),
         ('5', 'May'),
         ('6', 'June'),
         ('7', 'July'),
         ('8', 'August'),
         ('9', 'September'),
         ('10', 'October'),
         ('11', 'November'),
         ('12', 'December')])


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['highcharts'] = True
    d['description'] = """This plot displays a single month's worth of data
    over all of the years in the period of record.  In most cases, you can
    access the raw data for these plots
    <a href="/climodat/" class="link link-info">here.</a>  For the variables
    comparing the daily temperatures against average, the average is taken
    from the NCEI current 1981-2010 climatology."""
    today = datetime.date.today()
    d['arguments'] = [
        dict(type='station', name='station', default='IA0000',
             label='Select Station'),
        dict(type='select', name='month', default=today.month,
             label='Month/Season', options=MDICT),
        dict(type='select', name='type', default='max-high',
             label='Which metric to plot?', options=PDICT),
        dict(type='text', name='threshold', default='-99',
             label='Threshold (optional, specify when appropriate):'),
    ]
    return d


def highcharts(fdict):
    """Go high charts"""
    ctx = get_context(fdict)
    return """
$("#ap_container").highcharts({
    title: {text: '""" + ctx['title'] + """'},
    subtitle: {text: '""" + ctx['subtitle'] + """'},
    chart: {zoomType: 'x'},
    tooltip: {shared: true},
    xAxis: {title: {text: 'Year'}},
    yAxis: {title: {text: '"""+ctx['ylabel'].replace("$^\circ$", "")+"""'}},
    series: [{
        name: '""" + ctx['ptype'] + """',
        type: 'column',
        width: 0.8,
        pointStart: """ + str(ctx['df'].index.min()) + """,
        pointInterval: 1,
        data: """ + str(ctx['data'].tolist()) + """
        }, {
        tooltip: {
            valueDecimals: 2
        },
        name: '30 Year Trailing Avg',
        pointStart: """ + str(ctx['df'].index.min() + 30) + """,
        pointInterval: 1,
            width: 2,
        data: """ + str(ctx['tavg'][30:]) + """
        },{
            tooltip: {
                valueDecimals: 2
            },
            name: 'Average',
            width: 2,
            pointPadding: 0.1,
            pointStart: """ + str(ctx['df'].index.min()) + """,
            pointInterval: 1,
            data: """ + str([ctx['avgv']] * len(ctx['df'].index)) + """
        }]
});
    """


def get_context(fdict):
    """ Get the context"""
    ctx = dict()
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')

    station = fdict.get('station', 'IA0000')
    month = fdict.get('month', 7)
    ptype = fdict.get('type', 'max-high')
    threshold = int(fdict.get('threshold', -99))

    table = "alldata_%s" % (station[:2],)
    nt = network.Table("%sCLIMATE" % (station[:2],))

    l = "0 days"
    if month == 'fall':
        months = [9, 10, 11]
        label = "Fall (SON)"
    elif month == 'winter':
        months = [12, 1, 2]
        l = "31 days"
        label = "Winter (DJF)"
    elif month == 'spring':
        months = [3, 4, 5]
        label = "Spring (MAM)"
    elif month == 'summer':
        months = [6, 7, 8]
        label = "Summer (JJA)"
    else:
        months = [int(month), ]
        label = calendar.month_name[int(month)]

    df = read_sql("""
    WITH climo as (SELECT to_char(valid, 'mmdd') as sday,
    high, low from ncdc_climate81 WHERE
    station = %s)

    SELECT extract(year from day + '"""+l+"""'::interval)::int as myyear,
    max(o.high) as "max-high",
    min(o.high) as "min-high",
    avg(o.high) as "avg-high",
    max(o.low) as "max-low",
    min(o.low) as "min-low",
    avg(o.low) as "avg-low",
    avg((o.high + o.low)/2.) as "avg-temp",
    max(o.precip) as "max-precip",
    sum(o.precip) as "sum-precip",
    sum(case when o.high >= %s then 1 else 0 end) as "days-high-above",
    sum(case when o.high < %s then 1 else 0 end) as "days-high-below",
    sum(case when o.high >= c.high then 1 else 0 end) as "days-high-above-avg",
    sum(case when o.low >= %s then 1 else 0 end) as "days-lows-above",
    sum(case when o.low < c.low then 1 else 0 end) as "days-lows-below-avg",
    sum(case when o.low < %s then 1 else 0 end) as "days-lows-below"
  from """+table+""" o JOIN climo c on (o.sday = c.sday)
  where station = %s and month in %s
  GROUP by myyear ORDER by myyear ASC
    """, pgconn, params=(nt.sts[station]['ncdc81'], threshold, threshold,
                         threshold, threshold, station, tuple(months)),
                  index_col='myyear')

    data = df[ptype].values
    ctx['data'] = data
    ctx['avgv'] = df[ptype].mean()
    ctx['df'] = df
    # Compute 30 year trailing average
    tavg = [None]*30
    for i in range(30, len(data)):
        tavg.append(np.average(data[i-30:i]))
    ctx['tavg'] = tavg
    # End interval is inclusive
    ctx['a1981_2010'] = df.loc[1981:2010, ptype].mean()
    ctx['ptype'] = ptype
    ctx['station'] = station
    ctx['threshold'] = threshold
    ctx['month'] = month
    ctx['title'] = ("[%s] %s %s-%s"
                    ) % (station, nt.sts[station]['name'],
                         df.index.min(), df.index.max())
    ctx['subtitle'] = ("%s %s"
                       ) % (label, PDICT[ptype])
    if ptype.find("days") == 0 and ptype.find('avg') == -1:
        ctx['subtitle'] += " (%s)" % (threshold,)

    units = "$^\circ$F"
    if ctx['ptype'].find('precip') > 0:
        units = "inches"
    elif ctx['ptype'].find('days') > 0:
        units = "days"
    ctx['ylabel'] = "%s [%s]" % (PDICT[ctx['ptype']], units)
    return ctx


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    ctx = get_context(fdict)

    (fig, ax) = plt.subplots(1, 1)

    colorabove = 'tomato'
    colorbelow = 'dodgerblue'
    precision = "%.1f"
    if ctx['ptype'] in ['max-precip', 'sum-precip']:
        colorabove = 'dodgerblue'
        colorbelow = 'tomato'
        precision = "%.2f"
    bars = ax.bar(ctx['df'].index.values - 0.4, ctx['data'],
                  fc=colorabove, ec=colorabove)
    for i, bar in enumerate(bars):
        if ctx['data'][i] < ctx['avgv']:
            bar.set_facecolor(colorbelow)
            bar.set_edgecolor(colorbelow)
    lbl = "Avg: "+precision % (ctx['avgv'],)
    ax.axhline(ctx['avgv'], lw=2, color='k', zorder=2, label=lbl)
    lbl = "1981-2010: "+precision % (ctx['a1981_2010'],)
    ax.axhline(ctx['a1981_2010'], lw=2, color='brown', zorder=2, label=lbl)
    ax.plot(ctx['df'].index.values, ctx['tavg'], lw=1.5, color='g', zorder=4,
            label='Trailing 30yr')
    ax.plot(ctx['df'].index.values, ctx['tavg'], lw=3, color='yellow',
            zorder=3)
    ax.set_xlim(ctx['df'].index.min() - 1, ctx['df'].index.max() + 1)
    if ctx['ptype'].find('precip') == -1 and ctx['ptype'].find('days') == -1:
        ax.set_ylim(min(ctx['data']) - 5, max(ctx['data']) + 5)

    ax.set_xlabel("Year")
    ax.set_ylabel(ctx['ylabel'])
    ax.grid(True)
    ax.legend(ncol=3, loc='best', fontsize=10)
    ax.set_title("%s\n%s" % (ctx['title'], ctx['subtitle']))

    return fig, ctx['df']
