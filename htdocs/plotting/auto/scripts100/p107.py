import psycopg2
from pyiem import network
import numpy as np
from pandas.io.sql import read_sql
import datetime

PDICT = {'avg_temp': 'Average Temperature',
         'precip': 'Total Precipitation'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This plot presents statistics for a period of
    days each year provided your start date and number of days after that
    date. If your period crosses a year bounds, the plotted year represents
    the year of the start date of the period."""
    today = datetime.datetime.today() - datetime.timedelta(days=1)
    d['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station'),
        dict(type='month', name='month',
             default=(today - datetime.timedelta(days=14)).month,
             label='Start Month:'),
        dict(type='day', name='day',
             default=(today - datetime.timedelta(days=14)).day,
             label='Start Day:'),
        dict(type="text", name="days", default="14",
             label="Number of Days"),
        dict(type='select', name='varname', default='avg_temp',
             label='Variable to Compute:', options=PDICT),
        dict(type='year', name='year', default=today.year,
             label="Year to Highlight in Chart:"),
    ]
    return d


def nice(val):
    if val < 0.01 and val > 0:
        return 'Trace'
    return '%.2f' % (val, )


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')

    station = fdict.get('station', 'IA2203')
    days = int(fdict.get('days', 14))
    sts = datetime.date(2012, int(fdict.get('month', 10)),
                        int(fdict.get('day', 1)))
    ets = sts + datetime.timedelta(days=days)
    varname = fdict.get('varname', 'avg_temp')
    year = int(fdict.get('year', datetime.date.today().year))
    table = "alldata_%s" % (station[:2],)
    nt = network.Table("%sCLIMATE" % (station[:2],))
    sdays = []
    for i in range(days):
        ts = sts + datetime.timedelta(days=i)
        sdays.append(ts.strftime("%m%d"))

    doff = (days + 1) if ets.year != sts.year else 0
    df = read_sql("""
    SELECT extract(year from day - '"""+str(doff)+""" days'::interval) as yr,
    avg((high+low)/2.) as avg_temp,
    sum(precip) as precip
    from """ + table + """
    WHERE station = %s and sday in %s
    GROUP by yr ORDER by yr ASC
    """, pgconn, params=(station, tuple(sdays)))

    (fig, ax) = plt.subplots(1, 1, sharex=True)

    bars = ax.bar(df['yr'], df[varname], facecolor='r', edgecolor='r')
    thisvalue = "M"
    for bar, x, y in zip(bars, df['yr'], df[varname]):
        if x == year:
            bar.set_facecolor('g')
            bar.set_edgecolor('g')
            thisvalue = y
    ax.set_xlabel("Year, %s = %s" % (year, nice(thisvalue)))
    ax.axhline(np.average(df[varname]), lw=2,
               label='Avg: %.2f' % (np.average(df[varname]), ))
    ylabel = "Temperature $^\circ$F"
    if varname in ['precip', ]:
        ylabel = "Precipitation [inch]"
    ax.set_ylabel(ylabel)
    ax.set_title(("[%s] %s\n%s between %s and %s"
                  ) % (station, nt.sts[station]['name'], PDICT.get(varname),
                       sts.strftime("%d %b"), ets.strftime("%d %b")))
    ax.grid(True)
    ax.legend(ncol=2, fontsize=10)
    ax.set_xlim(df['yr'].min()-1, df['yr'].max()+1)

    return fig, df
