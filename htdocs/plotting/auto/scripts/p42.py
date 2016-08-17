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
import psycopg2.extras
import datetime
import pytz
import pandas as pd
from pyiem.network import Table as NetworkTable
from pyiem.util import get_autoplot_context
from collections import OrderedDict

PDICT = {'above': 'At or Above Threshold...',
         'below': 'Below Threshold...'}
PDICT2 = {'tmpf': 'Air Temperature',
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
    d = dict()
    d['cache'] = 86400
    d['data'] = True
    d['description'] = """ Based on hourly METAR reports of temperature
    or dew point, this
    plot displays the longest periods above or below a given temperature
    threshold.  There are plenty of caveats to this plot, including missing
    data periods that are ignored and data during the 1960s that only has
    reports every three hours.  This plot also limits the number of lines
    drawn to 10, so if you hit the limit, please change the thresholds.
    """
    d['arguments'] = [
        dict(type='zstation', name='zstation', default='DSM',
             label='Select Station:'),
        dict(type='select', name='m', default='all',
             label='Month Limiter', options=MDICT),
        dict(type='select', name='dir', default='above',
             label='Threshold Direction:', options=PDICT),
        dict(type='select', name='var', default='tmpf',
             label='Which variable', options=PDICT2),
        dict(type='int', name='threshold', default=50,
             label='Temperature (F) Threshold:'),
        dict(type='int', name='hours', default=36,
             label='Minimum Period to Plot (Hours):')
    ]
    return d


def plot(ax, interval, valid, tmpf, year, lines):
    """ Our plotting function """
    if len(valid) == 0:
        return lines
    if (valid[-1] - valid[0]) > interval:
        if len(lines) == 10:
            ax.text(0.5, 0.9, "ERROR: Limit of 10 lines reached",
                    transform=ax.transAxes)
            return lines
        if len(lines) > 10:
            return lines
        delta = ((valid[-1] - valid[0]).days * 86400. +
                 (valid[-1] - valid[0]).seconds)
        i = tmpf.index(min(tmpf))
        mylbl = "%s\n%.1fd" % (year, delta / 86400.)
        lines.append(ax.plot(valid, tmpf, lw=2,
                             label=mylbl.replace("\n", " "))[0])
        lines[-1].hours = round((valid[-1] - valid[0]).seconds / 3600., 2)
        lines[-1].days = (valid[-1] - valid[0]).days
        lines[-1].year = year
        lines[-1].mylbl = mylbl
        ax.text(valid[i], tmpf[i], mylbl,
                ha='center', va='center',
                bbox=dict(color=lines[-1].get_color()),
                color='white')
    return lines


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')
    cursor = ASOS.cursor(cursor_factory=psycopg2.extras.DictCursor)

    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['zstation']
    network = ctx['network']
    threshold = ctx['threshold']
    mydir = ctx['dir']
    hours = ctx['hours']
    varname = ctx['var']
    month = ctx['m'] if fdict.get('month') is None else fdict.get('month')
    nt = NetworkTable(network)

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
        sts = datetime.datetime(2000, int(month), 1)
        ets = sts + datetime.timedelta(days=35)
        ets = ets.replace(day=1)
        ts = datetime.datetime.strptime("2000-"+month+"-01", '%Y-%m-%d')
        # make sure it is length two for the trick below in SQL
        months = [ts.month, 999]

    cursor.execute("""
      SELECT valid, round(""" + varname + """::numeric,0)
      from alldata where station = %s
      and """ + varname + """ is not null and
      extract(month from valid) in %s
      ORDER by valid ASC
      """, (station, tuple(months)))

    (fig, ax) = plt.subplots(1, 1)
    interval = datetime.timedelta(hours=hours)

    valid = []
    tmpf = []
    year = 0
    lines = []
    for row in cursor:
        if year != row[0].year:
            year = row[0].year
            lines = plot(ax, interval, valid, tmpf, year, lines)
            valid = []
            tmpf = []
        if ((mydir == 'above' and row[1] >= threshold) or
                (mydir == 'below' and row[1] < threshold)):
            valid.append(row[0].replace(year=2000))
            tmpf.append(row[1])
        if ((mydir == 'above' and row[1] < threshold) or
                (mydir == 'below' and row[1] >= threshold)):
            valid.append(row[0].replace(year=2000))
            tmpf.append(row[1])
            lines = plot(ax, interval, valid, tmpf, year, lines)
            valid = []
            tmpf = []

    lines = plot(ax, interval, valid, tmpf, year, lines)
    rows = []
    x0 = []
    x1 = []
    for line in lines:
        xdata = line.get_xdata()
        x0.append(xdata[0])
        x1.append(xdata[-1])
        rows.append(dict(start=xdata[0].replace(year=line.year),
                         end=xdata[-1].replace(year=line.year),
                         hours=line.hours, days=line.days))
    df = pd.DataFrame(rows)

    if len(lines) > 0:
        sts = min(x0)
        ets = max(x1)
    ax.set_xlim(sts, ets)
    ax.xaxis.set_major_locator(
        mdates.DayLocator(interval=((ets - sts).days / 10),
                          tz=pytz.timezone(nt.sts[station]['tzname'])))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%-d\n%b'))
    ax.grid(True)
    ax.set_ylabel("%s $^\circ$F" % (PDICT2.get(varname),))
    ax.set_xlabel("Timezone %s" % (nt.sts[station]['tzname'],))
    ax.set_title(("%s-%s [%s] %s\n%s :: %.1f+ Day Streaks %s %s$^\circ$F"
                  ) % (nt.sts[station]['archive_begin'].year,
                       datetime.datetime.now().year, station,
                       nt.sts[station]['name'], MDICT.get(month),
                       hours / 24.0, mydir, threshold))
    # ax.axhline(32, linestyle='-.', linewidth=2, color='k')
    # ax.set_ylim(bottom=43)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.15,
                     box.width, box.height * 0.85])
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1),
              fancybox=True, shadow=True, ncol=5, fontsize=12,
              columnspacing=1)
    return fig, df

if __name__ == '__main__':
    plotter(dict(station='DSM', network='IA_ASOS', m='all', threshold=78))
