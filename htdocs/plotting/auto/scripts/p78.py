"""Avg dew point at temperature."""
from collections import OrderedDict
import datetime

from pandas.io.sql import read_sql
from metpy.units import units
import metpy.calc as mcalc
from pyiem.network import Table as NetworkTable
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.plot.use_agg import plt

MDICT = OrderedDict([
         ('all', 'No Month/Time Limit'),
         ('spring', 'Spring (MAM)'),
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


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['cache'] = 86400
    desc['description'] = """This plot displays the average dew point at
    a given air temperature.  The average dew point is computed by taking the
    observations of mixing ratio, averaging those, and then back computing
    the dew point temperature.  With that averaged dew point temperature a
    relative humidity value is computed."""
    desc['arguments'] = [
        dict(type='zstation', name='zstation', default='DSM',
             label='Select Station:', network='IA_ASOS'),
        dict(type='select', name='month', default='all',
             label='Month Limiter', options=MDICT),

    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn('asos')
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['zstation']
    network = ctx['network']
    month = ctx['month']

    nt = NetworkTable(network)

    if month == 'all':
        months = range(1, 13)
    elif month == 'fall':
        months = [9, 10, 11]
    elif month == 'winter':
        months = [12, 1, 2]
    elif month == 'spring':
        months = [3, 4, 5]
    elif month == 'summer':
        months = [6, 7, 8]
    else:
        ts = datetime.datetime.strptime("2000-"+month+"-01", '%Y-%b-%d')
        # make sure it is length two for the trick below in SQL
        months = [ts.month, 999]

    df = read_sql("""
        SELECT tmpf::int as tmpf, dwpf, relh,
        coalesce(mslp, alti * 33.8639, 1013.25) as slp
        from alldata where station = %s
        and drct is not null and dwpf is not null and dwpf <= tmpf
        and sknt > 3 and drct::int %% 10 = 0
        and extract(month from valid) in %s
        and report_type = 2
    """, pgconn, params=(station, tuple(months)))
    # Convert sea level pressure to station pressure
    df['pressure'] = mcalc.add_height_to_pressure(
        df['slp'].values * units('millibars'),
        nt.sts[station]['elevation'] * units('m')
    ).to(units('millibar'))
    # compute mixing ratio
    df['mixingratio'] = mcalc.mixing_ratio_from_relative_humidity(
        df['relh'].values * units('percent'),
        df['tmpf'].values * units('degF'),
        df['pressure'].values * units('millibars')
    )
    # compute pressure
    df['vapor_pressure'] = mcalc.vapor_pressure(
        df['pressure'].values * units('millibars'),
        df['mixingratio'].values * units('kg/kg')
    ).to(units('kPa'))

    means = df.groupby('tmpf').mean().copy()
    # compute dewpoint now
    means['dwpf'] = mcalc.dewpoint(
        means['vapor_pressure'].values * units('kPa')
    ).to(units('degF')).m
    means.reset_index(inplace=True)
    # compute RH again
    means['relh'] = mcalc.relative_humidity_from_dewpoint(
        means['tmpf'].values * units('degF'),
        means['dwpf'].values * units('degF')
    ) * 100.

    (fig, ax) = plt.subplots(1, 1, figsize=(8, 6))
    ax.bar(
        means['tmpf'].values - 0.5, means['dwpf'].values - 0.5,
        ec='green', fc='green', width=1
    )
    ax.grid(True, zorder=11)
    ax.set_title(("%s [%s]\nAverage Dew Point by Air Temperature (month=%s) "
                  "(%s-%s)\n"
                  "(must have 3+ hourly observations at the given temperature)"
                  ) % (nt.sts[station]['name'], station, month.upper(),
                       nt.sts[station]['archive_begin'].year,
                       datetime.datetime.now().year), size=10)

    ax.plot([0, 140], [0, 140], color='b')
    ax.set_ylabel("Dew Point [F]")
    y2 = ax.twinx()
    y2.plot(means['tmpf'].values, means['relh'].values, color='k')
    y2.set_ylabel("Relative Humidity [%] (black line)")
    y2.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    y2.set_ylim(0, 100)
    ax.set_ylim(0, means['tmpf'].max() + 2)
    ax.set_xlim(0, means['tmpf'].max() + 2)
    ax.set_xlabel(r"Air Temperature $^\circ$F")

    return fig, means[['tmpf', 'dwpf', 'relh']]


if __name__ == '__main__':
    plotter(dict())
