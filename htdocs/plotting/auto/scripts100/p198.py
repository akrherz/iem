"""Monthly Sounding Averages"""
import datetime
from collections import OrderedDict

from pandas.io.sql import read_sql
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = {'00': '00 UTC', '12': '12 UTC'}
MDICT = OrderedDict([
         ('all', 'No Month/Time Limit'),
         ('spring', 'Spring (MAM)'),
         ('mjj', 'May/June/July'),
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
PDICT3 = OrderedDict([
    ('tmpc', 'Air Temperature (C)'),
    ('dwpc', 'Dew Point (C)'),
    ('height', 'Height (m)'),
    ('smps', 'Wind Speed (mps)'),
    ('sbcape_jkg', 'Surface Based CAPE (J/kg)'),
    ('sbcin_jkg', 'Surface Based CIN (J/kg)'),
    ('mucape_jkg', 'Most Unstable CAPE (J/kg)'),
    ('mucin_jkg', 'Most Unstable CIN (J/kg)'),
    ('pwater_mm', 'Precipitable Water (mm)'),
    ])
PDICT4 = OrderedDict((
    ('min', 'Minimum'),
    ('avg', 'Average'),
    ('max', 'Maximum'),
))


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['cache'] = 86400
    desc['description'] = """This plot presents a simple average of a given
    sounding variable of your choice.  If the selected month period crosses
    a calendar year, the year shown is for the January included in the period.

    <br /><br />The 'Select Station' option provides some 'virtual' stations
    that are spliced together archives of close by stations.  For some
    locations, the place that the sounding is made has moved over the years..
    """
    desc['arguments'] = [
        dict(type='networkselect', name='station', network='RAOB',
             default='_OAX', label='Select Station:'),
        dict(type='select', name='hour', default='00', options=PDICT,
             label='Which Routine Sounding:'),
        dict(type='select', name='month', default='all',
             label='Month Limiter', options=MDICT),
        dict(type='select', name='agg', default='avg', options=PDICT4,
             label='Which Statistical Aggregate to Plot:'),
        dict(type='select', name='var', default='tmpc', options=PDICT3,
             label='Which Sounding Variable to Plot:'),
        dict(type='int', name='level', default=500,
             label='Which Pressure (hPa) level:'),
    ]
    return desc


def plotter(fdict):
    """ Go """
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']
    if station not in ctx['_nt'].sts:  # This is needed.
        raise NoDataFound("Unknown station metadata.")
    varname = ctx['var']
    hour = int(ctx['hour'])
    month = ctx['month']
    level = ctx['level']
    agg = ctx['agg']
    offset = 0
    if month == 'all':
        months = range(1, 13)
    elif month == 'fall':
        months = [9, 10, 11]
    elif month == 'winter':
        months = [12, 1, 2]
        offset = 32
    elif month == 'spring':
        months = [3, 4, 5]
    elif month == 'mjj':
        months = [5, 6, 7]
    elif month == 'summer':
        months = [6, 7, 8]
    else:
        ts = datetime.datetime.strptime("2000-"+month+"-01", '%Y-%b-%d')
        # make sure it is length two for the trick below in SQL
        months = [ts.month]

    name = ctx['_nt'].sts[station]['name']
    stations = [station, ]
    if station.startswith("_"):
        name = ctx['_nt'].sts[station]['name'].split("--")[0]
        stations = ctx['_nt'].sts[station]['name'].split(
            "--")[1].strip().split(" ")
    pgconn = get_dbconn('postgis')

    if varname in ['tmpc', 'dwpc', 'height', 'smps']:
        leveltitle = " @ %s hPa" % (level, )
        dfin = read_sql("""
            select extract(year from f.valid + '%s days'::interval) as year,
            avg(p.""" + varname + """) as avg_""" + varname + """,
            min(p.""" + varname + """) as min_""" + varname + """,
            max(p.""" + varname + """) as max_""" + varname + """,
            count(*)
            from raob_profile p JOIN raob_flights f on (p.fid = f.fid)
            WHERE f.station in %s and p.pressure = %s and
            extract(hour from f.valid at time zone 'UTC') = %s and
            extract(month from f.valid) in %s
            GROUP by year ORDER by year ASC
        """, pgconn, params=(
            offset, tuple(stations), level, hour, tuple(months)),
                        index_col='year')
    else:
        leveltitle = ""
        dfin = read_sql("""
            select extract(year from f.valid + '%s days'::interval) as year,
            count(*),
            avg(p.""" + varname + """) as avg_""" + varname + """,
            min(p.""" + varname + """) as min_""" + varname + """,
            max(p.""" + varname + """) as max_""" + varname + """
            from raob_flights f
            WHERE f.station in %s and
            extract(hour from f.valid at time zone 'UTC') = %s and
            extract(month from f.valid) in %s
            GROUP by year ORDER by year ASC
        """, pgconn, params=(
            offset, tuple(stations), hour, tuple(months)),
                        index_col='year')
    # need quorums
    df = dfin[dfin['count'] > ((len(months) * 28) * 0.75)]
    if df.empty:
        raise NoDataFound("No data was found!")
    colname = "%s_%s" % (agg, varname)
    fig, ax = plt.subplots(1, 1)
    avgv = df[colname].mean()
    bars = ax.bar(df.index.values, df[colname], align='center')
    for i, _bar in enumerate(bars):
        val = df.iloc[i][colname]
        if val < avgv:
            _bar.set_color('blue')
        else:
            _bar.set_color('red')
    ax.set_xlim(df.index.min() - 1, df.index.max() + 1)
    rng = df[colname].max() - df[colname].min()
    ax.set_ylim(df[colname].min() - rng * 0.1,
                df[colname].max() + rng * 0.1)
    ax.axhline(avgv, color='k')
    ax.text(df.index.values[-1] + 2, avgv, "Avg:\n%.1f" % (avgv, ))
    ax.set_xlabel("Year")
    ax.set_ylabel("%s %s @ %s hPa" % (PDICT4[agg], PDICT3[varname], level))
    plt.gcf().text(0.5, 0.9,
                   ("%s %s %02i UTC Sounding\n"
                    "%s %s%s over %s"
                    ) % (station, name, hour, PDICT4[agg], PDICT3[varname],
                         leveltitle, MDICT[month]),
                   ha='center', va='bottom')
    ax.grid(True)

    return fig, df


if __name__ == '__main__':
    plotter(dict())
