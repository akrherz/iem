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
    statistics.  You can optionally plot this index for two other period of
    days of your choice.  Entering '0' will disable additional lines appearing
    on the plot.
    """
    today = datetime.date.today()
    sts = today - datetime.timedelta(days=180)
    d['arguments'] = [
        dict(type='station', name='station', default='IA0200',
             label='Select Station:'),
        dict(type='text', name='days', default=91,
             label='Number of Days #1'),
        dict(type='text', name='days2', default=0,
             label='Number of Days #2 (0 disables)'),
        dict(type='text', name='days3', default=0,
             label='Number of Days #3 (0 disables)'),
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
    days2 = int(fdict.get('days2', 0))
    _days2 = days2 if days2 > 0 else 1
    days3 = int(fdict.get('days3', 0))
    _days3 = days3 if days3 > 0 else 1
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
        count(*) OVER (ORDER by day ASC ROWS %s PRECEDING) as cnt,
        avg(high) OVER (ORDER by day ASC ROWS %s PRECEDING) as avgt2,
        sum(precip) OVER (ORDER by day ASC ROWS %s PRECEDING) as sump2,
        count(*) OVER (ORDER by day ASC ROWS %s PRECEDING) as cnt2,
        avg(high) OVER (ORDER by day ASC ROWS %s PRECEDING) as avgt3,
        sum(precip) OVER (ORDER by day ASC ROWS %s PRECEDING) as sump3,
        count(*) OVER (ORDER by day ASC ROWS %s PRECEDING) as cnt3
        from """ + table + """ o WHERE station = %s),
    agg2 as (
        SELECT sday,
        avg(avgt) as avg_avgt, stddev(avgt) as std_avgt,
        avg(sump) as avg_sump, stddev(sump) as std_sump,
        avg(avgt2) as avg_avgt2, stddev(avgt2) as std_avgt2,
        avg(sump2) as avg_sump2, stddev(sump2) as std_sump2,
        avg(avgt3) as avg_avgt3, stddev(avgt3) as std_avgt3,
        avg(sump3) as avg_sump3, stddev(sump3) as std_sump3
        from agg WHERE cnt = %s GROUP by sday)

    SELECT day,
    (a.avgt - b.avg_avgt) / b.std_avgt as t,
    (a.sump - b.avg_sump) / b.std_sump as p,
    (a.avgt2 - b.avg_avgt2) / b.std_avgt2 as t2,
    (a.sump2 - b.avg_sump2) / b.std_sump2 as p2,
    (a.avgt3 - b.avg_avgt3) / b.std_avgt3 as t3,
    (a.sump3 - b.avg_sump3) / b.std_sump3 as p3
    from agg a JOIN agg2 b on (a.sday = b.sday) WHERE day >= %s and day <= %s
    ORDER by day ASC
    """, pgconn, params=(days - 1, days - 1, days - 1,
                         _days2 - 1, _days2 - 1, _days2 - 1,
                         _days3 - 1, _days3 - 1, _days3 - 1,
                         station, days,
                         sts, ets),
                  index_col='day')
    df['arridity'] = df['t'] - df['p']
    df['arridity2'] = df['t2'] - df['p2']
    df['arridity3'] = df['t3'] - df['p3']
    (fig, ax) = plt.subplots(1, 1)

    ax.plot(df.index.values, df['arridity'], color='r', lw=2,
            label='%s days' % (days,))
    maxval = df['arridity'].abs().max() + 0.25
    if days2 > 0:
        ax.plot(df.index.values, df['arridity2'], color='b', lw=2,
                label='%s days' % (days2,))
        maxval = max([maxval, df['arridity2'].abs().max() + 0.25])
    if days3 > 0:
        ax.plot(df.index.values, df['arridity3'], color='g', lw=2,
                label='%s days' % (days3,))
        maxval = max([maxval, df['arridity3'].abs().max() + 0.25])
    ax.grid(True)
    ax.set_title(("%s [%s] %s Day Arridity Index\n"
                  "Std. High Temp Departure minus Std. Precip Departure"
                  ) % (nt.sts[station]['name'], station, days))
    ax.set_ylim(0 - maxval, maxval)
    ax.set_ylabel("Arridity Index")
    ax.text(1.01, 0.75, "<-- More Water Stress", ha='left', va='center',
            transform=ax.transAxes, rotation=-90)
    ax.text(1.01, 0.25, "Less Water Stress -->", ha='left', va='center',
            transform=ax.transAxes, rotation=-90)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%-d %b\n%Y'))
    ax.legend(ncol=3, loc='best')
    return fig, df


if __name__ == '__main__':
    plotter(dict())
