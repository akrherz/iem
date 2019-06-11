"""iemre stuff"""
import datetime

import numpy as np
import matplotlib.dates as mdates
import pandas as pd
import geopandas as gpd
from metpy.units import units
from pyiem import iemre, reference
from pyiem.grid.zs import CachingZonalStats
from pyiem.util import get_autoplot_context, get_dbconn, ncopen
from pyiem.plot.use_agg import plt


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    today = datetime.date.today()
    desc['description'] = """This is a complex plot to describe!  For each
    24 hour period (roughly ending 7 AM), the IEM computes a gridded
    precipitation estimate.  This chart displays the daily coverage of a
    specified intensity for that day.  The chart also compares this coverage
    against the portion of the state that was below a second given threshold
    over X number of days.  This provides some insight into if the
    precipitation fell over locations that needed it.
    """
    desc['data'] = True
    desc['arguments'] = [
        dict(type='year', name='year', default=today.year,
             label='Select Year (1893-)'),
        dict(type='float', name='daythres', default='0.50',
             label='1 Day Precipitation Threshold [inch]'),
        dict(type='int', name='period', default='7',
             label='Over Period of Trailing Days'),
        dict(type='float', name='trailthres', default='0.50',
             label='Trailing Day Precipitation Threshold [inch]'),
        dict(type='state', name='state', default='IA', label='For State'),
    ]
    return desc


def do_date(ctx, now, precip, daythres, trailthres):
    """Do the local date and return a dict"""
    idx = iemre.daily_offset(now)
    sevenday = np.sum(precip[(idx-ctx['period']):idx, :, :], 0)
    ptrail = np.where(ctx['iowa'] > 0, sevenday, -1)
    pday = np.where(ctx['iowa'] > 0, precip[idx, :, :], -1)
    tots = np.sum(np.where(pday >= daythres, 1, 0))
    need = np.sum(np.where(np.logical_and(ptrail < trailthres,
                                          ptrail >= 0), 1, 0))
    htot = np.sum(np.where(np.logical_and(ptrail < trailthres,
                                          pday >= daythres), 1, 0))
    ctx['days'].append(now)
    return dict(day=now.strftime("%Y-%m-%d"),
                coverage=(tots / ctx['iowapts'] * 100.0),
                hits=(htot / ctx['iowapts'] * 100.0),
                efficiency=(htot / need * 100.),
                needed=(need / ctx['iowapts'] * 100.))


def get_data(ctx):
    """Do the processing work, please"""
    pgconn = get_dbconn('postgis')
    states = gpd.GeoDataFrame.from_postgis("""
    SELECT the_geom, state_abbr from states where state_abbr = %s
    """, pgconn, params=(ctx['state'], ), index_col='state_abbr',
                                           geom_col='the_geom')

    with ncopen(iemre.get_daily_ncname(ctx['year'])) as nc:
        precip = nc.variables['p01d']
        czs = CachingZonalStats(iemre.AFFINE)
        hasdata = np.zeros((nc.dimensions['lat'].size,
                            nc.dimensions['lon'].size))
        czs.gen_stats(hasdata, states['the_geom'])
        for nav in czs.gridnav:
            grid = np.ones((nav.ysz, nav.xsz))
            grid[nav.mask] = 0.
            jslice = slice(nav.y0, nav.y0 + nav.ysz)
            islice = slice(nav.x0, nav.x0 + nav.xsz)
            hasdata[jslice, islice] = np.where(
                grid > 0, 1, hasdata[jslice, islice])
        ctx['iowa'] = np.flipud(hasdata)
        ctx['iowapts'] = float(np.sum(np.where(hasdata > 0, 1, 0)))

        now = datetime.datetime(ctx['year'], 1, 1)
        now += datetime.timedelta(days=(ctx['period']-1))
        ets = datetime.datetime(ctx['year'], 12, 31)
        today = datetime.datetime.now()
        if ets > today:
            ets = today - datetime.timedelta(days=1)
        ctx['days'] = []
        rows = []
        trailthres = (
            ctx['trailthres'] * units('inch')).to(units('mm')).magnitude
        daythres = (
            ctx['daythres'] * units('inch')).to(units('mm')).magnitude
        while now < ets:
            rows.append(do_date(ctx, now, precip, daythres, trailthres))
            now += datetime.timedelta(days=1)
    return pd.DataFrame(rows)


def plotter(fdict):
    """ Go """
    ctx = get_autoplot_context(fdict, get_description())
    daythres = ctx['daythres']
    trailthres = ctx['trailthres']
    period = ctx['period']
    state = ctx['state'][:2]
    df = get_data(ctx)

    (fig, ax) = plt.subplots(2, 1, sharex=True, figsize=(10, 7))
    ax[0].bar(ctx['days'], df['coverage'], fc='g', ec='g', zorder=1,
              label='Daily %.2fin' % (daythres, ))
    ax[0].bar(ctx['days'], df['hits'], fc='b', ec='b', zorder=2,
              label='Over "Dry" Areas')
    ax[0].legend(loc=2, ncol=2, fontsize=10)
    ax[0].set_title(("IEM Estimated Areal Coverage Percent of %s\n"
                     " receiving daily %.2fin vs trailing %s day %.2fin"
                     ) % (reference.state_names[state], daythres, period,
                          trailthres))
    ax[0].set_ylabel("Areal Coverage [%]")
    ax[0].grid(True)

    ax[1].bar(ctx['days'], df['needed'], fc='tan', ec='tan', zorder=1)
    ax[1].bar(ctx['days'], df['efficiency'], fc='b', ec='b', zorder=2)
    ax[1].xaxis.set_major_formatter(mdates.DateFormatter('%-d %b\n%Y'))
    ax[1].grid(True)
    ax[1].set_ylabel("Areal Coverage [%]")
    ax[1].set_title(("Percentage of Dry Area (tan) below (%.2fin over %s days)"
                     " got %.2fin precip (blue) that day"
                     ) % (trailthres, period, daythres),
                    fontsize=12)
    return fig, df


if __name__ == '__main__':
    plotter(dict())
