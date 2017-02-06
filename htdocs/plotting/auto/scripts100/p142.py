import psycopg2
import datetime
from pyiem.network import Table as NetworkTable
from pandas.io.sql import read_sql
from pyiem.util import get_autoplot_context
from collections import OrderedDict

PDICT = OrderedDict([
        ('precip', 'Precipitation [inch]'),
        ('avgt', 'Daily Average Temperature [F]'),
        ('high', 'Daily High Temperature [F]'),
        ('low', 'Daily Low Temperature [F]')])


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['cache'] = 86400
    d['description'] = """This plot presents the trailing X number of days
    temperature or precipitation departure from long term average.
    """
    today = datetime.date.today()
    sts = today - datetime.timedelta(days=720)
    d['arguments'] = [
        dict(type='station', name='station', default='IA0200',
             label='Select Station:', network='IACLIMATE'),
        dict(type='int', name='p1', default=31, label='First Period of Days'),
        dict(type='int', name='p2', default=91,
             label='Second Period of Days'),
        dict(type='int', name='p3', default=365,
             label='Third Period of Days'),
        dict(type='date', name='sdate', default=sts.strftime("%Y/%m/%d"),
             min='1893/01/01',
             label='Start Date of Plot'),
        dict(type='date', name='edate', default=today.strftime("%Y/%m/%d"),
             min='1893/01/01',
             label='End Date of Plot'),
        dict(type='select', name='pvar', default='precip', options=PDICT,
             label='Which variable to plot?'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']
    network = ctx['network']
    nt = NetworkTable(network)
    p1 = ctx['p1']
    p2 = ctx['p2']
    p3 = ctx['p3']
    pvar = ctx['pvar']
    sts = ctx['sdate']
    ets = ctx['edate']
    bts = sts - datetime.timedelta(days=max([p1, p2, p3]))

    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')

    table = "alldata_%s" % (station[:2], )
    df = read_sql("""
    WITH obs as (
        SELECT day,
        high - avg(high) OVER (PARTITION by sday) as high_diff,
        low - avg(low) OVER (PARTITION by sday) as low_diff,
        ((high+low)/2.) -
         avg((high+low)/2.) OVER (PARTITION by sday) as avgt_diff,
        precip - avg(precip) OVER (PARTITION by sday) as precip_diff
        from """ + table + """
        WHERE station = %s ORDER by day ASC),
    lags as (
      SELECT day,
      avg(high_diff) OVER (ORDER by day ASC ROWS %s PRECEDING) as p1_high_diff,
      avg(high_diff) OVER (ORDER by day ASC ROWS %s PRECEDING) as p2_high_diff,
      avg(high_diff) OVER (ORDER by day ASC ROWS %s PRECEDING) as p3_high_diff,
      avg(low_diff) OVER (ORDER by day ASC ROWS %s PRECEDING) as p1_low_diff,
      avg(low_diff) OVER (ORDER by day ASC ROWS %s PRECEDING) as p2_low_diff,
      avg(low_diff) OVER (ORDER by day ASC ROWS %s PRECEDING) as p3_low_diff,
      avg(avgt_diff) OVER (ORDER by day ASC ROWS %s PRECEDING) as p1_avgt_diff,
      avg(avgt_diff) OVER (ORDER by day ASC ROWS %s PRECEDING) as p2_avgt_diff,
      avg(avgt_diff) OVER (ORDER by day ASC ROWS %s PRECEDING) as p3_avgt_diff,
      sum(precip_diff)
          OVER (ORDER by day ASC ROWS %s PRECEDING) as p1_precip_diff,
      sum(precip_diff)
          OVER (ORDER by day ASC ROWS %s PRECEDING) as p2_precip_diff,
      sum(precip_diff)
          OVER (ORDER by day ASC ROWS %s PRECEDING) as p3_precip_diff
    from obs WHERE day >= %s and day <= %s)

    SELECT * from lags where day >= %s and day <= %s ORDER by day ASC
    """, pgconn, params=(station, p1, p2, p3, p1, p2, p3, p1, p2, p3,
                         p1, p2, p3, bts, ets, sts, ets), index_col='day')

    (fig, ax) = plt.subplots(1, 1, figsize=(8, 6))

    ax.plot(df.index.values, df['p1_'+pvar+'_diff'], lw=2,
            label='%s Day' % (p1, ))
    ax.plot(df.index.values, df['p2_'+pvar+'_diff'], lw=2,
            label='%s Day' % (p2, ))
    ax.plot(df.index.values, df['p3_'+pvar+'_diff'], lw=2,
            label='%s Day' % (p3, ))
    ax.set_title(("[%s] %s\nTrailing %s, %s, %s Day Departures"
                  ) % (station, nt.sts[station]['name'], p1, p2, p3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
    ax.set_ylabel(PDICT.get(pvar))
    ax.grid(True)
    ax.legend(ncol=3, fontsize=12, loc='best')
    ax.text(1, -0.12, "%s to %s" % (sts.strftime("%-d %b %Y"),
                                    ets.strftime("%-d %b %Y")), va='bottom',
            ha='right', fontsize=12, transform=ax.transAxes)

    return fig, df


if __name__ == '__main__':
    plotter(dict())
