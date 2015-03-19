import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import psycopg2.extras
import datetime
import numpy as np
import math
from pyiem.network import Table as NetworkTable
import calendar

PDICT = {'yes': "Limit Plot to Year-to-Date",
         'no': 'Plot Entire Year'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['cache'] = 86400
    d['description'] = """This plot displays an accumulated total of
    Severe Thunderstorm and Tornado Warnings.  These totals are not official
    and based on IEM processing of NWS text warning data.  The totals are for
    individual warnings and not some combination of counties + warnings."""
    d['arguments'] = [
        dict(type='networkselect', name='station', network='WFO',
             default='DMX', label='Select WFO:', all=True),
        dict(type='select', name='limit', default='no',
             label='End Date Limit to Plot:', options=PDICT),

    ]
    return d


def plotter(fdict):
    """ Go """
    pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'DMX')
    limit = fdict.get('limit', 'no')

    nt = NetworkTable('WFO')
    nt.sts['_ALL'] = {'name': 'All Offices'}

    lastdoy = 367
    if limit.lower() == 'yes':
        lastdoy = int(datetime.datetime.today().strftime("%j")) + 1

    if station == '_ALL':
        cursor.execute("""
            with counts as (
                select extract(year from issue) as yr,
                extract(doy from issue) as doy, count(*) from sbw
                where status = 'NEW' and phenomena in ('SV', 'TO')
                and significance = 'W' and issue > '2003-01-01'
                and extract(doy from issue) < %s
                GROUP by yr, doy)

            SELECT yr, doy, sum(count) OVER (PARTITION by yr ORDER by doy ASC)
            from counts ORDER by yr ASC, doy ASC
          """, (lastdoy, ))

    else:
        cursor.execute("""
            with counts as (
                select extract(year from issue) as yr,
                extract(doy from issue) as doy, count(*) from sbw
                where status = 'NEW' and phenomena in ('SV', 'TO')
                and significance = 'W' and wfo = %s and issue > '2003-01-01'
                and extract(doy from issue) < %s
                GROUP by yr, doy)

            SELECT yr, doy, sum(count) OVER (PARTITION by yr ORDER by doy ASC)
            from counts ORDER by yr ASC, doy ASC
          """, (station, lastdoy))

    data = {}
    for yr in range(2003, datetime.datetime.now().year + 1):
        data[yr] = {'doy': [], 'counts': []}
    for row in cursor:
        data[row[0]]['doy'].append(row[1])
        data[row[0]]['counts'].append(row[2])

    (fig, ax) = plt.subplots(1, 1)
    ann = []
    for yr in range(2003, datetime.datetime.now().year + 1):
        if len(data[yr]['doy']) < 2:
            continue
        l = ax.plot(data[yr]['doy'], data[yr]['counts'], lw=2,
                    label="%s (%s)" % (str(yr), data[yr]['counts'][-1]))
        ann.append(
            ax.text(data[yr]['doy'][-1]+1, data[yr]['counts'][-1],
                    "%s" % (yr,), color='w', va='center',
                    fontsize=10, bbox=dict(facecolor=l[0].get_color(),
                                           edgecolor=l[0].get_color()))
            )

    mask = np.zeros(fig.canvas.get_width_height(), bool)
    fig.canvas.draw()

    attempts = 10
    while len(ann) > 0 and attempts > 0:
        attempts -= 1
        removals = []
        for a in ann:
            bbox = a.get_window_extent()
            x0 = int(bbox.x0)
            x1 = int(math.ceil(bbox.x1))
            y0 = int(bbox.y0)
            y1 = int(math.ceil(bbox.y1))

            s = np.s_[x0:x1+1, y0:y1+1]
            if np.any(mask[s]):
                a.set_position([a._x-int(lastdoy/14), a._y])
            else:
                mask[s] = True
                removals.append(a)
        for rm in removals:
            ann.remove(rm)

    ax.legend(loc=2, ncol=2, fontsize=10)
    ax.set_xlim(1, 367)
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 365))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.grid(True)
    ax.set_ylabel("Accumulated Count")
    ax.set_title(("NWS %s\nSevere Thunderstorm + Tornado Warning Count"
                  ) % (nt.sts[station]['name'],))
    ax.set_xlim(0, lastdoy)
    if lastdoy < 367:
        ax.set_xlabel(("thru approximately %s"
                       ) % (datetime.date.today().strftime("%-d %b"), ))

    return fig
