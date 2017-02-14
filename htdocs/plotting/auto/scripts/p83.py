import psycopg2.extras
import numpy as np
from pyiem import network
import datetime
import pandas as pd
from scipy import stats
from pyiem.util import get_autoplot_context

PDICT = {'high': 'Average High Temperature',
         'low': 'Average Low Temperature',
         'precip': 'Total Precipitation'}
UNITS = {'high': '$^\circ$F',
         'low': '$^\circ$F',
         'precip': 'inch'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This chart presents simple yearly statistics for
    a given day period around a given date.  For example, you can compare
    the previous 45 days to the next 45 days around 15 July.
    """
    d['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station', network='IACLIMATE'),
        dict(type='select', name='var', default='high',
             label='Which Variable:', options=PDICT),
        dict(type='text', name='days', default=45,
             label='How many days:'),
        dict(type='month', name='month', default='7',
             label='Select Month:'),
        dict(type='day', name='day', default='15',
             label='Select Day:'),

    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ctx = get_autoplot_context(fdict, get_description())

    station = ctx['station']
    varname = ctx['var']
    month = ctx['month']
    day = ctx['day']
    dt = datetime.date(2000, month, day)
    days = int(fdict.get('days', 45))
    if PDICT.get(varname) is None:
        return

    table = "alldata_%s" % (station[:2],)
    nt = network.Table("%sCLIMATE" % (station[:2],))

    ccursor.execute("""
    with data as (
        SELECT day,
        count(*) OVER
            (ORDER by day ASC ROWS BETWEEN %s PRECEDING AND 1 PRECEDING) as cb,
        avg(high) OVER
            (ORDER by day ASC ROWS BETWEEN %s PRECEDING AND 1 PRECEDING) as hb,
        avg(low) OVER
            (ORDER by day ASC ROWS BETWEEN %s PRECEDING AND 1 PRECEDING) as lb,
        sum(precip) OVER
            (ORDER by day ASC ROWS BETWEEN %s PRECEDING AND 1 PRECEDING) as pb,
        count(*) OVER
            (ORDER by day ASC ROWS BETWEEN 1 FOLLOWING AND %s FOLLOWING) as ca,
        avg(high) OVER
            (ORDER by day ASC ROWS BETWEEN 1 FOLLOWING AND %s FOLLOWING) as ha,
        avg(low) OVER
            (ORDER by day ASC ROWS BETWEEN 1 FOLLOWING AND %s FOLLOWING) as la,
        sum(precip) OVER
            (ORDER by day ASC ROWS BETWEEN 1 FOLLOWING AND %s FOLLOWING) as pa
        from """+table+""" WHERE station = %s)

    SELECT hb, lb, pb, ha, la, pa from data where cb = ca and
    cb = %s and extract(month from day) = %s and extract(day from day) = %s
    """, (days, days, days, days, days, days, days, days, station,
          days, month, day))
    rows = []
    for row in ccursor:
        rows.append(dict(high_before=row[0], high_after=row[3],
                         low_before=row[1], low_after=row[4],
                         precip_before=row[2], precip_after=row[5]))
    df = pd.DataFrame(rows)

    x = np.array(df[varname+'_before'], 'f')
    y = np.array(df[varname+'_after'], 'f')
    fig, ax = plt.subplots(1, 1, sharex=True, figsize=(8, 6))
    ax.scatter(x, y)
    msg = ("[%s] %s %s over %s days prior to and after %s"
           ) % (station, nt.sts[station]['name'], PDICT.get(varname),
                days, dt.strftime("%-d %B"))
    tokens = msg.split()
    sz = len(tokens) / 2
    ax.set_title(" ".join(tokens[:sz]) + "\n" + " ".join(tokens[sz:]))

    minv = min([min(x), min(y)])
    maxv = max([max(x), max(y)])
    ax.plot([minv-5, maxv+5], [minv-5, maxv+5], label='x=y', color='b')
    yavg = np.average(y)
    xavg = np.average(x)
    ax.axhline(yavg, label='After Avg: %.2f' % (yavg,),
               color='r', lw=2)
    ax.axvline(xavg, label='Before Avg: %.2f' % (xavg,),
               color='g', lw=2)
    df2 = df[np.logical_and(df[varname+'_before'] >= xavg,
                            df[varname+'_after'] >= yavg)]
    ax.text(0.98, 0.98, "I: %.1f%%" % (len(df2) / float(len(x)) * 100.,),
            transform=ax.transAxes, bbox=dict(edgecolor='tan',
                                              facecolor='white'),
            va='top', ha='right', zorder=3)

    df2 = df[np.logical_and(df[varname+'_before'] < xavg,
                            df[varname+'_after'] < yavg)]
    ax.text(0.02, 0.02, "III: %.1f%%" % (len(df2) / float(len(x)) * 100.,),
            transform=ax.transAxes, bbox=dict(edgecolor='tan',
                                              facecolor='white'),
            zorder=3)

    df2 = df[np.logical_and(df[varname+'_before'] >= xavg,
                            df[varname+'_after'] < yavg)]
    ax.text(0.98, 0.02, "IV: %.1f%%" % (len(df2) / float(len(x)) * 100.,),
            transform=ax.transAxes, bbox=dict(edgecolor='tan',
                                              facecolor='white'),
            va='bottom', ha='right', zorder=3)

    df2 = df[np.logical_and(df[varname+'_before'] < xavg,
                            df[varname+'_after'] >= yavg)]
    ax.text(0.02, 0.98, "II: %.1f%%" % (len(df2) / float(len(x)) * 100.,),
            transform=ax.transAxes, bbox=dict(edgecolor='tan',
                                              facecolor='white'),
            va='top', zorder=3)

    ax.set_xlabel("%s %s, %s Days Before" % (PDICT.get(varname),
                                             UNITS.get(varname), days))
    ax.set_ylabel("%s %s, %s Days After" % (PDICT.get(varname),
                                            UNITS.get(varname), days))
    ax.grid(True)
    ax.set_xlim(minv-2, maxv+2)
    ax.set_ylim(minv-2, maxv+2)

    _, _, r_value, _, _ = stats.linregress(x, y)
    ax.text(0.65, 0.02, "R$^2$=%.2f bias=%.2f" % (r_value**2, yavg - xavg),
            ha='right', transform=ax.transAxes, bbox=dict(color='white'))

    # Shrink current axis's height by 10% on the bottom
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.15,
                     box.width, box.height * 0.85])

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1),
              fancybox=True, shadow=True, ncol=3, scatterpoints=1, fontsize=12)

    return fig, df
