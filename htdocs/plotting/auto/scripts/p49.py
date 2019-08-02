"""Daily Frequency of Some Threshold."""
from collections import OrderedDict
import datetime

import matplotlib.dates as mdates
import pandas as pd
from pandas.io.sql import read_sql
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = OrderedDict([
    ('high', 'High Temp (F)'),
    ('low', 'Low Temp (F)'),
    ('precip', 'Precip (inch)'),
    ('snow', 'Snowfall (inch)'),
    ('snowd', 'Snow Depth (inch)'),
])
PDICT2 = OrderedDict([
    ('>=', 'Greater than or equal to'),
    ('<', 'Less than'),
])


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['cache'] = 86400
    desc['data'] = True
    desc['description'] = """This plot presents the observed frequency of
    some daily event happening.  Leap day (Feb 29th) is excluded from the
    analysis. If you download the data from this application, a placeholder
    date during the year 2001 is used."""
    desc['arguments'] = [
        dict(type='station', name='station', network='IACLIMATE',
             default='IATDSM', label='Select Climate Site:'),
        dict(type='select', name='var', default='snow',
             label='Select Variable:', options=PDICT),
        dict(type='select', name='opt', default='>=',
             label='Threshold Requirement:', options=PDICT2),
        dict(type='float', name='threshold', default='0.1',
             label='Threshold:'),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn('coop')
    ctx = get_autoplot_context(fdict, get_description())

    station = ctx['station']
    threshold = ctx['threshold']
    varname = ctx['var']
    opt = ctx['opt']
    table = "alldata_%s" % (station[:2], )

    df = read_sql("""
        SELECT sday, sum(case when """ + varname + """ """ + opt + """
            """ + str(threshold) + """ then 1 else 0 end) as hits,
        count(*) as total,
        min(day) as min_date,
        max(day) as max_date from """ + table + """
        WHERE station = %s and """ + varname + """ is not null
        and sday != '0229'
        GROUP by sday ORDER by sday
    """, pgconn, params=(station, ), index_col=None)
    if df.empty:
        raise NoDataFound("No Data Found.")
    # Covert sday into year 2001 date
    df['date'] = pd.to_datetime(df['sday'] + "2001", format='%m%d%Y')
    df.set_index('date', inplace=True)
    # calculate the frequency
    df['freq'] = df['hits'] / df['total'] * 100.

    (fig, ax) = plt.subplots(1, 1)
    ax.bar(df.index.values, df['freq'], ec='b', fc='b')
    ax.set_xlim(
        df.index.min() - datetime.timedelta(days=1),
        df.index.max() + datetime.timedelta(days=1))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax.grid(True)
    ax.set_ylabel("Frequency [%]")
    ax.set_title((
        "%s %s (%s-%s)\nFrequency of %s %s %s"
        ) % (station, ctx['_nt'].sts[station]['name'],
             df['min_date'].min().year,
             df['max_date'].max().year, PDICT[varname], PDICT2[opt],
             threshold))
    df.drop(['min_date', 'max_date'], axis=1, inplace=True)
    return fig, df


if __name__ == '__main__':
    plotter(dict())
