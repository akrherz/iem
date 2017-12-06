"""Seasonal averages of Humudity"""
import datetime
from collections import OrderedDict

import numpy as np
from scipy import stats
from pandas.io.sql import read_sql
import metpy.calc as mcalc
from metpy.units import units
from pyiem import meteorology
from pyiem.network import Table as NetworkTable
from pyiem.datatypes import temperature, mixingratio, pressure
from pyiem.util import get_autoplot_context, get_dbconn

MDICT = OrderedDict([
         ('all', 'No Month/Time Limit'),
         ('spring', 'Spring (MAM)'),
         ('spring2', 'Spring (AMJ)'),
         ('fall', 'Fall (SON)'),
         ('winter', 'Winter (DJF)'),
         ('summer', 'Summer (JJA)'),
         ('jan', 'January'),
         ('feb', 'February'),
         ('mar', 'March'),
         ('apr', 'April'),
         ('may', 'May'),
         ('jun', 'June'),
         ('jul', 'July'),
         ('aug', 'August'),
         ('sep', 'September'),
         ('oct', 'October'),
         ('nov', 'November'),
         ('dec', 'December')])
PDICT = {'dwpf': 'Dew Point Temperature',
         'vpd': 'Vapor Pressure Deficit'}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['description'] = """Simple plot of yearly average dew points by year,
    season, or month.
    This calculation was done by computing the mixing ratio, then averaging
    the mixing ratios by year, and then converting that average to a dew point.
    This was done due to the non-linear nature of dew point when expressed in
    units of temperature.  If you plot the 'winter' season, the year shown is
    of the Jan/Feb portion of the season.
    """
    desc['arguments'] = [
        dict(type='zstation', name='station', default='DSM',
             label='Select Station', network='IA_ASOS'),
        dict(type='select', name='season', default='winter',
             label='Select Time Period:', options=MDICT),
        dict(type='select', name='varname', default='dwpf',
             label='Metric to Plot:', options=PDICT),
        dict(type="year", name="year", default=1893,
             label="Start Year of Plot"),
    ]
    return desc


def run_calcs(df):
    """Do our maths"""
    df['mixingratio'] = meteorology.mixing_ratio(
        temperature(df['dwpf'].values, 'F')).value('KG/KG')
    df['vapor_pressure'] = mcalc.vapor_pressure(
        1000. * units.mbar,
        df['mixingratio'].values * units('kg/kg')).to(units.mbar)
    df['saturation_mixingratio'] = (
        meteorology.mixing_ratio(
            temperature(df['tmpf'].values, 'F')).value('KG/KG'))
    df['saturation_vapor_pressure'] = mcalc.vapor_pressure(
        1000. * units.mbar,
        df['saturation_mixingratio'].values * units('kg/kg')).to(units.mbar)
    df['vpd'] = df['saturation_vapor_pressure'] - df['vapor_pressure']
    group = df.groupby('year')
    df = group.aggregate(np.average)

    df['dwpf'] = meteorology.dewpoint_from_pq(
        pressure(1000, 'MB'),
        mixingratio(df['mixingratio'].values, 'KG/KG')).value('F')
    return df


def get_data(season, station, startyear):
    """Get data"""
    pgconn = get_dbconn('asos')
    today = datetime.datetime.now()
    lastyear = today.year
    deltadays = 0
    if season == 'all':
        months = range(1, 13)
    elif season == 'spring':
        months = [3, 4, 5]
        if today.month > 5:
            lastyear += 1
    elif season == 'spring2':
        months = [4, 5, 6]
        if today.month > 6:
            lastyear += 1
    elif season == 'fall':
        months = [9, 10, 11]
        if today.month > 11:
            lastyear += 1
    elif season == 'summer':
        months = [6, 7, 8]
        if today.month > 8:
            lastyear += 1
    elif season == 'winter':
        deltadays = 33
        months = [12, 1, 2]
        if today.month > 2:
            lastyear += 1
    else:
        ts = datetime.datetime.strptime("2000-"+season+"-01", '%Y-%b-%d')
        # make sure it is length two for the trick below in SQL
        months = [ts.month, 999]
        lastyear += 1

    df = read_sql("""
      SELECT valid,
      extract(year from valid + '%s days'::interval)::int as year,
      tmpf, dwpf from alldata
      where station = %s and dwpf > -90 and
      dwpf < 100 and extract(month from valid) in %s
      and tmpf > -90 and tmpf < 150 and tmpf >= dwpf
    """, pgconn, params=(deltadays, station,  tuple(months)), index_col=None)

    df = df[(df['year'] >= startyear) & (df['year'] < lastyear)]
    return df


def make_plot(df, ctx):
    """Do the plotting"""
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    season = ctx['season']
    varname = ctx['varname']
    network = ctx['network']
    nt = NetworkTable(network)
    (fig, ax) = plt.subplots(1, 1, figsize=(8, 6))
    avgv = df[varname].mean()

    colorabove = 'seagreen' if varname == 'dwpf' else 'lightsalmon'
    colorbelow = 'lightsalmon' if varname == 'dwpf' else 'seagreen'
    cols = ax.bar(df.index.values, df[varname].values,
                  fc=colorabove, ec=colorabove, align='center')
    for i, col in enumerate(cols):
        if df.iloc[i][varname] < avgv:
            col.set_facecolor(colorbelow)
            col.set_edgecolor(colorbelow)
    ax.axhline(avgv, lw=2, color='k', zorder=2, label='Average')
    h_slope, intercept, r_value, _, _ = stats.linregress(df.index.values,
                                                         df[varname].values)
    ax.plot(df.index.values, h_slope * df.index.values + intercept, '--',
            lw=2, color='k', label='Trend')
    ax.text(0.01, 0.98, "Avg: %.1f, slope: %.2f %s/century, R$^2$=%.2f" % (
            avgv, h_slope * 100.,
            'F' if varname == 'dwpf' else 'hPa', r_value ** 2),
            transform=ax.transAxes, va='top', bbox=dict(color='white'))
    ax.set_xlabel("Year")
    ax.set_xlim(df.index.min() - 1, df.index.max() + 1)
    ax.set_ylim((df[varname].min() - 5) if varname == 'dwpf' else 0,
                df[varname].max() + df[varname].max()/10.)
    ax.set_ylabel(("Average %s [%s]"
                   ) % (PDICT[varname], 'F' if varname == 'dwpf' else 'hPa'))
    ax.grid(True)
    ax.set_title(("[%s] %s %.0f-%.0f\nAverage %s [%s] "
                  ) % (ctx['station'], nt.sts[ctx['station']]['name'],
                       df.index.min(), df.index.max(),  PDICT[varname],
                       MDICT[season]))
    ax.legend(ncol=1, loc=1)
    return fig


def plotter(fdict):
    """ Go """
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']
    season = ctx['season']
    _ = MDICT[season]
    startyear = ctx['year']

    df = get_data(season, station, startyear)
    df = run_calcs(df)
    fig = make_plot(df, ctx)

    return fig, df


if __name__ == '__main__':
    plotter(dict(varname='vpd', season='winter'))
