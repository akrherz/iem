import psycopg2.extras
import numpy as np
from pyiem import network
import pandas as pd

PDICT = {'precip': 'Precipitation',
         'high': 'High Temperature',
         'low': 'Low Temperature'}

UNITS = {'precip': 'inch',
         'high': 'F',
         'low': 'F'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This plot produces statistics on min, max, and
    average values of a variable over a window of days.  The labels get
    a bit confusing, but we are looking for previous of time with temperature
    above or below a given threshold.  For precipitation, it is only a period
    with each day above a given threshold and the average over that period.
    """
    d['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station'),
        dict(type='select', name='var', default='precip',
             label='Which Variable:', options=PDICT),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'IA0000')
    varname = fdict.get('var', 'precip')
    if PDICT.get(varname) is None:
        return

    table = "alldata_%s" % (station[:2],)
    nt = network.Table("%sCLIMATE" % (station[:2],))

    rows = []
    for dy in range(1, 32):
        ccursor.execute("""
            with data as (
            select day,
            avg("""+varname+""") OVER
                (ORDER by day ASC rows between %s preceding and current row),
            min("""+varname+""") OVER
                (ORDER by day ASC rows between %s preceding and current row),
            max("""+varname+""") OVER
                (ORDER by day ASC rows between %s preceding and current row)
            from """+table+"""
            where station = %s)
        SELECT max(avg), min(avg), max(min), min(min), max(max), min(max)
        from data
        """, (dy-1, dy-1, dy-1, station))
        row = ccursor.fetchone()
        rows.append(dict(days=dy, highest_avg=row[0], lowest_avg=row[1],
                         highest_min=row[2], lowest_min=row[3],
                         highest_max=row[4], lowest_max=row[5]))
    df = pd.DataFrame(rows)

    fig, ax = plt.subplots(1, 1)
    if varname == 'precip':
        ax.plot(np.arange(1, 32), df['highest_avg'], color='b',
                label='Highest Average', lw=2)
        ax.plot(np.arange(1, 32), df['highest_min'], color='g',
                label='Consec Days Over', lw=2)
        ax.plot(np.arange(1, 32), df['lowest_min'], color='r',
                label='Consec Days Under', lw=2)
    else:
        ax.plot(np.arange(1, 32), df['highest_avg'],
                label='Highest Average', lw=2)
        ax.plot(np.arange(1, 32), df['lowest_avg'],
                label='Lowest Average', lw=2)
        ax.plot(np.arange(1, 32), df['highest_min'],
                label='Highest Above', lw=2)
        ax.plot(np.arange(1, 32), df['lowest_max'],
                label='Lowest Below', lw=2)
    msg = ("[%s] %s Statistics of %s over 1-31 Consecutive Days"
           ) % (station, nt.sts[station]['name'], PDICT.get(varname))
    tokens = msg.split()
    sz = len(tokens) / 2
    ax.set_title(" ".join(tokens[:sz]) + "\n" + " ".join(tokens[sz:]))
    ax.set_ylabel("%s (%s)" % (PDICT.get(varname), UNITS.get(varname)))
    ax.set_xlabel("Consecutive Days")
    ax.grid(True)
    ax.set_xlim(0.5, 31.5)

    # Shrink current axis's height by 10% on the bottom
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.15,
                     box.width, box.height * 0.85])

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1),
              fancybox=True, shadow=True, ncol=3, scatterpoints=1, fontsize=12)

    return fig, df
