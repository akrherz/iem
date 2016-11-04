import psycopg2
from pandas.io.sql import read_sql
import numpy as np
import datetime
from pyiem.network import Table as NetworkTable
from collections import OrderedDict
from pyiem.util import get_autoplot_context

PDICT = OrderedDict([
    ('last', 'Last Date At or Above'),
    ('first', 'First Date At or Above'),
    ('first_low', 'First Date Below (Low Temperature)'),
    ('last_low', 'Last Date Below (Low Temperature)')
    ])


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This plot presents the yearly first or last date
    of a given high or low temperature along with the number of days that
    year above/below the threshold along with the cumulative distribution
    function for the first date!  When you select a low temperature option,
    the season displayed in the chart and available download spreadsheet
    represents the start year of the winter season.  Rewording, the year 2016
    would represent the period of 1 July 2016 to 30 Jun 2017.
    """
    d['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station:'),
        dict(type='int', name='threshold', default='90',
             label='Enter Threshold:'),
        dict(type='select', name='which', default='last',
             label='Date Option:', options=PDICT),
        dict(type='year', name='year', default=datetime.date.today().year,
             label='Year to Highlight in Chart:'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']
    network = "%sCLIMATE" % (station[:2],)
    nt = NetworkTable(network)
    threshold = ctx['threshold']
    which = ctx['which']
    year = ctx['year']

    table = "alldata_%s" % (station[:2],)

    opp = ' low < ' if which.find("_low") > 0 else ' high >= '
    df = read_sql("""
        with data as (
            SELECT extract(year from day + '%s months'::interval) as season,
            high, low, day from """+table+""" WHERE station = %s
            and day >= '1893-01-01'),
        agg1 as (
            SELECT season - %s as season,
            count(*) as obs,
            min(case when """+opp+""" %s then day else null end) as nday,
            max(case when """+opp+""" %s then day else null end) as xday,
            sum(case when """+opp+""" %s then 1 else 0 end) as count
            from data GROUP by season)
    SELECT season::int, count, obs, nday, extract(doy from nday) as nday_doy,
    xday, extract(doy from xday) as xday_doy from agg1
    ORDER by season ASC
    """, pgconn, params=(6 if which.find('_low') > 0 else 0,
                         station,
                         1 if which.find('_low') > 0 else 0,
                         threshold, threshold, threshold),
                  index_col='season')
    # We need to do some magic to julian dates straight
    if which.find('_low') > 0:
        # drop the first row
        df.drop(df.index.values[0], inplace=True)
        df.loc[df['nday_doy'] < 183, 'nday_doy'] += 365.
        df.loc[df['xday_doy'] < 183, 'xday_doy'] += 365.
    # Set NaN where we did not meet conditions
    zeros = df[df['count'] == 0].index.values
    col = 'xday_doy' if which.find('last') == 0 else 'nday_doy'
    df2 = df[df['count'] > 0]

    (fig, ax) = plt.subplots(1, 1)
    ax.scatter(df2[col], df2['count'])
    ax.grid(True)
    ax.set_ylabel("Days %s Temp of %s$^\circ$F" % (
        ('Below Low' if which.find('_low') > 0 else
         'At or Above High'), threshold))
    ax.set_title(("%s [%s] Days per Year %s %s $^\circ$F\nversus "
                  "%s Date of that Temperature") % (
                nt.sts[station]['name'], station,
                ('below' if which.find('_low') > 0 else 'at or above'),
                threshold, "Latest" if which == 'last' else 'First'))

    xticks = []
    xticklabels = []
    for i in np.arange(df2[col].min() - 5, df2[col].max() + 5, 1):
        ts = datetime.datetime(2000, 1, 1) + datetime.timedelta(days=i)
        if ts.day == 1:
            xticks.append(i)
            xticklabels.append(ts.strftime("%-d %b"))
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)
    ax.set_xlabel(("Date of Last Occurrence" if which == 'last'
                   else 'Date of First Occurence'))

    ax2 = ax.twinx()
    sortvals = np.sort(df2[col].values)
    yvals = np.arange(len(sortvals)) / float(len(sortvals))
    ax2.plot(sortvals, yvals * 100., color='r')
    ax2.set_ylabel("Accumulated Frequency [%] (red line)")
    ax2.set_yticks([0, 25, 50, 75, 100])

    avgd = datetime.datetime(2000, 1, 1) + datetime.timedelta(
                                            days=int(df2[col].mean()))
    ax.text(0.01, 0.99, ("%s year(s) failed threshold %s\nAvg Date: %s\n"
                         "Avg Count: %.1f days"
                         ) % (len(zeros),
                              ("[" +
                               ",".join([str(z) for z in zeros]) + "]"
                               ) if len(zeros) < 4 else "",
                              avgd.strftime("%-d %b"),
                              df2['count'].mean()),
            transform=ax.transAxes, va='top', bbox=dict(color='white'))

    ax.set_xlim(df2[col].min() - 10, df2[col].max() + 10)
    ax.set_ylim(0, df2['count'].max() * 1.2)

    idx = df2[col].idxmax()
    ax.text(df2.at[idx, col] + 1, df2.at[idx, 'count'],
            "%s" % (idx,), ha='left')
    idx = df2[col].idxmin()
    ax.text(df2.at[idx, col] - 1, df2.at[idx, 'count'],
            "%s" % (idx,), va='bottom')
    idx = df2['count'].idxmax()
    ax.text(df2.at[idx, col] + 1, df2.at[idx, 'count'],
            "%s" % (idx,), va='bottom')
    if year in df2.index:
        df3 = df2.loc[year]
        ax.scatter(df3[col], df3['count'], zorder=5, color='r')
        ax.text(df3[col], df3['count'], "%s" % (year,), zorder=5, color='r')
    return fig, df


if __name__ == '__main__':
    plotter(dict(which='first_low', threshold=32, year=2016))
