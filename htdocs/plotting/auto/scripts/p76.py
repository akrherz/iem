"""Seasonal averages of Humudity."""
import datetime
from collections import OrderedDict

import numpy as np
from scipy import stats
from pandas.io.sql import read_sql
import metpy.calc as mcalc
from metpy.units import units
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn, utc

MDICT = OrderedDict([
         ('all', 'No Month/Time Limit'),
         ('water_year', 'Water Year'),
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
    of the Jan/Feb portion of the season. If you plot the 'Water Year', the
    year shown is the September 30th of the period.

    <p>You can optionally restrict the local hours of the day to consider for
    the plot.  These hours are expressed as a range of hours using a 24 hour
    clock.  For example, '8-16' would indicate a period between 8 AM and 4 PM
    inclusive.  If you want to plot one hour, just set the start and end hour
    to the same value.</p>
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
        dict(type='text', name='hours', optional=True, default='0-23',
             label=("Inclusive Local Hours (24-hour clock) "
                    "to Limit Analysis (optional)")),
    ]
    return desc


def run_calcs(df, ctx):
    """Do our maths."""
    # Convert sea level pressure to station pressure
    df['pressure'] = mcalc.add_height_to_pressure(
        df['slp'].values * units('millibars'),
        ctx['_nt'].sts[ctx['station']]['elevation'] * units('m')
    ).to(units('millibar'))
    # Compute the mixing ratio
    df['mixingratio'] = mcalc.mixing_ratio_from_relative_humidity(
        df['relh'].values * units('percent'),
        df['tmpf'].values * units('degF'),
        df['pressure'].values * units('millibars')
    )
    # Compute the saturation mixing ratio
    df['saturation_mixingratio'] = mcalc.saturation_mixing_ratio(
        df['pressure'].values * units('millibars'),
        df['tmpf'].values * units('degF')
    )
    df['vapor_pressure'] = mcalc.vapor_pressure(
        df['pressure'].values * units('millibars'),
        df['mixingratio'].values * units('kg/kg')).to(units('kPa'))
    df['saturation_vapor_pressure'] = mcalc.vapor_pressure(
        df['pressure'].values * units('millibars'),
        df['saturation_mixingratio'].values * units('kg/kg')).to(units('kPa'))
    df['vpd'] = df['saturation_vapor_pressure'] - df['vapor_pressure']
    # remove any NaN rows
    df = df.dropna()
    group = df.groupby('year')
    df = group.aggregate(np.average)

    df['dwpf'] = mcalc.dewpoint(
        df['vapor_pressure'].values * units('kPa')
    ).to(units('degF')).m
    return df


def get_data(ctx, startyear):
    """Get data"""
    pgconn = get_dbconn('asos')
    today = datetime.datetime.now()
    lastyear = today.year
    deltadays = 0
    if ctx['season'] == 'all':
        months = range(1, 13)
    elif ctx['season'] == 'water_year':
        deltadays = 92
        months = range(1, 13)
    elif ctx['season'] == 'spring':
        months = [3, 4, 5]
        if today.month > 5:
            lastyear += 1
    elif ctx['season'] == 'spring2':
        months = [4, 5, 6]
        if today.month > 6:
            lastyear += 1
    elif ctx['season'] == 'fall':
        months = [9, 10, 11]
        if today.month > 11:
            lastyear += 1
    elif ctx['season'] == 'summer':
        months = [6, 7, 8]
        if today.month > 8:
            lastyear += 1
    elif ctx['season'] == 'winter':
        deltadays = 33
        months = [12, 1, 2]
        if today.month > 2:
            lastyear += 1
    else:
        ts = datetime.datetime.strptime("2000-" + ctx['season'] + "-01",
                                        '%Y-%b-%d')
        # make sure it is length two for the trick below in SQL
        months = [ts.month, 999]
        lastyear += 1
    hours = range(24)
    if ctx.get('hours'):
        try:
            tokens = [int(i.strip()) for i in ctx['hours'].split("-")]
            hours = range(tokens[0], tokens[1] + 1)
        except ValueError:
            raise Exception("malformed hour limiter, sorry.")
        ctx['hour_limiter'] = "[%s-%s]" % (utc(2017, 1, 1, tokens[0]
                                               ).strftime("%-I %p"),
                                           utc(2017, 1, 1, tokens[1]
                                               ).strftime("%-I %p"))

    df = read_sql("""
        WITH obs as (
            SELECT valid at time zone %s as valid, tmpf, dwpf, relh,
            coalesce(mslp, alti * 33.8639, 1013.25) as slp
            from alldata WHERE station = %s and dwpf > -90
            and dwpf < 100 and tmpf >= dwpf and
            extract(month from valid) in %s and
            extract(hour from valid at time zone %s) in %s
            and report_type = 2
        )
      SELECT valid,
      extract(year from valid + '%s days'::interval)::int as year,
      tmpf, dwpf, slp, relh from obs
    """, pgconn, params=(ctx['_nt'].sts[ctx['station']]['tzname'],
                         ctx['station'], tuple(months),
                         ctx['_nt'].sts[ctx['station']]['tzname'],
                         tuple(hours), deltadays),
                  index_col=None)

    df = df[(df['year'] >= startyear) & (df['year'] < lastyear)]
    return df


def make_plot(df, ctx):
    """Do the plotting"""
    season = ctx['season']
    varname = ctx['varname']
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
            'F' if varname == 'dwpf' else 'kPa', r_value ** 2),
            transform=ax.transAxes, va='top', bbox=dict(color='white'))
    ax.set_xlabel("Year")
    ax.set_xlim(df.index.min() - 1, df.index.max() + 1)
    ax.set_ylim((df[varname].min() - 5) if varname == 'dwpf' else 0,
                df[varname].max() + df[varname].max()/10.)
    ax.set_ylabel(("Average %s [%s]"
                   ) % (PDICT[varname], 'F' if varname == 'dwpf' else 'kPa'))
    ax.grid(True)
    ax.set_title(("[%s] %s %.0f-%.0f\nAverage %s [%s] %s"
                  ) % (ctx['station'], ctx['_nt'].sts[ctx['station']]['name'],
                       df.index.min(), df.index.max(), PDICT[varname],
                       MDICT[season], ctx.get('hour_limiter', '')))
    ax.legend(ncol=1, loc=1)
    return fig


def plotter(fdict):
    """ Go """
    ctx = get_autoplot_context(fdict, get_description())
    startyear = ctx['year']

    df = get_data(ctx, startyear)
    df = run_calcs(df, ctx)
    fig = make_plot(df, ctx)

    return fig, df


if __name__ == '__main__':
    _fig, _df = plotter(
        dict(varname='dwpf', season='winter', station='DSM',
             network='IA_ASOS'))
    print(_df)
