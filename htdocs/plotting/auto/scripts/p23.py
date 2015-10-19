import psycopg2.extras
import numpy as np
from pyiem.network import Table as NetworkTable
import datetime


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    year = datetime.date.today().year - 7
    d['description'] = """This plot presents the combination of monthly
    temperature departures and El Nino index values."""
    d['arguments'] = [
        dict(type='station', name='station', default='IA0200',
             label='Select Station:'),
        dict(type='year', name='syear', default=year,
             label='Start Year of Plot', min=1950),
        dict(type='text', name='years', default='8',
             label='Number of Years to Plot'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'IA0000')
    nt = NetworkTable("%sCLIMATE" % (station[:2].upper(),))
    table = "alldata_%s" % (station[:2],)
    syear = int(fdict.get('syear', 2007))
    years = int(fdict.get('years', 8))

    sts = datetime.datetime(syear, 1, 1)
    ets = datetime.datetime(syear+years, 1, 1)
    archiveend = datetime.date.today() + datetime.timedelta(days=1)
    archiveend = archiveend.replace(day=1)

    elnino = []
    elninovalid = []
    cursor.execute("""SELECT anom_34, monthdate from elnino
        where monthdate >= %s and monthdate < %s
        ORDER by monthdate ASC""", (sts, ets))
    for row in cursor:
        elnino.append(float(row[0]))
        elninovalid.append(row[1])

    elnino = np.array(elnino)

    cursor.execute("""
 WITH climo as (
 SELECT month, avg((high+low)/2.) from """+table+""" where station = %s
 and day < %s GROUP by month),

 obs as (
 SELECT year, month, avg((high+low)/2.) from """+table+""" where station = %s
 and day < %s and year >= %s and year < %s GROUP by year, month)

 SELECT obs.year, obs.month, obs.avg - climo.avg from obs JOIN climo on
 (climo.month = obs.month)
 ORDER by obs.year ASC, obs.month ASC

    """, (station, archiveend, station, archiveend, sts.year, ets.year))
    diff = []
    valid = []
    for row in cursor:
        valid.append(datetime.datetime(row[0], row[1], 1))
        diff.append(float(row[2]))

    (fig, ax) = plt.subplots(1, 1)
    ax.set_title(("[%s] %s\nMonthly Departure of Average Temperature + "
                  "El Nino 3.4 Index") % (station, nt.sts[station]['name']))

    xticks = []
    xticklabels = []
    for v in valid:
        if v.month not in [1, 7]:
            continue
        if years > 8 and v.month == 7:
            continue
        if v.month == 1:
            fmt = "%b\n%Y"
        else:
            fmt = "%b"
        xticklabels.append(v.strftime(fmt))
        xticks.append(v)
    while len(xticks) > 9:
        xticks = xticks[::2]
        xticklabels = xticklabels[::2]

    bars = ax.bar(valid, diff, fc='r', ec='r', width=30)
    for bar in bars:
        if bar.get_xy()[1] < 0:
            bar.set_facecolor('b')
            bar.set_edgecolor('b')

    ax2 = ax.twinx()

    ax2.plot(elninovalid, elnino, zorder=2, color='k', lw=2.0)
    ax2.set_ylabel("El Nino 3.4 Index (line)")
    ax2.set_ylim(-3, 3)

    ax.set_ylabel("Avg Temperature Departure [F] (bars)")
    ax.grid(True)
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)
    ax.set_xlim(sts, ets)
    maxv = np.max(np.absolute(diff)) + 2
    ax.set_ylim(0-maxv, maxv)

    return fig
