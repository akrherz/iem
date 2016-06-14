import psycopg2
import calendar
import matplotlib.cm as cm
import datetime
import numpy as np
from pandas.io.sql import read_sql
from collections import OrderedDict

PDICT = {'precip': 'Total Precipitation',
         'arridity': 'Arridity Index',
         'avgt': 'Average Temperature'}

MDICT = OrderedDict([
         ('spring', 'Spring (MAM)'),
         ('fall', 'Fall (SON)'),
         ('winter', 'Winter (DJF)'),
         ('summer', 'Summer (JJA)'),
         ('1', 'January'),
         ('2', 'February'),
         ('3', 'March'),
         ('4', 'April'),
         ('5', 'May'),
         ('6', 'June'),
         ('7', 'July'),
         ('8', 'August'),
         ('9', 'September'),
         ('10', 'October'),
         ('11', 'November'),
         ('12', 'December')])


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['cache'] = 86400
    d['description'] = """This map presents IEM computed precipitation
    ranks for a month and year of your choice.  The map unit is climate
    districts for which the IEM generates spatially weighted daily averages
    for.  For seasonal totals, the year presented is the calendar year of
    the last month in the three month period."""
    today = datetime.date.today() - datetime.timedelta(days=28)
    d['arguments'] = [
        dict(type='select', name='var', default='precip',
             label='Select Variable', options=PDICT),
        dict(type='year', name='year', default=today.year,
             label='Select Year:',
             min=1893),
        dict(type='select', name='month', default=today.month,
             label='Month Limiter', options=MDICT),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    from pyiem.plot import MapPlot
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')

    year = int(fdict.get('year', 2014))
    month = fdict.get('month', 9)
    varname = fdict.get('var', 'precip')
    l = "0 days"
    if month == 'fall':
        months = [9, 10, 11]
        label = "Fall (SON)"
    elif month == 'winter':
        months = [12, 1, 2]
        l = "32 days"
        label = "Winter (DJF)"
    elif month == 'spring':
        months = [3, 4, 5]
        label = "Spring (MAM)"
    elif month == 'summer':
        months = [6, 7, 8]
        label = "Summer (JJA)"
    else:
        months = [int(month), ]
        label = calendar.month_name[int(month)]

    lastyear = datetime.date.today().year
    years = lastyear - 1893 + 1

    df = read_sql("""
    with monthly as (
        SELECT extract(year from day + '"""+l+"""'::interval) as myyear,
        station, sum(precip) as p,
        avg((high+low)/2.) as avgt,
        avg(high) as avghi
        from alldata
        WHERE substr(station,3,1) = 'C' and month in %s
        GROUP by myyear, station),
    ranks as (
        SELECT station, myyear as year,
        avg(p) OVER (PARTITION by station) as avg_precip,
        stddev(p) OVER (PARTITION by station) as std_precip,
        p as precip,
        avg(avghi) OVER (PARTITION by station) as avg_high,
        stddev(avghi) OVER (PARTITION by station) as std_high,
        avghi as high,
        rank() OVER (PARTITION by station ORDER by p DESC) as precip_rank,
        rank() OVER (PARTITION by station ORDER by avgt DESC) as avgt_rank
        from monthly)

    SELECT station, precip_rank, avgt_rank,
    ((high - avg_high) / std_high) - ((precip - avg_precip) / std_precip)
    as arridity from ranks
    where year = %s """, pgconn, params=(tuple(months), year),
                  index_col='station')

    subtitle = ('Based on IEM Estimates, '
                '1 is %s out of %s total years (1893-%s)'
                ) % ('wettest' if varname == 'precip' else 'hottest',
                     years, lastyear)
    if varname == 'arridity':
        subtitle = "Std Average High Temp Departure minus Std Precip Departure"
    m = MapPlot(sector='midwest', axisbg='white',
                title='%s %s %s %sby Climate District' % (
                        year, label, PDICT[varname],
                        'Ranks ' if varname != 'arridity' else ''),
                subtitle=subtitle)
    cmap = cm.get_cmap("BrBG_r" if varname in ['precip', 'arridity']
                       else 'BrBG')
    cmap.set_under('white')
    cmap.set_over('black')
    bins = [1, 5, 10, 25, 50, 75, 100, years-10, years-5, years]
    pvar = varname+'_rank'
    fmt = '%.0f'
    if varname == 'arridity':
        bins = np.arange(-4, 4.1, 1)
        pvar = varname
        fmt = '%.1f'
    m.fill_climdiv(df[pvar], ilabel=True, plotmissing=False, lblformat=fmt,
                   bins=bins,
                   cmap=cmap)

    return m.fig, df
