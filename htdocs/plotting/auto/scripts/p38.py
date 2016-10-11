import numpy as np
import calendar
import psycopg2
import datetime
from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable
from collections import OrderedDict

PDICT = OrderedDict([
        ('best', 'Use NARR, then MERRA, then HRRR'),
        ('narr_srad', 'Use NARR (1979-2015)'),
        ('merra_srad', 'Use MERRA v2'),
        ('hrrr_srad', 'Use HRRR (2013+)')])


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
    the numbers presented.  There are three sources of solar radiation made
    available for this plot.  The HRRR data is the only one in 'real-time',
    the MERRAv2 lags by about a month, and the NARR is no longer produced."""
    d['arguments'] = [
        dict(type='station', name='station', default='IA0200',
             label='Select Station:'),
        dict(type='select', options=PDICT, default='best', name='var',
             label='Select Radiation Source'),
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

    station = fdict.get('station', 'IA0200')
    year = int(fdict.get('year', 2014))
    varname = fdict.get('var', 'best')

    table = "alldata_%s" % (station[:2],)
    nt = NetworkTable("%sCLIMATE" % (station[:2],))

    df = read_sql("""
        WITH agg as (
            SELECT sday, max(coalesce(narr_srad, 0))
            from """ + table + """ where
            station = %s  and year > 1978 GROUP by sday),
        obs as (
            SELECT sday, day, narr_srad, merra_srad, hrrr_srad
            from """ + table + """ WHERE
            station = %s and year = %s)
        SELECT a.sday, a.max as max_narr, o.day, o.narr_srad, o.merra_srad,
        o.hrrr_srad from agg a LEFT JOIN obs o on (a.sday = o.sday)
        ORDER by a.sday ASC
    """, pgconn, params=(station, station, year), index_col='sday')
    df['max_narr_smooth'] = df['max_narr'].rolling(window=7, min_periods=1,
                                                   center=True).mean()
    df['best'] = df['narr_srad'].fillna(
                                    df['merra_srad']).fillna(df['hrrr_srad'])

    ax = plt.axes([0.1, 0.1, 0.6, 0.8])

    ax.fill_between(range(1, 367), 0, df['max_narr_smooth'], color='tan',
                    label="Max")
    if not np.isnan(df[varname].max()):
        ax.bar(range(len(df.index)), df[varname], fc='g',
               ec='g', label="%s" % (year,))
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 365))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlim(0, 366)
    lyear = datetime.date.today().year - 1
    ax.set_title(("[%s] %s Daily Solar Radiation\n"
                  "1979-%s NARR Climatology w/ %s "
                  ) % (station, nt.sts[station]['name'], lyear, year))
    ax.legend()
    ax.grid(True)
    ax.set_ylabel("Shortwave Solar Radiation $MJ$ $d^{-1}$")

    # Do the x,y scatter plots
    for i, combo in enumerate([('narr_srad', 'merra_srad'),
                               ('narr_srad', 'hrrr_srad'),
                               ('hrrr_srad', 'merra_srad')]):
        ax3 = plt.axes([0.78, 0.1 + (0.3 * i), 0.2, 0.2])

        xmax = df[combo[0]].max()
        xlabel = combo[0].replace("_srad", "").upper()
        ylabel = combo[1].replace("_srad", "").upper()
        ymax = df[combo[1]].max()
        if np.isnan(xmax) or np.isnan(ymax):
            ax3.text(0.5, 0.5, "%s or %s\nis missing" % (xlabel, ylabel),
                     ha='center', va='center')
            ax3.get_xaxis().set_visible(False)
            ax3.get_yaxis().set_visible(False)
            continue
        c = df[[combo[0], combo[1]]].corr()
        ax3.text(0.5, 1.01,
                 "Pearson Corr: %.2f" % (c.iat[1, 0],), fontsize=10,
                 ha='center', transform=ax3.transAxes)
        ax3.scatter(df[combo[0]], df[combo[1]], edgecolor='None',
                    facecolor='green')
        maxv = max([ax3.get_ylim()[1], ax3.get_xlim()[1]])
        ax3.set_ylim(0, maxv)
        ax3.set_xlim(0, maxv)
        ax3.plot([0, maxv], [0, maxv], color='k')
        ax3.set_xlabel("%s $\mu$=%.1f" % (xlabel, df[combo[0]].mean()),
                       labelpad=0, fontsize=12)
        ax3.set_ylabel("%s $\mu$=%.1f" % (ylabel, df[combo[1]].mean()),
                       fontsize=12)

    return plt.gcf(), df

if __name__ == '__main__':
    plotter(dict(year=2016))
