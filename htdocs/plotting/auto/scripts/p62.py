import psycopg2.extras
import numpy as np
import datetime
from pyiem.network import Table as NetworkTable
from pyiem.util import get_autoplot_context


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['description'] = """This chart presents the daily snow depth reports
    as a image.  Each box represents an individual day's report with the
    color denoting the amount.  Values in light gray are missing in the
    database."""
    today = datetime.datetime.today()
    lyear = today.year if today.month > 8 else (today.year - 1)
    d['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station:', network='IACLIMATE'),
        dict(type='year', name='syear', default=1893, min=1893,
             label='Start Year (inclusive):'),
        dict(type='year', name='eyear', default=lyear,
             min=1893, label='End Year (inclusive):'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.colors as mpcolors
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']
    syear = ctx['syear']
    eyear = ctx['eyear']
    sts = datetime.date(syear, 11, 1)
    ets = datetime.date(eyear + 1, 6, 1)

    table = "alldata_%s" % (station[:2],)
    nt = NetworkTable("%sCLIMATE" % (station[:2],))
    syear = nt.sts[station]['archive_begin'].year
    eyear = datetime.datetime.now().year
    obs = np.ma.ones((eyear - syear + 1, 153), 'f') * -1

    cursor.execute("""
     SELECT year, extract(doy from day), snowd, day from """+table+"""
     WHERE station = %s and
     month in (11,12,1,2,3) and snowd >= 0 and day between %s and %s
    """, (station, sts, ets))
    minyear = 2050
    maxyear = 1900
    for row in cursor:
        year = row[0]
        if year < minyear:
            minyear = year
        if row[3].month > 6 and year > maxyear:
            maxyear = year
        doy = row[1]
        val = row[2]
        if doy > 180:
            doy = doy - 365
        else:
            year -= 1
        obs[year-syear, int(doy + 61)] = val

    obs.mask = np.where(obs < 0, True, False)
    # obs[obs == 0] = -1

    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111)
    ax.set_xticks((0, 29, 60, 91, 120, 151))
    ax.set_xticklabels(('Nov 1', 'Dec 1', 'Jan 1', 'Feb 1', 'Mar 1', 'Apr 1'))
    ax.set_ylabel('Year of Nov,Dec of Season Labeled')
    ax.set_xlabel('Date of Winter Season')
    ax.set_title(('[%s] %s\nDaily Snow Depth (%s-%s) [inches]'
                 '') % (station, nt.sts[station]['name'], minyear, eyear))

    cmap = plt.get_cmap("jet")
    norm = mpcolors.BoundaryNorm([0.01, 0.1, 1, 2, 3, 4, 5, 6, 9, 12,
                                  15, 18, 21, 24, 30, 36],
                                 cmap.N)
    cmap.set_bad('#EEEEEE')
    cmap.set_under('white')
    res = ax.imshow(obs, aspect='auto', rasterized=True, norm=norm,
                    interpolation='nearest', cmap=cmap,
                    extent=[0, 152, eyear+1-0.5, syear-0.5])
    fig.colorbar(res)
    ax.grid(True)
    ax.set_ylim(maxyear + 0.5, minyear - 0.5)

    return fig

if __name__ == '__main__':
    plotter(dict())
