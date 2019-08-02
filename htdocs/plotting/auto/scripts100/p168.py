"""First fall or last spring"""
import calendar
import datetime

from pandas.io.sql import read_sql
import numpy as np
from pyiem import util
from pyiem.plot.use_agg import plt
from pyiem.exceptions import NoDataFound


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['description'] = """This chart presents the last date of fall or first
    date of spring that a given temperature threshold was last or first
    reached.  Note that leap day creates some ambiguity with an analysis like
    this, so for example, the 15th of November is considered equal for each
    year.  The plot truncates once you reach the 20th of December.  If you use
    the downloaded file, please note that you need to consider the levels
    above the given threshold as the latest date.  The downloaded file simply
    provides the latest date at a given temperature.
    """
    desc['arguments'] = [
        dict(type='station', name='station', default='IATDSM',
             label='Select Station:', network='IACLIMATE')
        ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = util.get_dbconn('coop')
    ctx = util.get_autoplot_context(fdict, get_description())
    station = ctx['station']
    table = "alldata_%s" % (station[:2],)
    df = read_sql("""
    with data as (
        select day, high, year,
        rank() OVER (PARTITION by high ORDER by sday DESC)
        from """ + table + """ where station = %s)
    SELECT day, year, high, rank from data WHERE rank = 1
    ORDER by high DESC, day DESC
    """, pgconn, params=(station, ), index_col=None)
    if df.empty:
        raise NoDataFound("No data found!")

    (fig, ax) = plt.subplots(1, 1, figsize=(6, 8))
    current = {'d2000': datetime.date(2000, 1, 1),
               'date': datetime.date(2000, 1, 1),
               'ties': False}
    x = []
    y = []
    for level in np.arange(df['high'].max(), 0, -1):
        if level not in df['high']:
            continue
        df2 = df[df['high'] == level]
        row = df2.iloc[0]
        if row['day'].replace(year=2000) > current['d2000']:
            current['d2000'] = row['day'].replace(year=2000)
            current['date'] = row['day']
            current['ties'] = (len(df2.index) > 1)
        if current['date'].month == 12 and current['date'].day > 20:
            break
        y.append(level)
        x.append(int(current['d2000'].strftime("%j")))
        ax.text(x[-1] + 3, level,
                "%s -- %s %s%s" % (level, current['d2000'].strftime("%-d %b"),
                                   current['date'].year,
                                   " **" if current['ties'] else ""),
                va='center')
    ax.barh(y, x, align='center')
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 365))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlim(min(x) - 5, 400)
    ax.set_ylim(y[-1] - 1, y[0] + 1)
    ax.grid(True)
    ab = ctx['_nt'].sts[station]['archive_begin']
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    ax.set_title(("Most Recent & Latest Date of High Temperature\n"
                  "[%s] %s (%s-%s)"
                  ) % (station, ctx['_nt'].sts[station]['name'],
                       ab.year,
                       datetime.date.today().year))
    ax.set_ylabel(r"High Temperature $^\circ$F")
    ax.set_xlabel("** denotes ties")

    return fig, df


if __name__ == '__main__':
    plotter(dict())
