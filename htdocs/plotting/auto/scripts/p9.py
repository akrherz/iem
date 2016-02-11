import psycopg2
import numpy as np
from pyiem import network
import calendar
import datetime
from pandas.io.sql import read_sql


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This chart produces the daily climatology of
    Growing Degree Days for a location of your choice. Please note that
    Feb 29 is not considered for this analysis."""
    d['arguments'] = [
        dict(type='station', name='station', default='IA0200',
             label='Select Station:'),
        dict(type='year', name='year', default='2015', min=1893,
             label='Select Year:'),
        dict(type='text', name='base', default='50',
             label='Enter GDD Base (F):'),
        dict(type='text', name='ceiling', default='86',
             label='Enter GDD Ceiling (F):'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')

    station = fdict.get('station', 'IA0200')
    thisyear = datetime.datetime.now().year
    year = int(fdict.get('year', thisyear))
    base = int(fdict.get('base', 50))
    ceiling = int(fdict.get('ceiling', 86))

    table = "alldata_%s" % (station[:2],)
    nt = network.Table("%sCLIMATE" % (station[:2],))
    syear = max(nt.sts[station]['archive_begin'].year, 1893)

    glabel = "gdd%s%s" % (base, ceiling)
    df = read_sql("""
    SELECT year, sday,
    gddxx("""+str(base)+""", """+str(ceiling)+""", high, low) as """+glabel+"""
    from """+table+""" WHERE station = %s and year > 1892 and sday != '0229'
    """, pgconn, params=(station, ))

    # Do some magic!
    df2 = df[['sday', glabel]].groupby('sday').describe(
                percentiles=[.05, .25, .75, .95])
    df2 = df2.unstack(level=-1)
    (fig, ax) = plt.subplots(1, 1)
    ax.plot(np.arange(1, 366), df2[(glabel, 'mean')], color='r', zorder=2,
            lw=2., label='Average')
    _data = df[df['year'] == year][[glabel, 'sday']]
    _data.sort_values(by='sday', inplace=True)
    ax.scatter(np.arange(1, _data[glabel].shape[0] + 1),
               _data[glabel], color='b',
               zorder=2, label='%s' % (year,))
    ax.bar(np.arange(1, 366), df2[(glabel, '95%')] - df2[(glabel, '5%')],
           bottom=df2[(glabel, '5%')], ec='tan', fc='tan',
           zorder=1, label='5-95 Percentile')
    ax.bar(np.arange(1, 366), df2[(glabel, '75%')] - df2[(glabel, '25%')],
           bottom=df2[(glabel, '25%')],
           ec='lightblue',
           fc='lightblue', zorder=1, label='25-75 Percentile')
    ax.set_xlim(1, 367)
    ax.set_ylim(-0.25, 40)
    ax.grid(True)
    ax.set_title("%s-%s %s [%s]\n%s Daily Growing Degree Days (%s/%s)" % (
                syear, thisyear, nt.sts[station]['name'], station, year,
                base, ceiling))
    ax.set_ylabel("Daily Accumulation $^{\circ}\mathrm{F}$")
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274,
                   305, 335, 365))
    ax.legend(ncol=2)
    ax.set_xticklabels(calendar.month_abbr[1:])

    # collapse the multiindex for columns
    df2.columns = ['_'.join(col).strip() for col in df2.columns.values]
    return fig, df2

if __name__ == '__main__':
    plotter(dict())
