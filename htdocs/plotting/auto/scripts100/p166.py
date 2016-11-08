from pyiem import util
from pandas.io.sql import read_sql
import psycopg2
import datetime
from pyiem.reference import state_names

MDICT = {'ytd': 'Limit Plot to Year to Date',
         'year': 'Plot Entire Year of Data'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This plot presents a summary of the number of year
    to date watches issued by the Storm Prediction Center and the percentage
    of those watches that at least touched the given state.
    """
    d['arguments'] = [
        dict(type='state', name='state', default='IA',
             label='Select State:'),
        dict(type='select', name='limit', default='ytd', options=MDICT,
             label='Time Limit of Plot'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(dbname='postgis', host='iemdb', user='nobody')
    ctx = util.get_autoplot_context(fdict, get_description())
    state = ctx['state'][:2].upper()
    limit = ctx['limit']

    sqllimit = ''
    ets = '31 December'
    if limit == 'ytd':
        ets = datetime.date.today().strftime("%-d %B")
        sqllimit = 'extract(doy from issued) <= extract(doy from now()) and '

    # Get total issued
    df = read_sql("""
        Select extract(year from issued) as year,
        count(*) as national_count from watches
        where """ + sqllimit + """
        num < 3000 GROUP by year ORDER by year ASC
    """, pgconn, index_col='year')

    # Get total issued
    odf = read_sql("""
        select extract(year from issued) as year, count(*) as state_count
        from watches w, states s where w.geom && s.the_geom and
        ST_Overlaps(w.geom, s.the_geom) and
        """ + sqllimit + """
        s.state_abbr = %s
        GROUP by year ORDER by year ASC
    """, pgconn, params=(state,), index_col='year')
    df['state_count'] = odf['state_count']
    df['state_percent'] = df['state_count'] / df['national_count'] * 100.

    (fig, ax) = plt.subplots(3, 1, sharex=True)

    ax[0].bar(df.index.values, df['national_count'].values, align='center')
    for year, row in df.iterrows():
        ax[0].text(year, row['national_count'],
                   "%.0f" % (row['national_count'],), ha='center',
                   rotation=90, va='top', color='white')
    ax[0].grid(True)
    ax[0].set_title(("Storm Prediction Center Issued Tornado / "
                     "Svr T'Storm Watches\n"
                     "1 January to %s, Watch Outlines touching %s"
                     ) % (ets,
                          state_names[state]))
    ax[0].set_ylabel("National Count")

    ax[1].bar(df.index.values, df['state_count'].values, align='center')
    for year, row in df.iterrows():
        ax[1].text(year, row['state_count'],
                   "%.0f" % (row['state_count'],), ha='center',
                   rotation=90, va='top', color='white')
    ax[1].grid(True)
    ax[1].set_ylabel("State Count")

    ax[2].bar(df.index.values, df['state_percent'].values, align='center')
    for year, row in df.iterrows():
        ax[2].text(year, row['state_percent'],
                   "%.1f%%" % (row['state_percent'],), ha='center',
                   rotation=90, va='top', color='white')
    ax[2].grid(True)
    ax[2].set_ylabel("% Touching State")

    ax[0].set_xlim(df.index.values[0] - 0.5,
                   df.index.values[-1] + 0.5)

    return fig, df
