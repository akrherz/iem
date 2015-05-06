import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import psycopg2.extras
import numpy as np
from pyiem import network
import calendar
import datetime


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['description'] = """This chart produces the daily climatology of
    Growing Degree Days for a location of your choice. """
    d['arguments'] = [
        dict(type='station', name='station', default='IA0200',
             label='Select Station:'),
        dict(type='year', name='year', default='2015', min=1893,
             label='Select Year:'),
        dict(type='text', name='base', default='50',
             label='Enter GDD Base (F):'),
        dict(type='text', name='ceiling', default='86',
             label='Enter GDD Ceiling (F):'),
    ]
    return d


def plotter(fdict):
    """ Go """
    COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'IA0200')
    thisyear = datetime.datetime.now().year
    year = int(fdict.get('year', thisyear))
    base = int(fdict.get('base', 50))
    ceiling = int(fdict.get('ceiling', 86))

    table = "alldata_%s" % (station[:2],)
    nt = network.Table("%sCLIMATE" % (station[:2],))
    syear = max(nt.sts[station]['archive_begin'].year, 1893)
    obs = np.ma.ones(((thisyear+1)-syear, 366), 'f') * -1

    ccursor.execute("""
    SELECT year, extract(doy from day),
    gddxx("""+str(base)+""", """+str(ceiling)+""", high, low)
    from """+table+"""
      WHERE station = %s and year > 1892
    """, (station, ))
    for row in ccursor:
        obs[row[0] - syear, row[1] - 1] = row[2]

    obs.mask = np.where(obs < 0, True, False)

    avg = np.average(obs[:-1, :], 0)
    (fig, ax) = plt.subplots(1, 1)
    ax.plot(np.arange(1, 367), avg, color='r', zorder=2, lw=2.,
            label='Average')
    ax.scatter(np.arange(1, 367), obs[year-syear, :], color='b',  zorder=2,
               label='%s' % (year,))
    p5, p25, p75, p95 = np.percentile(obs[:-1, :], [5, 25, 75, 95], 0)
    ax.bar(np.arange(1, 367), p95 - p5, bottom=p5, ec='tan', fc='tan',
           zorder=1, label='5-95 Percentile')
    ax.bar(np.arange(1, 367), p75 - p25, bottom=p25, ec='lightblue',
           fc='lightblue', zorder=1, label='25-75 Percentile')
    ax.set_xlim(1, 367)
    ax.set_ylim(-0.25, 40)
    ax.grid(True)
    ax.set_title("%s-%s %s [%s]\n%s Daily Growing Degree Days (%s/%s)" % (
                syear, thisyear, nt.sts[station]['name'], station, year,
                base, ceiling))
    ax.set_ylabel("Daily Accumulation $^{\circ}\mathrm{F}$")
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274,
                   305, 335, 365))
    ax.legend(ncol=2)
    ax.set_xticklabels(calendar.month_abbr[1:])

    return fig
