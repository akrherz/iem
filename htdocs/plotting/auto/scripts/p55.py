"""Climatologies comparison"""
import datetime
import calendar

import psycopg2.extras
import numpy as np
import pandas as pd
from pyiem.network import Table as NetworkTable
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['description'] = """This plot displays a comparison of various daily
    temperature climatologies.  The National Center for Environmental
    Information (NCEI) releases a 30 year climatology every ten years.  This
    data is smoothed to remove day to day variability.  The raw daily averages
    are shown computed from the daily observation archive maintained by the
    IEM."""
    desc['arguments'] = [
        # IATDSM has some troubles here
        dict(type='station', name='station', default='IA2203',
             network='IACLIMATE', label='Select Station:'),
        dict(type='month', name='month', default='12',
             label='Select Month:')
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn('coop')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']
    month = ctx['month']

    table = "alldata_%s" % (station[:2],)
    nt = NetworkTable("%sCLIMATE" % (station[:2],))

    # beat month
    cursor.execute("""
    with obs as (
     SELECT sday, avg(high) as avgh, avg(low) as avgl,
     avg((high+low)/2.) as avgt from """+table+"""
     WHERE station = %s and month = %s GROUP by sday
    ), c81 as (
     SELECT to_char(valid, 'mmdd') as sday, high, low, (high+low)/2. as avgt
     from ncdc_climate81 where station = %s
    ), c71 as (
     SELECT to_char(valid, 'mmdd') as sday, high, low, (high+low)/2. as avgt
     from ncdc_climate71 where station = %s
    )

    SELECT o.sday, o.avgh, c81.high, c71.high,
    o.avgl, c81.low, c71.low,
    o.avgt, c81.avgt, c71.avgt from
    obs o, c81, c71 where o.sday = c81.sday and o.sday = c71.sday
    ORDER by o.sday ASC
    """, (station, month, nt.sts[station]['ncdc81'],
          station))
    if cursor.rowcount == 0:
        raise NoDataFound("No Data Found.")

    o_avgh = []
    o_avgl = []
    o_avgt = []
    c81_avgh = []
    c81_avgl = []
    c81_avgt = []
    c71_avgh = []
    c71_avgl = []
    c71_avgt = []
    days = []
    for row in cursor:
        days.append(int(row[0][2:]))
        o_avgh.append(float(row[1]))
        o_avgl.append(float(row[4]))
        o_avgt.append(float(row[7]))

        c81_avgh.append(row[2])
        c81_avgl.append(row[5])
        c81_avgt.append(row[8])

        c71_avgh.append(row[3])
        c71_avgl.append(row[6])
        c71_avgt.append(row[9])

    df = pd.DataFrame(dict(day=pd.Series(days),
                           iem_avgh=pd.Series(o_avgh),
                           iem_avgl=pd.Series(o_avgl),
                           iem_avgt=pd.Series(o_avgt),
                           ncei81_avgh=pd.Series(c81_avgh),
                           ncei81_avgl=pd.Series(c81_avgl),
                           ncei81_avgt=pd.Series(c81_avgt),
                           ncei71_avgh=pd.Series(c71_avgh),
                           ncei71_avgl=pd.Series(c71_avgl),
                           ncei71_avgt=pd.Series(c71_avgt)))

    days = np.array(days)

    (fig, ax) = plt.subplots(3, 1, sharex=True, figsize=(8, 6))

    ax[0].set_title(("%s %s Daily Climate Comparison\n"
                     "Observation Period: %s-%s for %s"
                     ) % (station,
                          nt.sts[station]['name'],
                          nt.sts[station]['archive_begin'].year,
                          datetime.datetime.now().year,
                          calendar.month_name[month]), fontsize=12)

    ax[0].bar(days, o_avgh, width=0.8, fc='tan', align='center')
    ax[0].plot(days, c81_avgh, lw=2, zorder=2, color='g')
    ax[0].plot(days, c71_avgh, lw=2, zorder=2, color='r')
    ax[0].grid(True)
    ax[0].set_ylabel(r"High Temp $^\circ$F")
    ax[0].set_ylim(
        bottom=min([min(o_avgh), min(c71_avgh), min(c81_avgh)])-2)

    ax[1].bar(days, o_avgl, width=0.8, fc='tan', align='center')
    ax[1].plot(days, c81_avgl, lw=2, zorder=2, color='g')
    ax[1].plot(days, c71_avgl, lw=2, zorder=2, color='r')
    ax[1].grid(True)
    ax[1].set_ylabel(r"Low Temp $^\circ$F")
    ax[1].set_ylim(
        bottom=min([min(o_avgl), min(c71_avgl), min(c81_avgl)])-2)

    ax[2].bar(days, o_avgt, width=0.8, fc='tan', align='center',
              label='IEM Observered Avg')
    ax[2].plot(days, c81_avgt, lw=2, zorder=2, color='g',
               label='NCEI 1981-2010')
    ax[2].plot(days, c71_avgt, lw=2, zorder=2, color='r',
               label='NCEI 1971-2000')
    ax[2].grid(True)
    ax[2].legend(loc='lower center', bbox_to_anchor=(0.5, 0.95),
                 fancybox=True, shadow=True, ncol=3, scatterpoints=1,
                 fontsize=10)

    ax[2].set_ylabel(r"Average Temp $^\circ$F")
    ax[2].set_ylim(bottom=min([min(o_avgt), min(c71_avgt), min(c81_avgt)])-2)
    ax[2].set_xlabel("Day of %s" % (calendar.month_name[month],))
    ax[2].set_xlim(0.5, len(days)+0.5)

    return fig, df


if __name__ == '__main__':
    plotter(dict())
