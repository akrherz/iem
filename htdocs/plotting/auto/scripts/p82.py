"""Calendar Plot of Automated Station Summaries"""
import datetime
from collections import OrderedDict

import psycopg2.extras
import pandas as pd
from pandas.io.sql import read_sql
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.datatypes import speed
from pyiem.reference import TRACE_VALUE
from pyiem.plot import calendar_plot
from pyiem.exceptions import NoDataFound


PDICT = OrderedDict([
        ('avg_smph', 'Average Wind Speed [mph]'),
        ('max_tmpf', 'High Temperature'),
        ('high_departure', 'High Temperature Departure'),
        ('min_tmpf', 'Low Temperature'),
        ('low_departure', 'Low Temperature Departure'),
        ('avg_tmpf', 'Average Temperature'),
        ('avg_departure', 'Average Temperature Departure'),
        ('max_dwpf', 'Highest Dew Point Temperature'),
        ('min_dwpf', 'Lowest Dew Point Temperature'),
        ('pday', 'Precipitation')])


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['description'] = """This chart presents a series of daily summary data
    as a calendar.  The daily totals should be valid for the local day of the
    weather station.
    """
    today = datetime.date.today()
    m90 = today - datetime.timedelta(days=90)
    desc['arguments'] = [
        dict(type='zstation', name='station', default='DSM',
             network='IA_ASOS', label='Select Station'),
        dict(type='select', name='var', default='pday',
             label='Which Daily Variable:', options=PDICT),
        dict(type='date', name='sdate',
             default=m90.strftime("%Y/%m/%d"),
             label='Start Date:', min="1929/01/01"),
        dict(type='date', name='edate',
             default=today.strftime("%Y/%m/%d"),
             label='End Date:', min="1929/01/01"),
    ]
    return desc


def safe(row, varname):
    """Safe conversion of value for printing as a string"""
    val = row[varname]
    if val is None:
        return 'M'
    if varname == 'pday':
        if val == TRACE_VALUE:
            return 'T'
        if val == 0:
            return '0'
        return "%.2f" % (val,)
    return '%.0f' % (val,)


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn('iem')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']
    varname = ctx['var']
    sdate = ctx['sdate']
    edate = ctx['edate']

    # Get Climatology
    cdf = read_sql("""
        SELECT to_char(valid, 'mmdd') as sday, high, low,
        (high + low) / 2. as avg,
        precip from ncdc_climate81 WHERE station = %s
    """, get_dbconn('coop'),
                   params=(
                       ctx['_nt'].sts[station]['ncdc81'],), index_col='sday')
    if cdf.empty:
        raise NoDataFound("No Data Found.")

    cursor.execute("""
    SELECT day, max_tmpf, min_tmpf, max_dwpf, min_dwpf,
    (max_tmpf + min_tmpf) / 2. as avg_tmpf,
    pday, coalesce(avg_sknt, 0) as avg_sknt from summary s JOIN stations t
    on (t.iemid = s.iemid) WHERE s.day >= %s and s.day <= %s and
    t.id = %s and t.network = %s ORDER by day ASC
    """, (sdate, edate, station, ctx['network']))
    rows = []
    data = {}
    for row in cursor:
        hd = row['max_tmpf'] - cdf.at[row[0].strftime("%m%d"), 'high']
        ld = row['min_tmpf'] - cdf.at[row[0].strftime("%m%d"), 'low']
        ad = row['avg_tmpf'] - cdf.at[row[0].strftime("%m%d"), 'avg']
        rows.append(dict(day=row['day'], max_tmpf=row['max_tmpf'],
                         avg_smph=speed(row['avg_sknt'], 'KT').value('MPH'),
                         min_dwpf=row['min_dwpf'], max_dwpf=row['max_dwpf'],
                         high_departure=hd, low_departure=ld,
                         avg_departure=ad,
                         min_tmpf=row['min_tmpf'], pday=row['pday']))
        data[row[0]] = {'val': safe(rows[-1], varname)}
        if varname == 'high_departure':
            data[row[0]]['color'] = 'b' if hd < 0 else 'r'
        elif varname == 'low_departure':
            data[row[0]]['color'] = 'b' if ld < 0 else 'r'
        elif varname == 'avg_departure':
            data[row[0]]['color'] = 'b' if ad < 0 else 'r'
    df = pd.DataFrame(rows)

    title = '[%s] %s Daily %s' % (
        station, ctx['_nt'].sts[station]['name'], PDICT.get(varname))
    subtitle = '%s thru %s' % (
        sdate.strftime("%-d %b %Y"), edate.strftime("%-d %b %Y"))

    fig = calendar_plot(
        sdate, edate, data, title=title, subtitle=subtitle)
    return fig, df


if __name__ == '__main__':
    plotter(dict())
