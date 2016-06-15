import psycopg2
from pyiem.network import Table as NetworkTable
from pandas.io.sql import read_sql
import datetime


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['cache'] = 86400
    d['description'] = """This plot presents a time series of Arridity Index.
    This index computes the standardized high temperature departure subtracted
    by the standardized precipitation departure.  For the purposes of this
    plot, this index is computed daily over a trailing period of days of your
    choice.  The climatology is based on the present period of record
    statistics.
    """
    today = datetime.date.today()
    sts = today - datetime.timedelta(days=180)
    d['arguments'] = [
        dict(type='station', name='station', default='IA0200',
             label='Select Station:'),
        dict(type='text', name='days', default=91,
             label='Number of Days'),
        dict(type='date', name='sdate', default=sts.strftime("%Y/%m/%d"),
             min='1893/01/01',
             label='Start Date of Plot'),
        dict(type='date', name='edate', default=today.strftime("%Y/%m/%d"),
             min='1893/01/01',
             label='End Date of Plot'),

    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    station = fdict.get('station', 'IA0200')
    network = fdict.get('network', 'IACLIMATE')
    days = int(fdict.get('days', 91))
    sts = datetime.datetime.strptime(fdict.get('sdate', '2015-12-25'),
                                     '%Y-%m-%d')
    ets = datetime.datetime.strptime(fdict.get('edate', '2015-12-25'),
                                     '%Y-%m-%d')
    nt = NetworkTable(network)
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')

    table = "alldata_%s" % (station[:2], )
    df = read_sql("""
    WITH agg as (
        SELECT o.day, o.sday,
        avg(high) OVER (ORDER by day ASC ROWS %s PRECEDING) as avgt,
        sum(precip) OVER (ORDER by day ASC ROWS %s PRECEDING) as sump,
        count(*) OVER (ORDER by day ASC ROWS %s PRECEDING) as cnt
        from """ + table + """ o WHERE station = %s),
    agg2 as (
        SELECT sday, avg(avgt) as avg_avgt,
        stddev(avgt) as std_avgt, avg(sump) as avg_sump,
        stddev(avgt) as std_sump from agg WHERE cnt = %s GROUP by sday)

    SELECT day, (a.avgt - b.avg_avgt) / b.std_avgt as t,
    (a.sump - b.avg_sump) / b.std_sump as p
    from agg a JOIN agg2 b on (a.sday = b.sday) WHERE day >= %s and day <= %s
    ORDER by day ASC
    """, pgconn, params=(days - 1, days - 1, days - 1, station, days,
                         sts, ets),
                  index_col='day')
    df['arridity'] = df['t'] - df['p']
    (fig, ax) = plt.subplots(1, 1)

    ax.plot(df.index.values, df['arridity'], color='r')
    ax.grid(True)
    ax.set_title(("%s [%s] %s Day Arridity Index\n"
                  "Std. High Temp Departure minus Std. Precip Departure"
                  ) % (nt.sts[station]['name'], station, days))
    maxval = df['arridity'].abs().max() + 0.25
    ax.set_ylim(0 - maxval, maxval)
    ax.set_ylabel("Arridity Index")
    ax.text(1.01, 0.75, "<-- More Water Stress", ha='left', va='center',
            transform=ax.transAxes, rotation=-90)
    ax.text(1.01, 0.25, "Less Water Stress -->", ha='left', va='center',
            transform=ax.transAxes, rotation=-90)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%-d %b\n%Y'))
    return fig, df


if __name__ == '__main__':
    plotter(dict())
