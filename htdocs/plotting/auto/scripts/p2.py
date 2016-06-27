import psycopg2
from scipy import stats
from pyiem import network
import datetime
import calendar
from pandas.io.sql import read_sql


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
    The circle represents a line of equal extremity as compared with the year
    of your choosing.  The dots greater than 2.5 sigma from center are
    labelled with the year they represent.
    """
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')

    station = fdict.get('station', 'IA0000')
    month = int(fdict.get('month', 7))
    year = int(fdict.get('year', datetime.datetime.now().year))
    table = "alldata_%s" % (station[:2],)
    nt = network.Table("%sCLIMATE" % (station[:2],))

    df = read_sql("""
        SELECT year, sum(precip) as total_precip,
        sum(gdd50(high::numeric,low::numeric)) as gdd50 from """+table+"""
        WHERE station = %s and month = %s GROUP by year
    """, pgconn, params=(station, month), index_col='year')
    if len(df.index) == 0:
        return "ERROR: No Data Found"

    gstats = df.gdd50.describe()
    pstats = df.total_precip.describe()

    df['precip_sigma'] = (df.total_precip - pstats['mean']) / pstats['std']
    df['gdd50_sigma'] = (df.gdd50 - gstats['mean']) / gstats['std']
    df['distance'] = (df.precip_sigma ** 2 + df.gdd50_sigma ** 2) ** 0.5

    h_slope, intercept, r_value, _, _ = stats.linregress(df['gdd50_sigma'],
                                                         df['precip_sigma'])

    y1 = -4.0 * h_slope + intercept
    y2 = 4.0 * h_slope + intercept
    ax = plt.axes([0.1, 0.12, 0.8, 0.78])

    ax.scatter(df['gdd50_sigma'], df['precip_sigma'], label=None)
    ax.plot([-4, 4], [y1, y2], label="Slope=%.2f\nR$^2$=%.2f" % (h_slope,
                                                                 r_value ** 2))
    xmax = df.gdd50_sigma.abs().max() + 0.25
    ymax = df.precip_sigma.abs().max() + 0.25
    ax.set_xlim(0 - xmax, xmax)
    ax.set_ylim(0 - ymax, ymax)
    events = df.query("distance > 2.5 or year == %.0f" % (year, ))
    for _year, row in events.iterrows():
        ax.text(row['gdd50_sigma'], row['precip_sigma'],
                ' %.0f' % (_year,), va='center')

    if year in df.index:
        c = Circle((0, 0), radius=df.loc[year].distance, facecolor='none')
        ax.add_patch(c)
    ax.set_xlabel("Growing Degree Day Departure ($\sigma$)")
    ax.set_ylabel("Precipitation Departure ($\sigma$)")
    ax.grid(True)
    ax.set_title(("%s %s [%s]\n"
                  "Growing Degree Day (base=50) + Precipitation Departure"
                  ) % (
        calendar.month_name[month], nt.sts[station]['name'], station))
    ax.legend(loc='upper right', bbox_to_anchor=(0.99, -0.04),
              ncol=2, fontsize=10)

    return plt.gcf(), df
