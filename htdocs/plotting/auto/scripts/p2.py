import psycopg2.extras
import numpy as np
from scipy import stats
from pyiem import network
import datetime
import calendar
import pandas as pd


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    today = datetime.datetime.now()
    d['data'] = True
    d['arguments'] = [
        dict(type='station', name='station', default='IA0000',
             label='Select Station'),
        dict(type='month', name='month', default='7', label='Month'),
        dict(type='year', name='year', default=today.year,
             label='Year to Highlight'),
    ]
    d['description'] = """This plot compares the growing degree day vs
    precipitation
    departure for a given month and station.  The departure is expressed in
    units of standard deviation.  So a value of one would represent an one
    standard deviation departure from long term mean.  The mean and standard
    deviation is computed against the current / period of record climatology.
    """
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle
    COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'IA0000')
    month = int(fdict.get('month', 7))
    year = int(fdict.get('year', datetime.datetime.now().year))
    table = "alldata_%s" % (station[:2],)
    nt = network.Table("%sCLIMATE" % (station[:2],))

    ccursor.execute("""
     SELECT stddev(sp) as p, avg(sp) as pavg,
        stddev(tp) as t, avg(tp) as tavg  from
 (    SELECT year, sum(precip) as sp,
         sum(gdd50(high::numeric,low::numeric)) as tp
      from """+table+"""
      where station = %s and month = %s
      GROUP by year) as foo
    """, (station, month))
    row = ccursor.fetchone()
    if row is None or row['p'] is None:
        return "ERROR: No Data Found"
    pstd = float(row['p'])
    pavg = float(row['pavg'])
    tstd = float(row['t'])
    tavg = float(row['tavg'])

    ccursor.execute("""SELECT year, sum(precip) as sp,
      sum(gdd50(high::numeric,low::numeric)) as tp from """ + table + """
      where station = %s and month = %s
      GROUP by year ORDER by year ASC""", (station, month))

    tsigma = []
    psigma = []
    years = []
    dist = []
    for row in ccursor:
        t = float((float(row['tp']) - tavg) / tstd)
        p = float((float(row['sp']) - pavg) / pstd)
        d = ((t * t) + (p * p))**0.5
        tsigma.append(t)
        psigma.append(p)
        dist.append(d)
        years.append(int(row['year']))

    if len(years) == 0:
        return "ERROR: No Data Found!"

    tsigma = np.array(tsigma)
    psigma = np.array(psigma)
    df = pd.DataFrame(dict(year=pd.Series(years),
                           temp_sigma=pd.Series(tsigma),
                           prec_sigma=pd.Series(psigma)))

    h_slope, intercept, r_value, _, _ = stats.linregress(tsigma, psigma)

    y1 = -4.0 * h_slope + intercept
    y2 = 4.0 * h_slope + intercept
    (fig, ax) = plt.subplots(1, 1)

    ax.scatter(tsigma, psigma)
    ax.plot([-4, 4], [y1, y2], label="Slope=%.2f\nR$^2$=%.2f" % (h_slope,
                                                                 r_value ** 2))
    xmax = max(abs(tsigma)) + 0.5
    ymax = max(abs(psigma)) + 0.5
    ax.set_xlim(0 - xmax, xmax)
    ax.set_ylim(0 - ymax, ymax)
    for i in range(len(years)):
        if years[i] in [year, ] or dist[i] > 2.5:
            ax.text(tsigma[i], psigma[i], ' %.0f' % (years[i],), va='center')

    if year in years:
        c = Circle((0, 0), radius=dist[years.index(year)], facecolor='none')
        ax.add_patch(c)
    ax.set_xlabel("Growing Degree Day Departure ($\sigma$)")
    ax.set_ylabel("Precipitation Departure ($\sigma$)")
    ax.grid(True)
    ax.legend(fontsize=10)
    ax.set_title(("%s %s [%s]\n"
                  "Growing Degree Day (base=50) + Precipitation Departure"
                  ) % (
        calendar.month_name[month], nt.sts[station]['name'], station))

    return fig, df
