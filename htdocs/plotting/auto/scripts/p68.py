"""VTEC combos"""
from pandas.io.sql import read_sql
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['cache'] = 86400
    desc['description'] = """This chart shows the number of VTEC phenomena and
    significance combinations issued by a NWS Forecast Office for a given year.
    Please note that not all current-day VTEC products were started in 2005,
    some came a few years later.  So numbers in 2005 are not directly
    comparable to 2015.  Here is a
<a href="http://www.nws.noaa.gov/os/vtec/pdfs/VTEC_explanation6.pdf">handy
 chart</a> with more details on VTEC and codes used in this graphic.
    """
    desc['arguments'] = [
        dict(type='networkselect', name='station', network='WFO',
             default='DMX', label='Select WFO:', all=True)
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn('postgis')
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station'][:4]
    ctx['_nt'].sts['_ALL'] = {'name': 'All Offices'}

    fig = plt.figure(figsize=(8,
                              14 if station != '_ALL' else 21))
    ax = [None, None]
    ax[0] = plt.axes([0.1, 0.75, 0.85, 0.2])
    ax[1] = plt.axes([0.1, 0.05, 0.85, 0.65])

    if station == '_ALL':
        df = read_sql("""
            SELECT distinct extract(year from issue) as year,
                phenomena, significance from warnings WHERE
                phenomena is not null and significance is not null and
                issue > '2005-01-01'
            """, pgconn, index_col=None)
    else:
        df = read_sql("""
            SELECT distinct extract(year from issue) as year,
            phenomena, significance from warnings WHERE
            wfo = %s and phenomena is not null and significance is not null
            and issue > '2005-01-01'
            """, pgconn, params=(station, ), index_col=None)

    df['wfo'] = station
    df['year'] = df['year'].astype('i')
    gdf = df.groupby('year').count()

    ax[0].bar(gdf.index.values, gdf['wfo'], width=0.8, fc='b', ec='b',
              align='center')
    for yr, row in gdf.iterrows():
        ax[0].text(yr, row['wfo'] + 1, "%s" % (row['wfo'],), ha='center')
    ax[0].set_title(("[%s] NWS %s\nCount of Distinct VTEC Phenomena/"
                     "Significance - %i to %i"
                     ) % (station, ctx['_nt'].sts[station]['name'],
                          df['year'].min(), df['year'].max()))
    ax[0].grid()
    ax[0].set_ylabel("Count")
    ax[0].set_xlim(gdf.index.values.min() - 0.5,
                   gdf.index.values.max() + 0.5)

    pos = {}
    i = 1
    df.sort_values(['phenomena', 'significance'], inplace=True)
    for _, row in df.iterrows():
        key = "%s.%s" % (row['phenomena'], row['significance'])
        if key not in pos:
            pos[key] = i
            i += 1
        ax[1].text(row['year'], pos[key], key, ha='center',
                   va='center', fontsize=10,
                   bbox=dict(color='white'))

    ax[1].set_title("VTEC <Phenomena.Significance> Issued by Year")
    ax[1].set_ylim(0, i)
    ax[1].grid(True)
    ax[1].set_xlim(gdf.index.values.min() - 0.5,
                   gdf.index.values.max() + 0.5)
    return fig, df


if __name__ == '__main__':
    plotter(dict())
