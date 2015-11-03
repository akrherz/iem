import psycopg2.extras
import calendar
import matplotlib.cm as cm
import datetime
from pandas.io.sql import read_sql


PDICT = {'precip': 'Total Precipitation',
         'avgt': 'Average Temperature'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['cache'] = 86400
    d['description'] = """This map presents IEM computed precipitation
    ranks for a month and year of your choice.  The map unit is climate
    districts for which the IEM generates spatially weighted daily averages
    for."""
    today = datetime.date.today() - datetime.timedelta(days=28)
    d['arguments'] = [
        dict(type='select', name='var', default='precip',
             label='Select Variable', options=PDICT),
        dict(type='year', name='year', default=today.year,
             label='Select Year:',
             min=1893),  # Comes back to python as yyyy-mm-dd
        dict(type='month', name='month', default=today.month,
             label='Select Month:'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    from pyiem.plot import MapPlot
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')

    year = int(fdict.get('year', 2014))
    month = int(fdict.get('month', 9))
    varname = fdict.get('var', 'precip')

    lastyear = datetime.date.today().year
    years = lastyear - 1893 + 1

    df = read_sql("""
    with monthly as (
        SELECT year, station,
        sum(precip) as p,
        avg((high+low)/2.) as avgt
        from alldata
        WHERE substr(station,3,1) = 'C' and month = %s
        GROUP by year, station),
    ranks as (
        SELECT station, year,
        rank() OVER (PARTITION by station ORDER by p DESC) as precip_rank,
        rank() OVER (PARTITION by station ORDER by avgt DESC) as avgt_rank
        from monthly)

    SELECT station, precip_rank, avgt_rank from ranks
    where year = %s """, pgconn, params=(month, year), index_col='station')

    m = MapPlot(sector='midwest', axisbg='white',
                title='%s %s %s Ranks by Climate District' % (
                        year, calendar.month_name[month], PDICT[varname]),
                subtitle=('Based on IEM Estimates, '
                          '1 is %s out of %s total years (1893-%s)'
                          ) % ('wettest' if varname == 'precip' else 'hottest',
                               years, lastyear)
                )
    cmap = cm.get_cmap("BrBG_r" if varname == 'precip' else 'BrBG')
    cmap.set_under('white')
    cmap.set_over('black')
    m.fill_climdiv(df[varname+'_rank'], ilabel=True, plotmissing=False,
                   bins=[1, 5, 10, 25, 50, 75, 100, years-10, years-5, years],
                   cmap=cmap)

    return m.fig, df
