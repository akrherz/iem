"""
This has a bug though as it would not catch end period streaks :/

with data as (
  select valid, tmpf as val,
  lag(tmpf) OVER (ORDER by valid ASC) as lag_val
  from t2001 where station = 'DSM' and tmpf is not null
  ORDER by valid ASC),
agg as (
  SELECT valid,
  case
    when lag_val >= 70 and val < 70
    then 'down'
    when lag_val < 70 and val >= 70
    then 'up'
    else null end as mydir from data),
agg2 as (
  SELECT valid, lag(valid) OVER (ORDER by valid ASC) as lag_valid, mydir
  from agg WHERE mydir is not null),
agg3 as (
  SELECT rank() OVER (ORDER by valid ASC), * from agg2
  where (valid - lag_valid) > '48 hours'::interval
  and mydir = 'down' and
  extract(year from valid) = extract(year from lag_valid))

SELECT a.rank, d.valid, d.val from agg3 a, data d WHERE
  d.valid <= a.valid and d.valid >= a.lag_valid ORDER by d.valid;
"""
import datetime
from collections import OrderedDict

import psycopg2.extras
import pandas as pd
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = {'above': 'At or Above Threshold...',
         'below': 'Below Threshold...'}
PDICT2 = {'tmpf': 'Air Temperature',
          'feel': 'Feels Like Temperature',
          'dwpf': 'Dew Point Temperature'}
