"""Daily avg wind speeds"""
import datetime

import psycopg2.extras
import numpy as np
import pandas as pd
import matplotlib.patheffects as PathEffects
from pyiem.network import Table as NetworkTable
from pyiem.util import drct2text
from pyiem.datatypes import speed
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.plot.use_agg import plt
from pyiem.exceptions import NoDataFound

PDICT = {'KT': 'knots',
         'MPH': 'miles per hour',
         'MPS': 'meters per second',
         'KMH': 'kilometers per hour'}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['cache'] = 86400
    desc['description'] = """This plot displays daily average wind speeds for
    a given year and month of your choice.  These values are computed by the
    IEM using available observations.  Some observation sites explicitly
    produce an average wind speed, but that is not considered for this plot.
    You can download daily summary data
    <a href="/request/daily.phtml" class="alert-link">here</a>.
    The average wind direction
    is computed by vector averaging of the wind speed and direction reports.
    """
    desc['arguments'] = [
        dict(type='sid', name='zstation', default='DSM',
             network='IA_ASOS', label='Select Station:'),
        dict(type='year', name='year', default=datetime.datetime.now().year,
             label='Select Year:'),
        dict(type='month', name='month', default=datetime.datetime.now().month,
             label='Select Month:'),
        dict(type='select', name='units', default='MPH',
             label='Wind Speed Units:', options=PDICT),

    ]
    return desc


def draw_line(x, y, angle):
    """Draw a line"""
    r = 0.25
    plt.arrow(x, y, r * np.cos(angle), r * np.sin(angle),
              head_width=0.35, head_length=0.5, fc='k', ec='k')


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn('iem')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['zstation']
    network = ctx['network']
    units = ctx['units']
    year = ctx['year']
    month = ctx['month']
    sts = datetime.date(year, month, 1)
    ets = (sts + datetime.timedelta(days=35)).replace(day=1)
    nt = NetworkTable(network)

    cursor.execute("""
      SELECT day, avg_sknt, vector_avg_drct from summary s JOIN stations t
      ON (t.iemid = s.iemid) WHERE t.id = %s and t.network = %s and
      s.day >= %s and s.day < %s ORDER by day ASC
    """, (station, network, sts, ets))
    days = []
    drct = []
    sknt = []
    for row in cursor:
        if row[1] is None:
            continue
        days.append(row[0].day)
        drct.append(row[2])
        sknt.append(row[1])
    if not sknt:
        raise NoDataFound("ERROR: No Data Found")
    df = pd.DataFrame(dict(day=pd.Series(days),
                           drct=pd.Series(drct),
                           sknt=pd.Series(sknt)))
    sknt = speed(np.array(sknt), 'KT').value(units)
    (fig, ax) = plt.subplots(1, 1)
    ax.bar(np.array(days), sknt, ec='green', fc='green', align='center')
    pos = max([min(sknt) / 2.0, 0.5])
    for d, _, r in zip(days, sknt, drct):
        draw_line(d, max(sknt)+0.5, (270. - r) / 180. * np.pi)
        txt = ax.text(d, pos, drct2text(r), ha='center', rotation=90,
                      color='white', va='center')
        txt.set_path_effects([PathEffects.withStroke(linewidth=2,
                                                     foreground="k")])
    ax.grid(True, zorder=11)
    ax.set_title(("%s [%s]\n%s Daily Average Wind Speed and Direction"
                  ) % (nt.sts[station]['name'], station,
                       sts.strftime("%b %Y")))
    ax.set_xlim(0.5, 31.5)
    ax.set_xticks(range(1, 31, 5))
    ax.set_ylim(top=max(sknt)+2)

    ax.set_ylabel("Average Wind Speed [%s]" % (PDICT.get(units),))

    return fig, df


if __name__ == '__main__':
    plotter(dict())
