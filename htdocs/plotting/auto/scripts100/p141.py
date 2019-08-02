"""yieldfx plot"""
import calendar
import os
from collections import OrderedDict
import datetime

import pandas as pd
from pyiem.meteorology import gdd
from pyiem.plot.use_agg import plt
from pyiem.datatypes import temperature, distance
from pyiem.util import get_autoplot_context
from pyiem.exceptions import NoDataFound

STATIONS = OrderedDict([
        ('ames', 'Central (Ames)'),
        ('cobs', 'Central (COBS)'),
        ('crawfordsville', 'Southeast (Crawfordsville)'),
        ('kanawha', 'Northern (Kanawha)'),
        ('lewis', 'Southwest (Lewis)'),
        ('mcnay', 'Southern (Chariton/McNay)'),
        ('muscatine', 'Southeast (Muscatine)'),
        ('nashua', 'Northeast (Nashua)'),
        ('sutherland', 'Northwest (Sutherland)')])

PLOTS = OrderedDict([
        ('gdd', 'Growing Degree Days [F]'),
        ('rain', 'Precipitation [in]'),
        ('maxt', 'Daily Maximum Temperature [F]'),
        ('mint', 'Daily Minimum Temperature [F]'),
                     ])


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['description'] = """ """
    desc['arguments'] = [
        dict(type='select', name='location', default='ames',
             label='Select Location:', options=STATIONS),
        dict(type='select', name='ptype', default='gdd',
             label='Select Plot Type:', options=PLOTS),
        dict(type='text', name='sdate', default='mar15',
             label='Start Date:')
    ]
    return desc


def load(dirname, location, sdate):
    """ Read a file please """
    data = []
    idx = []
    mindoy = int(sdate.strftime("%j"))
    fn = "%s/%s.met" % (dirname, location)
    if not os.path.isfile(fn):
        raise NoDataFound("Data file was not found.")
    for line in open(fn):
        line = line.strip()
        if not line.startswith('19') and not line.startswith('20'):
            continue
        tokens = line.split()
        if int(tokens[1]) < mindoy:
            continue
        data.append(tokens)
        ts = (datetime.date(int(tokens[0]), 1, 1) +
              datetime.timedelta(days=int(tokens[1])-1))
        idx.append(ts)
    if len(data[0]) < 10:
        cols = ['year', 'doy', 'radn', 'maxt', 'mint', 'rain']
    else:
        cols = ['year', 'doy', 'radn', 'maxt', 'mint',
                'rain', 'gdd', 'st4', 'st12', 'st24',
                'st50', 'sm12', 'sm24', 'sm50']
    df = pd.DataFrame(data, index=idx,
                      columns=cols)
    for col in cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    if len(data[0]) < 10:
        df['gdd'] = gdd(temperature(df['maxt'].values, 'C'),
                        temperature(df['mint'].values, 'C'))
    df['gddcum'] = df.groupby(['year'])['gdd'].apply(lambda x: x.cumsum())
    df['raincum'] = distance(
        df.groupby(['year'])['rain'].apply(lambda x: x.cumsum()),
        'MM').value('IN')
    return df


def plotter(fdict):
    """ Go """
    ctx = get_autoplot_context(fdict, get_description())

    location = ctx['location']
    ptype = ctx['ptype']
    sdate = datetime.datetime.strptime(ctx['sdate'], '%b%d')
    df = load("/mesonet/share/pickup/yieldfx", location, sdate)
    cdf = load("/opt/iem/scripts/yieldfx/baseline", location, sdate)

    today = datetime.date.today()
    thisyear = df[df['year'] == today.year].copy()
    thisyear.reset_index(inplace=True)
    thisyear.set_index('doy', inplace=True)

    # Drop extra day from cdf during non-leap year
    if today.year % 4 != 0:
        cdf = cdf[cdf['doy'] < 366]
        df = df[df['doy'] < 366]

    # Create a specialized result dataframe for CSV, Excel output options
    resdf = pd.DataFrame(index=thisyear.index)
    resdf.index.name = 'date'
    resdf['doy'] = thisyear.index.values
    resdf.reset_index(inplace=True)
    resdf.set_index('doy', inplace=True)

    # write current year data back to resdf
    for _v, _u in zip(['gddcum', 'raincum'],
                      ['F', 'in']):
        resdf["%s[%s]" % (_v, _u)] = thisyear[_v]
    for _v in ['mint', 'maxt']:
        resdf["%s[F]" % (_v)] = temperature(thisyear[_v].values,
                                            'C').value('F')
    resdf['rain[in]'] = distance(thisyear['rain'], 'MM').value('IN')
    for _ptype, unit in zip(['gdd', 'rain'], ['F', 'in']):
        resdf[_ptype+'cum_climo[%s]' % (unit, )
              ] = cdf.groupby('doy')[_ptype+'cum'].mean()
        resdf[_ptype+'cum_min[%s]' % (unit, )
              ] = df.groupby('doy')[_ptype+'cum'].min()
        resdf[_ptype+'cum_max[%s]' % (unit, )
              ] = df.groupby('doy')[_ptype+'cum'].max()
    for _ptype in ['maxt', 'mint']:
        resdf[_ptype+'_climo[F]'] = temperature(
            cdf.groupby('doy')[_ptype].mean().values, 'C').value('F')
        resdf[_ptype+'_min[F]'] = temperature(
            df.groupby('doy')[_ptype].min().values, 'C').value('F')
        resdf[_ptype+'_max[F]'] = temperature(
            df.groupby('doy')[_ptype].max().values, 'C').value('F')

    (fig, ax) = plt.subplots(1, 1, figsize=(8, 6))
    if ptype in ['gdd', 'rain']:
        ax.plot(thisyear.index.values, thisyear[ptype+'cum'], zorder=4,
                color='b',
                lw=2, label='%s Obs + CFS Forecast' % (today.year,))
        climo = cdf.groupby('doy')[ptype+'cum'].mean()
        ax.plot(climo.index.values, climo.values, lw=2, color='k',
                label="Climatology", zorder=3)
        xrng = df.groupby('doy')[ptype+'cum'].max()
        nrng = df.groupby('doy')[ptype+'cum'].min()
        ax.fill_between(xrng.index.values, nrng.values, xrng.values,
                        color='tan', label="Range", zorder=2)
    else:
        ax.plot(thisyear.index.values,
                temperature(thisyear[ptype], 'C').value('F'),
                zorder=4, color='b',
                lw=2, label='%s Obs + CFS Forecast' % (today.year,))
        climo = cdf.groupby('doy')[ptype].mean()
        ax.plot(climo.index.values,
                temperature(climo.values, 'C').value('F'), lw=2, color='k',
                label='Climatology', zorder=3)
        xrng = df.groupby('doy')[ptype].max()
        nrng = df.groupby('doy')[ptype].min()
        ax.fill_between(xrng.index.values,
                        temperature(nrng.values, 'C').value('F'),
                        temperature(xrng.values, 'C').value('F'),
                        color='tan', label="Range", zorder=2)

    ax.set_title("%s %s" % (STATIONS[location], PLOTS[ptype]))
    ax.set_ylabel(PLOTS[ptype])
    ax.legend(loc=(0.03, -0.16), ncol=3, fontsize=12)
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335,
                   365))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.grid(True)
    ax.set_xlim(int(sdate.strftime("%j")),
                int(datetime.date(today.year, 12, 1).strftime("%j")))
    pos = ax.get_position()
    ax.set_position([pos.x0, pos.y0 + 0.05, pos.width, pos.height * 0.95])

    return fig, resdf


if __name__ == '__main__':
    plotter(dict())
