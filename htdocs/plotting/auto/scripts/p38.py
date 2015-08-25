import psycopg2.extras
import numpy as np
import calendar
import datetime
import pandas as pd
from pyiem.network import Table as NetworkTable


def smooth(x, window_len=11, window='hanning'):

    s = np.r_[2*x[0]-x[window_len:1:-1], x, 2*x[-1]-x[-1:-window_len:-1]]
    if window == 'flat':  # moving average
        w = np.ones(window_len, 'd')
    else:
        w = eval('np.'+window+'(window_len)')

    y = np.convolve(w/w.sum(), s, mode='same')
    return y[window_len-1:-window_len+1]


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This plot presents yearly estimates of daily
    solar radiation for the 'climodat' stations tracked by the IEM.  These
    stations only report temperature, precipitation, and snowfall, but many
    users are interested in solar radiation data as well.  So estimates
    are pulled from various reanalysis and forecast model analyses to generate
    the numbers presented.  Data availability for NARR is lagged, so data
    from MERRA is used and if MERRA is unavailable, estimates from NCEP HRRR
    analysis is used."""
    d['arguments'] = [
        dict(type='station', name='station', default='IA0200',
             label='Select Station:'),
        dict(type='year', name='year', default=datetime.date.today().year,
             min=1979, label='Select Year to Plot:'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'IA0200')
    year = int(fdict.get('year', 2014))

    table = "alldata_%s" % (station[:2],)
    nt = NetworkTable("%sCLIMATE" % (station[:2],))

    # HRRR data seems to be a big low, so 1.1 adjust it
    cursor.execute("""
     SELECT sday,
     sum(case when (narr_srad < (0.75 * thres) and
                    narr_srad < (0.75 * thres) and
                    narr_srad < (0.75 * thres)) then 1 else 0 end),
     max(thres),
     max(case when year = %s then
         coalesce(narr_srad, merra_srad, hrrr_srad * 1.1) else 0 end) from

     (SELECT sday, year, merra_srad, hrrr_srad,
     narr_srad, max(narr_srad) OVER (partition by sday) as thres,
     lag(narr_srad) OVER (ORDER by day ASC),
     lead(narr_srad) OVER (ORDER by day ASC)
     from """ + table + """ where
     station = %s  and year > 1978) as foo
     GROUP by sday ORDER by sday ASC
    """, (year, station))

    y = []
    y2 = []
    rows = []
    for row in cursor:
        y.append(row[2])
        y2.append(row[3])
        rows.append(dict(ob=row[2], maxval=row[3]))
    df = pd.DataFrame(rows)
    y = np.array(y)
    y2 = np.array(y2)

    (fig, ax) = plt.subplots(1, 1)

    smoothed = smooth(y, 5)
    ax.fill_between(range(1, 367), 0, smoothed, color='tan', label="Max")
    ax.bar(range(366), np.where(y2 > smoothed, smoothed, y2), fc='g',
           ec='g', label="%s" % (year,))
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 365))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlim(0, 366)
    lyear = datetime.date.today().year - 1
    ax.set_title(("[%s] %s Daily Solar Radiation\n"
                  "1979-%s NARR Climatology w/ %s NARR + HRRR Estimates"
                  ) % (station, nt.sts[station]['name'], lyear, year))
    ax.legend()
    ax.grid(True)
    ax.set_ylabel("Shortwave Solar Radiation $MJ$ $d^{-1}$")

    return fig, df
