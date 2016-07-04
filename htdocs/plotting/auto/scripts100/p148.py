import psycopg2
from pyiem.network import Table as NetworkTable
from pandas.io.sql import read_sql
from collections import OrderedDict
import datetime
import mx.DateTime

PDICT = OrderedDict([
        ('memorial', 'Memorial Day'),
        ('exact', 'Same Date each Year'),
        ])
PDICT2 = OrderedDict([
        ('high', 'High Temperature [F]'),
        ('low', 'Low Temperature [F]'),
        ('precip', 'Precipitation [inch]'),
        ])


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['cache'] = 86400
    d['description'] = """This plot presents a daily observation for a site
    and year on a given date / holiday date each year.  A large caveat to this
    chart is that much of the long term daily climate data is for a 24 hour
    period ending at around 7 AM.
    """
    d['arguments'] = [
        dict(type='station', name='station', default='IA0200',
             label='Select Station:'),
        dict(type='select', name='date', default='memorial', options=PDICT,
             label='Which date/holiday to plot?'),
        dict(type='date', name='thedate', default='2000/01/01',
             min='2000/01/01', max='2000/12/31',
             label='Same date each year to plot (when selected above):'),
        dict(type='select', name='var', default='high',
             label='Which variable to plot?', options=PDICT2)
    ]
    return d


def memorial_days():
    days = []
    for year in range(1971, datetime.date.today().year + 1):
        may31 = mx.DateTime.DateTime(year, 5, 31)
        memorial = may31 + mx.DateTime.RelativeDateTime(
                                        weekday=(mx.DateTime.Monday, -1))
        days.append(datetime.date(year, 5, memorial.day))
    return days


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    station = fdict.get('station', 'IA0200')
    network = fdict.get('network', 'IACLIMATE')
    varname = fdict.get('var', 'high')
    thedate = datetime.datetime.strptime(fdict.get('thedate', '2000-01-01'),
                                         '%Y-%m-%d')

    date = fdict.get('date', 'memorial')
    nt = NetworkTable(network)
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')

    table = "alldata_%s" % (station[:2], )
    if date == 'exact':
        df = read_sql("""
        SELECT year, high, precip from """ + table + """ WHERE station = %s
        and sday = %s ORDER by year ASC
        """, pgconn, params=(station, thedate.strftime("%m%d")),
                      index_col='year')
        subtitle = thedate.strftime("%B %-d")
    else:
        days = memorial_days()

        df = read_sql("""
        SELECT year, high, precip from """ + table + """ WHERE station = %s
        and day in %s ORDER by year ASC
        """, pgconn, params=(station, tuple(days)),
                      index_col='year')
        subtitle = PDICT[date]

    (fig, ax) = plt.subplots(1, 1)

    ax.bar(df.index.values, df[varname], fc='r', ec='r', align='center')
    mean = df[varname].mean()
    ax.axhline(mean)
    ax.text(df.index.values[-1] + 1, mean, '%.2f' % (mean,), ha='left',
            va='center')
    ax.grid(True)
    ax.set_title(("%s [%s] Daily %s\non %s"
                  ) % (nt.sts[station]['name'], station, PDICT2[varname],
                       subtitle))
    ax.set_xlim(df.index.values.min() - 1,
                df.index.values.max() + 1)
    ax.set_ylabel(PDICT2[varname])
    if varname != 'precip':
        ax.set_ylim(df[varname].min() - 5, df[varname].max() + 5)
    return fig, df


if __name__ == '__main__':
    plotter(dict())
