"""Snow depth."""
import datetime

import numpy as np
import matplotlib.colors as mpcolors
from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable
from pyiem.plot.use_agg import plt
from pyiem.plot.colormaps import nwssnow
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

LEVELS = [0.1, 1, 2, 3, 4, 6, 8, 12, 18, 24, 30, 36]


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['description'] = """This chart presents the daily snow depth reports
    as a image.  Each box represents an individual day's report with the
    color denoting the amount.  Values in light gray are missing in the
    database."""
    today = datetime.datetime.today()
    lyear = today.year if today.month > 8 else (today.year - 1)
    desc['arguments'] = [
        dict(type='station', name='station', default='IATDSM',
             label='Select Station:', network='IACLIMATE'),
        dict(type='year', name='syear', default=1893, min=1893,
             label='Start Year (inclusive):'),
        dict(type='year', name='eyear', default=lyear,
             min=1893, label='End Year (inclusive):'),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn('coop')
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']
    nt = NetworkTable(ctx['network'])
    ab = nt.sts[station]['archive_begin']
    if ab is None:
        raise NoDataFound("Unknown station metadatab.")
    syear = max([ctx['syear'], ab.year])
    eyear = ctx['eyear']
    sts = datetime.date(syear, 11, 1)
    ets = datetime.date(eyear + 1, 6, 1)

    table = "alldata_%s" % (station[:2],)
    eyear = datetime.datetime.now().year
    obs = np.ma.ones((eyear - syear + 1, 183), 'f') * -1

    df = read_sql("""
        SELECT year, extract(doy from day) as doy, snowd, day,
        case when month < 6 then year - 1 else year end as winter_year
        from """+table+"""
        WHERE station = %s and
        month in (11, 12, 1, 2, 3, 4) and snowd >= 0 and day between %s and %s
    """, pgconn, params=(station, sts, ets), index_col='day')
    if df.empty:
        raise NoDataFound("No Data Found.")
    minyear = df['year'].min()
    maxyear = df['year'].max()
    for _, row in df.iterrows():
        doy = row['doy'] if row['doy'] < 180 else (row['doy'] - 365)
        obs[int(row['winter_year']) - syear, int(doy) + 61] = row['snowd']

    obs.mask = np.where(obs < 0, True, False)
    # obs[obs == 0] = -1

    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_axes([0.1, 0.1, 0.93, 0.8])
    ax.set_xticks((0, 29, 60, 91, 120, 151, 181))
    ax.set_xticklabels(['Nov 1', 'Dec 1', 'Jan 1', 'Feb 1', 'Mar 1', 'Apr 1',
                        'May 1'])
    ax.set_ylabel('Year of Nov,Dec of Season Labeled')
    ax.set_xlabel('Date of Winter Season')
    ax.set_title(('[%s] %s\nDaily Snow Depth (%s-%s) [inches]'
                 '') % (station, nt.sts[station]['name'], minyear, eyear))

    cmap = nwssnow()
    norm = mpcolors.BoundaryNorm(LEVELS, cmap.N)
    cmap.set_bad('#EEEEEE')
    cmap.set_under('white')
    res = ax.imshow(obs, aspect='auto', rasterized=True, norm=norm,
                    interpolation='nearest', cmap=cmap,
                    extent=[0, 182, eyear+1-0.5, syear-0.5])
    fig.colorbar(res, spacing='proportional', ticks=LEVELS, extend='max')
    ax.grid(True)
    ax.set_ylim(maxyear + 0.5, minyear - 0.5)

    return fig, df


if __name__ == '__main__':
    plotter(dict())
