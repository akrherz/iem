import psycopg2
from pyiem import network
import numpy as np
import calendar
import pandas as pd

PDICT = {'yes': 'Yes, consider trace reports',
         'no': 'No, omit trace reports'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This plot presents three precipitation metrics for
    a site of your choice.  The upper plot displays the maximum period of days
    in between precip events of either greater than 0.01" (labelled no rain)
    and then of a threshold of your choice.  The bottom plot provides the
    maximum 24 hour period precip as reported by the once daily observatons.
    """
    d['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station'),
        dict(type="text", name="thres", default="0.10",
             label="Precipitation Threshold (inch)"),
        dict(type='select', name='trace', default='no',
             label='Include "trace" reports in the analysis?', options=PDICT),
    ]
    return d


def get_color(val, cat):
    if cat == 't':
        if val > 0:
            return 'r'
        return 'b'
    if val > 0:
        return 'b'
    return 'r'


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    cursor = pgconn.cursor()

    station = fdict.get('station', 'IA2203')
    threshold = float(fdict.get('thres', 0.10))
    use_trace = (fdict.get('trace', 'no').lower() == 'yes')
    table = "alldata_%s" % (station[:2],)
    nt = network.Table("%sCLIMATE" % (station[:2],))

    cursor.execute("""
    with data as (
      select sday, day, precip from """ + table + """
      where station = %s),

    rains as (
      SELECT day from """ + table + """ WHERE station = %s and precip >= %s),

    rains2 as (
      SELECT day from """ + table + """ WHERE station = %s and precip >= %s),

    agg as (
      SELECT d.sday, d.day, d.precip, r.day as rday
      from data d LEFT JOIN rains r ON (d.day = r.day)),

    agg2 as (
      SELECT d.sday, d.day, d.precip, d.rday, r.day as rday2 from
      agg d LEFT JOIN rains2 r ON (d.day = r.day)),

    agg3 as (
      SELECT sday, precip, day - max(rday) OVER (ORDER by day ASC) as diff,
      day - max(rday2) OVER (ORDER by day ASC) as diff2 from agg2)

    SELECT sday, max(precip), max(diff), max(diff2) from agg3
    GROUP by sday ORDER by sday ASC
    """, (station, station, 0.0001 if use_trace else 0.01, station, threshold))
    rows = []
    for row in cursor:
        if row[0] == '0229':
            continue
        rows.append(dict(sday=row[0], maxp=row[1], d1=row[2], d2=row[3]))

    df = pd.DataFrame(rows)

    (fig, ax) = plt.subplots(2, 1, sharex=True)

    ax[0].plot(np.arange(1, 366), df['d1'], c='r', label='No Rain')
    ax[0].plot(np.arange(1, 366), df['d2'], c='b',
               label='Below %.2fin' % (threshold,))
    ax[0].set_ylabel("Consec Days below threshold")
    ax[0].grid(True)
    ax[0].legend(ncol=2, loc=(0.5, -0.13), fontsize=10)
    ax[0].set_title("%s [%s] Precipitation Metrics" % (nt.sts[station]['name'],
                                                       station))
    ax[0].text(0.05, -0.09,
               "Trace Reports %s" % ('Included' if use_trace else 'Excluded',),
               transform=ax[0].transAxes, ha='left')

    ax[1].bar(np.arange(1, 366), df['maxp'], edgecolor='b', facecolor='b')
    ax[1].set_ylabel("Max 24 Hour Precip [inch]")
    ax[1].set_xlim(0.5, 366.5)
    ax[1].set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274,
                      305, 335, 365))
    ax[1].set_xticklabels(calendar.month_abbr[1:])
    ax[1].grid(True)

    return fig, df
