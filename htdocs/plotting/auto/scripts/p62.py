import psycopg2.extras
import numpy as np
import datetime
from pyiem.network import Table as NetworkTable


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['description'] = """ """
    d['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station:')
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

    station = fdict.get('station', 'IA2203')

    table = "alldata_%s" % (station[:2],)
    nt = NetworkTable("%sCLIMATE" % (station[:2],))
    syear = nt.sts[station]['archive_begin'].year
    eyear = datetime.datetime.now().year
    obs = np.ma.ones((eyear - syear + 1, 153), 'f') * -1

    cursor.execute("""
     SELECT year, extract(doy from day), snowd from """+table+"""
     WHERE station = %s and
     month in (11,12,1,2,3) and snowd >= 0 and day >= '1893-11-01'
    """, (station,))
    minyear = 2015
    for row in cursor:
        year = row[0]
        if year < minyear:
            minyear = year
        doy = row[1]
        val = row[2]
        if doy > 180:
            doy = doy - 365
        else:
            year -= 1
        obs[year-syear, doy + 61] = val

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
    ax.set_ylim(top=minyear)

    return fig
