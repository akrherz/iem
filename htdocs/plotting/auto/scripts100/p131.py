"""Plot overcast conditions by temperature"""
import datetime
from collections import OrderedDict

from pandas.io.sql import read_sql
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.plot.use_agg import plt
from pyiem.exceptions import NoDataFound

PDICT = OrderedDict((
    ('CLR', 'Clear (CLR)'),
    ('OVC', 'Overcast (OVC)'),
))
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
    desc['description'] = """
    This plot displays the frequency of having overcast
    conditions reported by air temperature.  More specifically, this script
    looks for the report of 'OVC' within the METAR sky conditions.  Many
    caveats apply with the reporting changes of this over the years."""
    desc['arguments'] = [
        dict(type='zstation', name='zstation', default='DSM',
             network='IA_ASOS', label='Select Station:'),
        dict(type='select', name='month', default='all',
             label='Month Limiter', options=MDICT),
        dict(type='select', name='var', default='OVC', options=PDICT,
             label='Overcast or Clear Sky Conditions?'),
        dict(type='hour', name='hour', default=0, optional=True,
             label='Limit plot to local hour of day? (optional)'),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn('asos')
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['zstation']
    month = ctx['month']
    varname = ctx['var']
    hour = ctx.get('hour')

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

    if hour is None:
        df = read_sql("""
            SELECT tmpf::int as t,
            SUM(case when (skyc1 = %s or skyc2 = %s or skyc3 = %s
                or skyc4 = %s) then 1 else 0 end) as hits,
            count(*)
            from alldata where station = %s
            and tmpf is not null and extract(month from valid) in %s
            and report_type = 2
            GROUP by t ORDER by t ASC
            """, pgconn, params=(varname, varname, varname, varname,
                                 station, tuple(months)), index_col=None)
    else:
        df = read_sql("""
            SELECT tmpf::int as t,
            SUM(case when (skyc1 = %s or skyc2 = %s or skyc3 = %s
                or skyc4 = %s) then 1 else 0 end) as hits,
            count(*)
            from alldata where station = %s
            and tmpf is not null and extract(month from valid) in %s
            and extract(hour from ((valid +
                '10 minutes'::interval) at time zone %s)) = %s
            and report_type = 2
            GROUP by t ORDER by t ASC
            """, pgconn, params=(varname, varname, varname, varname,
                                 station, tuple(months),
                                 ctx['_nt'].sts[station]['tzname'], hour),
                      index_col=None)
    if df.empty:
        raise NoDataFound("No data was found.")
    df['freq'] = df['hits'] / df['count'] * 100.
    df2 = df[df['count'] > 2]
    avg = df['hits'].sum() / float(df['count'].sum()) * 100.

    (fig, ax) = plt.subplots(1, 1)
    ax.bar(df2['t'], df2['freq'], ec='green', fc='green', width=1)
    ax.grid(True, zorder=11)
    hrlabel = 'ALL'
    if hour is not None:
        ts = datetime.datetime(2000, 1, 1, hour)
        hrlabel = ts.strftime("%-I %p")
    ab = ctx['_nt'].sts[station]['archive_begin']
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    ax.set_title(
        ("%s [%s]\nFrequency of %s by "
         "Air Temp (month=%s,hour=%s) (%s-%s)\n"
         "(must have 3+ hourly observations at the given temperature)"
         ) % (ctx['_nt'].sts[station]['name'], station,
              "Overcast Clouds" if varname == 'OVC' else 'Clear Skies',
              month.upper(), hrlabel,
              ab.year,
              datetime.datetime.now().year), size=10)

    ax.set_ylabel("%s Frequency [%%]" % (PDICT[varname], ))
    ax.set_ylim(0, 100)
    ax.set_xlabel(r"Air Temperature $^\circ$F")
    if df2['t'].min() < 30:
        ax.axvline(32, lw=2, color='k')
        ax.text(32, -4, "32", ha='center')
    ax.axhline(avg, lw=2, color='k')
    ax.text(df2['t'].min() + 5, avg + 2, "Avg: %.1f%%" % (avg,))

    return fig, df


if __name__ == '__main__':
    plotter(dict())