MDICT = OrderedDict([
         ('all', 'Entire Year'),
         ('spring', 'Spring (MAM)'),
         ('fall', 'Fall (SON)'),
         # no worky ('winter', 'Winter (DJF)'),
         ('summer', 'Summer (JJA)'),
         # no worky ('octmar', 'October thru March'),
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
    desc['cache'] = 86400
    desc['data'] = True
    desc['description'] = """ Based on hourly METAR reports of temperature
    or dew point, this
    plot displays the longest periods above or below a given temperature
    threshold.  There are plenty of caveats to this plot, including missing
    data periods that are ignored and data during the 1960s that only has
    reports every three hours.  This plot also limits the number of lines
    drawn to 10, so if you hit the limit, please change the thresholds.
    """
    year_range = "1928-%s" % (datetime.date.today().year, )
    desc['arguments'] = [
        dict(type='zstation', name='zstation', default='DSM',
             network='IA_ASOS', label='Select Station:'),
        dict(type='select', name='m', default='all',
             label='Month Limiter', options=MDICT),
        dict(type='text', name='yrange', default=year_range, optional=True,
             label='Inclusive Range of Years to Include (optional)'),
        dict(type='select', name='dir', default='above',
             label='Threshold Direction:', options=PDICT),
        dict(type='select', name='var', default='tmpf',
             label='Which variable', options=PDICT2),
        dict(type='int', name='threshold', default=50,
             label='Temperature (F) Threshold:'),
        dict(type='int', name='hours', default=36,
             label='Minimum Period to Plot (Hours):')
    ]
    return desc


def plot(ax, interval, valid, tmpf, lines, mydir, month):
    """ Our plotting function """
    if len(lines) > 10 or len(valid) < 2 or (valid[-1] - valid[0]) < interval:
        return lines
    if len(lines) == 10:
        ax.text(0.5, 0.9, "ERROR: Limit of 10 lines reached",
                transform=ax.transAxes)
        return lines
    delta = (valid[-1] - valid[0]).total_seconds()
    i = tmpf.index(min(tmpf))
    mylbl = "%s\n%id%.0fh" % (valid[0].year, delta / 86400,
                              (delta % 86400) / 3600.)
    x0 = valid[0].replace(month=1, day=1, hour=0, minute=0)
    offset = 0
    if mydir == 'below' and valid[0].month < 7 and month == 'all':
        offset = 366. * 86400.
    seconds = [((v - x0).total_seconds() + offset) for v in valid]
    lines.append(ax.plot(seconds, tmpf, lw=2,
                         label=mylbl.replace("\n", " "))[0])
    lines[-1].hours = round((valid[-1] - valid[0]).seconds / 3600., 2)
    lines[-1].days = (valid[-1] - valid[0]).days
    lines[-1].mylbl = mylbl
    lines[-1].period_start = valid[0]
    lines[-1].period_end = valid[-1]
    ax.text(seconds[i], tmpf[i], mylbl,
            ha='center', va='center',
            bbox=dict(color=lines[-1].get_color()),
            color='white')
    return lines


def compute_xlabels(ax):
    """Figure out how to make pretty xaxis labels"""
    # values are in seconds
    xlim = ax.get_xlim()
    x0 = datetime.datetime(2000, 1, 1) + datetime.timedelta(seconds=xlim[0])
    x0 = x0.replace(hour=0, minute=0)
    x1 = datetime.datetime(2000, 1, 1) + datetime.timedelta(seconds=xlim[1])
    x1 = x1.replace(hour=0, minute=0) + datetime.timedelta(days=1)
    xticks = []
    xticklabels = []
    # Pick a number of days so that we end up with 8 labels
    delta = int((xlim[1] - xlim[0]) / 86400. / 7)
    if delta == 0:
        delta = 1
    for x in range(int((x0 - datetime.datetime(2000, 1, 1)).total_seconds()),
                   int((x1 - datetime.datetime(2000, 1, 1)).total_seconds()),
                   86400 * delta):
        xticks.append(x)
        ts = datetime.datetime(2000, 1, 1) + datetime.timedelta(seconds=x)
        xticklabels.append(ts.strftime("%-d\n%b"))
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn('asos', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['zstation']
    threshold = ctx['threshold']
    mydir = ctx['dir']
    hours = ctx['hours']
    varname = ctx['var']
    month = ctx['m'] if fdict.get('month') is None else fdict.get('month')

    year_limiter = ""
    y1, y2 = None, None
    if 'yrange' in ctx:
        y1, y2 = ctx['yrange'].split("-")
        year_limiter = (
            " and valid >= '%s-01-01' and valid < '%s-01-01' "
        ) % (int(y1), int(y2))
    if month == 'all':
        months = range(1, 13)
        sts = datetime.datetime(2000, 1, 1)
        ets = datetime.datetime(2000, 12, 31)
    elif month == 'fall':
        months = [9, 10, 11]
        sts = datetime.datetime(2000, 9, 1)
        ets = datetime.datetime(2000, 11, 30)
    elif month == 'spring':
        months = [3, 4, 5]
        sts = datetime.datetime(2000, 3, 1)
        ets = datetime.datetime(2000, 5, 31)
    elif month == 'summer':
        months = [6, 7, 8]
        sts = datetime.datetime(2000, 6, 1)
        ets = datetime.datetime(2000, 8, 31)
    else:
        ts = datetime.datetime.strptime("2000-"+month+"-01", '%Y-%b-%d')
        # make sure it is length two for the trick below in SQL
        months = [ts.month, 999]
        sts = datetime.datetime(2000, ts.month, 1)
        ets = sts + datetime.timedelta(days=35)
        ets = ets.replace(day=1)

    cursor.execute("""
        SELECT valid, round(""" + varname + """::numeric,0)
        from alldata where station = %s """ + year_limiter + """
        and """ + varname + """ is not null and
        extract(month from valid) in %s
        ORDER by valid ASC
    """, (station, tuple(months)))

    (fig, ax) = plt.subplots(1, 1, figsize=(9, 6))
    interval = datetime.timedelta(hours=hours)

    valid = []
    tmpf = []
    year = 0
    lines = []
    for row in cursor:
        if month != 'all' and year != row[0].year:
            year = row[0].year
            lines = plot(ax, interval, valid, tmpf, lines, mydir, month)
            valid = []
            tmpf = []
        if ((mydir == 'above' and row[1] >= threshold) or
                (mydir == 'below' and row[1] < threshold)):
            valid.append(row[0])
            tmpf.append(row[1])
        if ((mydir == 'above' and row[1] < threshold) or
                (mydir == 'below' and row[1] >= threshold)):
            valid.append(row[0])
            tmpf.append(row[1])
            lines = plot(ax, interval, valid, tmpf, lines, mydir, month)
            valid = []
            tmpf = []

    lines = plot(ax, interval, valid, tmpf, lines, mydir, month)
    compute_xlabels(ax)
    rows = []
    for line in lines:
        # Ensure we don't send datetimes to pandas
        rows.append(dict(start=line.period_start.strftime("%Y-%m-%d %H:%M"),
                         end=line.period_end.strftime("%Y-%m-%d %H:%M"),
                         hours=line.hours, days=line.days))
    df = pd.DataFrame(rows)

    ax.grid(True)
    ax.set_ylabel(r"%s $^\circ$F" % (PDICT2.get(varname),))
    ab = ctx['_nt'].sts[station]['archive_begin']
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    ax.set_title(
        ("%s-%s [%s] %s\n"
         r"%s :: %.0fd%.0fh+ Streaks %s %s$^\circ$F"
         ) % (y1 if y1 is not None else ab.year,
              y2 if y2 is not None else datetime.datetime.now().year, station,
              ctx['_nt'].sts[station]['name'], MDICT.get(month),
              hours / 24, hours % 24, mydir, threshold))
    # ax.axhline(32, linestyle='-.', linewidth=2, color='k')
    # ax.set_ylim(bottom=43)
    ax.set_xlabel(("* Due to timezones and leapday, there is some ambiguity"
                   " with the plotted dates"))
    ax.set_position([0.1, 0.25, 0.85, 0.65])
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.165),
              fancybox=True, shadow=True, ncol=5, fontsize=12,
              columnspacing=1)
    return fig, df


if __name__ == '__main__':
    plotter(dict())
