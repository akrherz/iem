"""Day freq of month"""
import calendar
import datetime

from pandas.io.sql import read_sql
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn

PDICT = {'cold': 'Coldest Temperature',
         'hot': 'Hottest Temperature'}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['description'] = """This plot displays the frequency of a given day
    in the month having the coldest high or low temperature of that month for
    a year."""
    today = datetime.date.today()
    desc['arguments'] = [
        dict(type='station', name='station', default='IATDSM',
             label='Select Station:', network='IACLIMATE'),
        dict(type='month', name='month', default=today.month,
             label='Select Month:'),
        dict(type="select", name='dir', default='cold',
             label='Select variable to plot:', options=PDICT),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn('coop')
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']
    month = ctx['month']
    mydir = ctx['dir']
    ts = datetime.datetime(2000, month, 1)
    ets = ts + datetime.timedelta(days=35)
    ets = ets.replace(day=1)
    days = int((ets - ts).days)

    table = "alldata_%s" % (station[:2],)

    s = "ASC" if mydir == 'cold' else 'DESC'
    df = read_sql("""
        with ranks as (
            select day, high, low,
    rank() OVER (PARTITION by year ORDER by high """ + s + """) as high_rank,
    rank() OVER (PARTITION by year ORDER by low """ + s + """) as low_rank
            from """ + table + """ where station = %s and month = %s),
        highs as (
            SELECT extract(day from day) as dom, count(*) from ranks
            where high_rank = 1 GROUP by dom),
        lows as (
            SELECT extract(day from day) as dom, count(*) from ranks
            where low_rank = 1 GROUP by dom)

        select coalesce(h.dom, l.dom) as dom, h.count as high_count,
        l.count as low_count from
        highs h FULL OUTER JOIN lows l on (h.dom = l.dom) ORDER by h.dom
    """, pgconn, params=(station, month))

    fig, ax = plt.subplots(2, 1, sharex=True)
    lbl = 'Coldest' if mydir == 'cold' else 'Hottest'
    ax[0].set_title(("[%s] %s\nFrequency of Day in %s\n"
                     "Having %s High Temperature of %s"
                     ) % (station, ctx['_nt'].sts[station]['name'],
                          calendar.month_name[month], lbl,
                          calendar.month_name[month]), fontsize=10)
    ax[0].set_ylabel("Years (ties split)")

    ax[0].grid(True)
    ax[0].bar(df['dom'], df['high_count'], align='center')

    ax[1].set_title(("Having %s Low Temperature of %s"
                     ) % (lbl, calendar.month_name[month], ),
                    fontsize=10)
    ax[1].set_ylabel("Years (ties split)")
    ax[1].grid(True)
    ax[1].set_xlabel("Day of %s" % (calendar.month_name[month], ))
    ax[1].bar(df['dom'], df['low_count'], align='center')
    ax[1].set_xlim(0.5, days + 0.5)

    return fig, df


if __name__ == '__main__':
    plotter(dict())
