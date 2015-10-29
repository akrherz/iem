import psycopg2
from pyiem.network import Table as NetworkTable
from pandas.io.sql import read_sql


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['cache'] = 86400
    d['description'] = """This chart shows the number of VTEC phenomena and
    significance combinations issued by a NWS Forecast Office for a given year.
    Please note that not all current-day VTEC products were started in 2005,
    some came a few years later.  So numbers in 2005 are not directly
    comparable to 2015.
    """
    d['arguments'] = [
        dict(type='networkselect', name='station', network='WFO',
             default='DMX', label='Select WFO:', all=True)
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')

    station = fdict.get('station', 'DMX')[:4]

    nt = NetworkTable('WFO')
    nt.sts['_ALL'] = {'name': 'All Offices'}

    (fig, ax) = plt.subplots(1, 1, sharex=True)

    if station == '_ALL':
        df = read_sql("""
            with obs as (
                SELECT distinct extract(year from issue) as yr,
                phenomena, significance from warnings WHERE
                phenomena is not null and significance is not null and
                issue > '2005-01-01' and issue is not null
            )
            SELECT yr as year, count(*) from obs GROUP by yr ORDER by yr ASC
            """, pgconn, index_col=None)
    else:
        df = read_sql("""
            with obs as (
                SELECT distinct extract(year from issue) as yr,
                phenomena, significance from warnings WHERE
                wfo = %s and phenomena is not null and significance is not null
                and issue > '2005-01-01' and issue is not null
            )
            SELECT yr as year, count(*) from obs GROUP by yr ORDER by yr ASC
            """, pgconn, params=(station, ), index_col=None)

    df['wfo'] = station
    df['year'] = df['year'].astype('i')

    ax.bar(df['year']-0.4, df['count'], width=0.8, fc='b', ec='b')
    for yr, val in zip(df['year'], df['count']):
        ax.text(yr, val+1, "%s" % (val,), ha='center')
    ax.set_title(("[%s] NWS %s\nCount of Distinct VTEC Phenomena/"
                  "Significance - %i to %i"
                  ) % (station, nt.sts[station]['name'],
                       df['year'].min(), df['year'].max()))
    ax.grid()
    ax.set_ylabel("Count")

    return fig, df
