import psycopg2.extras
import datetime
import pandas as pd
import calendar
from pyiem.network import Table as NetworkTable
from pyiem.util import get_autoplot_context

PDICT = {'high': 'High Temperature',
         'low': 'Low Temperature',
         'avg': 'Daily Average Temperature'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This plot presents the daily high, low, or
    average temperature departure.  The average temperature is simply the
    average of the daily high and low."""
    d['arguments'] = [
        dict(type='station', name='station', default='IA0200',
             label='Select Station:', network='IACLIMATE'),
        dict(type='year', name='year', default=datetime.date.today().year,
             label='Year to Plot:'),
        dict(type="select", name='var', default='high', options=PDICT,
             label='Select Variable to Plot'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']
    year = ctx['year']
    varname = ctx['var']

    table = "alldata_%s" % (station[:2],)
    nt = NetworkTable("%sCLIMATE" % (station[:2],))

    cursor.execute("""
    WITH data as (
     select day, high, low, (high+low)/2. as avg, sday
     from """+table+""" where station = %s and year = %s
    ), climo as (
     SELECT valid, high, low, (high+low)/2. as avg from ncdc_climate81
     WHERE station = %s
    )
    SELECT extract(doy from d.day) as doy, d.high - c.high,
    d.low - c.low, d.avg - c.avg, d.high, c.high, d.low, c.low,
    d.avg, c.avg, d.day from
    data d JOIN climo c on
    (to_char(c.valid, 'mmdd') = d.sday) ORDER by doy ASC
    """, (station, year, nt.sts[station]['ncdc81']))

    rows = []
    for row in cursor:
        rows.append(dict(jday=row[0], high_diff=row[1], low_diff=row[2],
                         avg_diff=row[3], high=row[4], climate_high=row[5],
                         low=row[6], climate_low=row[7], avg=row[8],
                         climate_avg=row[9], day=row[10]))
    df = pd.DataFrame(rows)
    (fig, ax) = plt.subplots(1, 1, sharex=True)
    diff = df[varname+'_diff']
    bars = ax.bar(df['jday'], diff,  fc='b', ec='b')
    for i, bar in enumerate(bars):
        if diff[i] > 0:
            bar.set_facecolor('r')
            bar.set_edgecolor('r')
    ax.grid(True)
    ax.set_ylabel("Temperature Departure $^\circ$F")
    ax.set_title(("%s %s\nYear %s %s Departure"
                  ) % (station, nt.sts[station]['name'], year,
                       PDICT[varname]))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274,
                   305, 335, 365))
    ax.set_xlim(0, 366)

    return fig, df
