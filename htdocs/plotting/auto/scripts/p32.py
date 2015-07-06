import psycopg2.extras
import datetime
import pandas as pd
import calendar
from pyiem.network import Table as NetworkTable


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This plot presents the daily high temperature
    departure."""
    d['arguments'] = [
        dict(type='station', name='station', default='IA0200',
             label='Select Station:'),
        dict(type='year', name='year', default=datetime.date.today().year,
             label='Year to Plot:'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'IA0200')
    year = int(fdict.get('year', 2014))

    table = "alldata_%s" % (station[:2],)
    nt = NetworkTable("%sCLIMATE" % (station[:2],))

    cursor.execute("""
    WITH data as (
     select day, high, sday
     from """+table+""" where station = %s and year = %s
    ), climo as (
     SELECT valid, high from ncdc_climate81
     WHERE station = %s
    )
    SELECT extract(doy from d.day) as doy, d.high - c.high from
    data d JOIN climo c on
    (to_char(c.valid, 'mmdd') = d.sday) ORDER by doy ASC
    """, (station, year, nt.sts[station]['ncdc81']))

    jdays = []
    diff = []
    rows = []
    for row in cursor:
        jdays.append(row[0])
        diff.append(row[1])
        rows.append(dict(jday=row[0], diff=row[1]))
    df = pd.DataFrame(rows)
    (fig, ax) = plt.subplots(1, 1, sharex=True)
    bars = ax.bar(jdays, diff,  fc='b', ec='b')
    for i, bar in enumerate(bars):
        if diff[i] > 0:
            bar.set_facecolor('r')
            bar.set_edgecolor('r')
    ax.grid(True)
    ax.set_ylabel("Temperature Departure $^\circ$F")
    ax.set_title(("%s %s\nYear %s Daily High Temperature Departure"
                  ) % (station, nt.sts[station]['name'], year))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274,
                   305, 335, 365))
    ax.set_xlim(0, 366)

    return fig, df
