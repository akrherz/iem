import psycopg2
from pyiem.network import Table as NetworkTable
from pandas.io.sql import read_sql
import pandas as pd
import datetime
from pyiem.util import get_autoplot_context


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['report'] = True
    d['description'] = """This chart presents the accumulated frequency of
    having the first fall temperature at or below a given threshold."""
    d['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station'),
        dict(type='int', name='t1', default=32,
             label='First Threshold (F)'),
        dict(type='int', name='t2', default=28,
             label='Second Threshold (F)'),
        dict(type='int', name='t3', default=26,
             label='Third Threshold (F)'),
        dict(type='int', name='t4', default=22,
             label='Fourth Threshold (F)'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']
    thresholds = [ctx['t1'], ctx['t2'], ctx['t3'], ctx['t4']]

    table = "alldata_%s" % (station[:2], )
    nt = NetworkTable("%sCLIMATE" % (station[:2], ))
    # Load up dict of dates..

    df = pd.DataFrame({'dates': pd.date_range("2000/07/28", "2000/12/31"),
                       '%scnts' % (thresholds[0],): 0,
                       '%scnts' % (thresholds[1],): 0,
                       '%scnts' % (thresholds[2],): 0,
                       '%scnts' % (thresholds[3],): 0},
                      index=range(210, 367))
    df.index.name = 'doy'

    for base in thresholds:
        # Query Last doy for each year in archive
        df2 = read_sql("""
            select year,
            min(case when low <= %s then extract(doy from day)
                else 400 end) as doy from
            """ + table + """
            WHERE month > 7 and station = %s and year < %s
            GROUP by year
        """, pgconn,  params=(base, station, datetime.date.today().year),
                       index_col=None)
        for _, row in df2.iterrows():
            if row['doy'] == 400:
                continue
            df.loc[row['doy']:367, '%scnts' % (base,)] += 1
        df['%sfreq' % (base,)] = df['%scnts' % (base,)] / len(df2.index) * 100.

    res = """\
# IEM Climodat http://mesonet.agron.iastate.edu/climodat/
# Report Generated: %s
# Climate Record: %s -> %s
# Site Information: [%s] %s
# Contact Information: Daryl Herzmann akrherz@iastate.edu 515.294.5978
# Low Temperature exceedence probabilities
# (On a certain date, what is the chance a temperature below a certain
# threshold would have been observed once already during the fall of that year)
 DOY Date    <%s  <%s  <%s  <%s
""" % (datetime.date.today().strftime("%d %b %Y"),
       nt.sts[station]['archive_begin'].date(), datetime.date.today(), station,
       nt.sts[station]['name'], thresholds[0] + 1,
       thresholds[1] + 1, thresholds[2] + 1, thresholds[3] + 1)
    fcols = ['%sfreq' % (s,) for s in thresholds]
    mindate = None
    for doy, row in df.iterrows():
        if doy % 2 != 0:
            continue
        if row[fcols[0]] > 0 and mindate is None:
            mindate = row['dates'] - datetime.timedelta(days=5)
        res += (" %3s %s  %3i  %3i  %3i  %3i\n"
                ) % (row['dates'].strftime("%-j"),
                     row['dates'].strftime("%b %d"),
                     row[fcols[0]], row[fcols[1]], row[fcols[2]],
                     row[fcols[3]])

    (fig, ax) = plt.subplots(1, 1)
    for base in thresholds:
        ax.plot(df['dates'].values, df['%sfreq' % (base,)],
                label="%s" % (base,), lw=2)

    ax.legend(loc='best')
    ax.set_xlim(mindate)
    ax.xaxis.set_major_locator(mdates.DayLocator([1, 7, 14, 21]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%-d\n%b"))
    ax.set_title(("Frequency of First Fall Temperature\n"
                  "%s %s (%s-%s)"
                  ) % (station, nt.sts[station]['name'],
                       nt.sts[station]['archive_begin'].year,
                       datetime.date.today().year))
    ax.grid(True)
    df.reset_index(inplace=True)
    return fig, df, res

if __name__ == '__main__':
    plotter(dict())
