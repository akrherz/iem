"""snow cover coverage"""
import datetime

import numpy as np
import netCDF4
import pandas as pd
from pyiem import iemre
from pyiem.datatypes import distance
from pyiem.util import get_autoplot_context
from pyiem import reference


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    today = datetime.date.today()
    year = today.year if today.month > 9 else today.year - 1
    desc['description'] = """This chart displays estimated areal coverage of
    snow cover for a single state.  This estimate is based on a 0.25x0.25
    degree analysis of NWS COOP observations.  The date shown would represent
    snow depth reported approximately at 7 AM.
    """
    desc['data'] = True
    desc['arguments'] = [
        dict(type='year', name='year', default=year,
             label='Year of December for Winter Season'),
        dict(type='float', name='thres', default='1.0',
             label='Snow Cover Threshold [inch]'),
        dict(type='clstate', name='state', default='IA', label='For State'),
    ]
    return desc


def f(st, snowd, metric, stpts):
    v = np.ma.sum(
        np.ma.where(
            np.ma.logical_and(st > 0, snowd >= metric), 1, 0)
                  ) / float(stpts) * 100.
    return np.nan if v is np.ma.masked else v


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    ctx = get_autoplot_context(fdict, get_description())
    year = ctx['year']
    thres = ctx['thres']
    metric = distance(thres, 'IN').value('MM')
    state = ctx['state'][:2]

    nc2 = netCDF4.Dataset("/mesonet/data/iemre/state_weights.nc")
    st = nc2.variables[state][:]
    stpts = np.sum(np.where(st > 0, 1, 0))
    nc2.close()

    sts = datetime.datetime(year, 10, 1)
    ets = datetime.datetime(year + 1, 5, 1)
    rows = []

    sidx = iemre.daily_offset(sts)
    nc = netCDF4.Dataset('/mesonet/data/iemre/%s_mw_daily.nc' % (sts.year, ))
    snowd = nc.variables['snowd_12z'][sidx:, :, :]
    nc.close()
    for i in range(snowd.shape[0]):
        rows.append({
            'valid': sts + datetime.timedelta(days=i),
            'coverage': f(st, snowd[i], metric, stpts),
                     })

    eidx = iemre.daily_offset(ets)
    nc = netCDF4.Dataset('/mesonet/data/iemre/%s_mw_daily.nc' % (ets.year, ))
    snowd = nc.variables['snowd_12z'][:eidx, :, :]
    nc.close()
    for i in range(snowd.shape[0]):
        rows.append({
         'valid': datetime.date(ets.year, 1, 1) + datetime.timedelta(days=i),
         'coverage': f(st, snowd[i], metric, stpts),
                     })
    df = pd.DataFrame(rows)
    df = df[np.isfinite(df['coverage'])]

    (fig, ax) = plt.subplots(1, 1, sharex=True, figsize=(8, 6))
    ax.bar(df['valid'].values, df['coverage'].values, fc='tan', ec='tan',
           align='center')
    ax.set_title(("IEM Estimated Areal Snow Coverage Percent of %s\n"
                  " percentage of state reporting at least  %.2fin snow"
                  " cover"
                  ) % (reference.state_names[state], thres))
    ax.set_ylabel("Areal Coverage [%]")
    ax.xaxis.set_major_locator(mdates.DayLocator([1, 15]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%-d %b\n%Y"))
    ax.set_yticks(range(0, 101, 25))
    ax.grid(True)

    return fig, df


if __name__ == '__main__':
    fig, df = plotter(dict())
    # print df['coverage'].max()
